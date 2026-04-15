from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, ZeroShotAgent, AgentExecutor, create_react_agent
from langchain.tools import tool, Tool
from langchain.chains import LLMChain
from string_manager import StringManager
from window_tool import WindowTool
from file_load import ResourceExtractor
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.stdout import StdOutCallbackHandler
from PySide6.QtCore import QObject, Signal
from datetime import datetime
from zhdate import ZhDate
import os
import json

class StreamingHandler(BaseCallbackHandler):
    def __init__(self, emit_callback=None):
        self.emit_callback = emit_callback
        self.tokens = []
    def on_llm_new_token(self, token: str, **kwargs):
        # 每收到一个 token 就被调用（用于实时显示）
        # print(token, end="", flush=True)
        self.tokens.append(token)
        try:
            if callable(self.emit_callback):
                self.emit_callback(token)
        except Exception:
            # 忽略回调内部错误以免影响主流式流程
            pass
    def on_llm_end(self, response, **kwargs):
        print("")  # 换行，便于控制台阅读

class AIAgent(QObject):
    _instance = None
    is_start = False
    run_type = 1
    text_stream = Signal(str)
    final_answer = Signal(str)
    show_overlay = Signal()
    trigger_task = Signal()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = AIAgent()
        return cls._instance

    def on_text_stream(self, token:str):
        self.text_stream.emit(token)

    def __init__(self, model: str = "Qwen/Qwen3-30B-A3B-GPTQ-Int4"):
        super().__init__()

        set_config = ResourceExtractor.get_setting_config()
        base_url = set_config["Url"]["server_url"]
        self.trigger_task.connect(self.run_task)
        self.question_text = ""
        # 初始化 LLM
        self.streaming_handler = StreamingHandler(lambda token: self.text_stream.emit(token))
        callback_manager = CallbackManager([self.streaming_handler, StdOutCallbackHandler()])
        self.llm = ChatOpenAI(
            model=model,
            api_key="EMPTY",   # vLLM 默认不校验
            streaming=True,
            callback_manager=callback_manager,
            base_url=base_url,
            temperature=0.7,
        )
        self.string_manager = StringManager()
        sys_prompt = self.update_system_prompt() + "\n" + self.string_manager.get("React_Rule")
        self.custom_prompt = ChatPromptTemplate.from_messages([
            ("system", f"{sys_prompt}"),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
            ])
        # 初始化工具
        self.windows_tools = WindowTool()
        self.tools = []
        self.init_tool()
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent_type=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=memory,
            prompt=self.custom_prompt,
            callback_manager=callback_manager
        )
        # self.agent = initialize_agent(
        #     llm=self.llm,
        #     tools=self.tools,
        #     prompt=self.custom_prompt
        # )


    def update_system_prompt(self) -> str:
        self.set_config = ResourceExtractor.get_setting_config()
        index = self.set_config["General_Set"]["current_index"]

        nickname = self.set_config["Nick_Name"][f"nickname{index}"]
        profile_prompts:list = self.string_manager.get(f"New_Character_{index}").copy()
        if  "{nickname}" in profile_prompts[0]:
            profile_prompts[0] = profile_prompts[0].replace("{nickname}", nickname)
        sys_prompts:list = self.string_manager.get("New_Prompt") + profile_prompts
        return AIAgent.get_system_prompt(sys_prompts)

    @staticmethod
    def get_system_prompt(str_array: list):
        result = [str_array[0]]
        for i in range(1, len(str_array)):
            formatted_item = f"\n{str_array[i]}"
            result.append(formatted_item)
        return "".join(result)

    def to_ask(self, question:str):
        response = self.ask(question)
        if self.is_start:
            self.show_overlay.emit()
            self.is_start = False
        self.final_answer.emit(response)

    def ask(self, question: str) -> str:
        """流式打印生成 token，同时返回最终合并结果字符串"""
        # 清空之前的 token 缓存
        self.streaming_handler.tokens = []
        # invoke/ __call__ 会在生成过程中触发 on_llm_new_token 回调
        result = self.agent.invoke({"input": question})
        # 合并已收到的 tokens（如果需要）
        streamed_text = "".join(self.streaming_handler.tokens)
        # 返回最终的 agent 返回值（可能是 dict），也可返回合并 token
        try:
            # 若 result 是 dict，尝试取常见字段
            if isinstance(result, dict):
                for key in ("output", "result", "final_output", "text"):
                    if key in result:
                        return str(result[key])
            return str(result)
        finally:
            # 可选：把流式文本保存或记录
            pass

    def init_send_message(self):
        if not self.is_start:
                return
        self.run_type = 1

    def run_task(self):
        if self.run_type == 1:
            self.update_response()
        elif self.run_type == 2:
            # self.on_update_memory()
            pass

    def to_get_response(self, question: str, history_messages):
        self.question_text =  question

    def update_response(self):
        if self.question_text == "" and not self.is_start:
            return
        if self.is_start:
            print("初始化招呼请求")
            self.to_ask("现在请给主人打个招呼！")
        else:
            self.to_ask(self.question_text)

    def init_tool(self):
        @tool
        def get_current_address(param: str) -> str:
            """返回当前所在城市"""
            return self.windows_tools.get_current_address()

        @tool
        def get_weather(city: str = None) -> str:
            """返回城市当前天气，
            输入：字符串类型的城市名（如"北京"）"""
            return self.windows_tools.get_weather(city)

        @tool
        def get_all_weather(city: str = None) -> str:
            """返回城市未来天气，
            输入：字符串类型的城市名（如"北京"）"""
            return self.windows_tools.get_weather(city, "all")

        @tool
        def to_set_clock_alarm(time: str) -> str:
            """设置闹钟，输入格式为 'HH:MM'（24小时制，例如 '08:30'）"""
            return self.windows_tools.to_set_clock_alarm(time)

        @tool
        def to_set_clock_stopwatch(param: str) -> str:
            """调取秒表并开始计时"""
            return self.windows_tools.to_set_clock_stopwatch()

        @tool
        def to_set_clock_timer(need_time: str) -> str:
            """输入秒数并启动时钟程序定时器"""
            return self.windows_tools.to_set_clock_timer(need_time)

        @tool
        def open_url(url: str) -> str:
            """浏览器访问网址"""
            return self.windows_tools.open_url([url])

        @tool
        def get_current_time(param: str) -> str:
            """获取时间"""
            return self.windows_tools.get_current_time()

        @tool
        def get_holiday_json(name:str) -> str:
            """获取农历节日的公历日期，输入格式例：元旦/春节/国庆节"""
            return self.windows_tools.get_holiday_json(name)

        self.tools = [get_current_address, get_weather, to_set_clock_alarm, to_set_clock_stopwatch, to_set_clock_timer,
                      open_url, get_current_time, get_holiday_json, get_all_weather]

# 使用示例
if __name__ == "__main__":
    agent = AIAgent()
    result = agent.ask("明天应该穿什么衣服？")
    print("Agent回答：", result)
