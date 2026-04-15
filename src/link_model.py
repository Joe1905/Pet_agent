
import re
from PySide6.QtCore import QObject, Signal, QTimer
from string_manager import StringManager
import requests
from typing import Iterable, Optional, List
from window_tool import WindowTool
from file_load import ResourceExtractor
import sys
from pathlib import Path
import chardet
from dataclasses import dataclass
import datetime
import time
import base64

class ChatAgent(QObject):
    # message_window = None
    _instance = None
    is_start = False
    run_type = 1
    text_stream = Signal(str)
    final_answer = Signal(str)
    show_overlay = Signal()
    trigger_task = Signal()
    update_memory = Signal(str)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = ChatAgent()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.string_manager = StringManager()
        self.windows_tool = WindowTool()
        self.model = LocalLLM()
        self.SYSTEM_PROMPT = ""
        self.update_system_prompt()
        self.sys_prompt = ""
        self.question_text = ""
        self.chain_text = ""
        self.tool_text = ""
        self.stop_keywords = []
        self.trigger_task.connect(self.run_task)

        self.overlay_timer = QTimer(self)
        self.overlay_timer.setSingleShot(True)  # 单次触发
        self.overlay_timer.timeout.connect(self.on_overlay_timeout)

    def run_task(self):
        if self.run_type == 1:
            self.update_response()
        elif self.run_type == 2:
            self.on_update_memory()

    def update_response(self, is_tool_back = False):
        if self.question_text == "" and not self.is_start:
            return
        if is_tool_back:
            print("工具回调")
            self.question_text += (self.chain_text + self.tool_text)
        elif self.is_start:
            print("初始化招呼请求")
            self.question_text = "现在请结合目前天气和时间给主人打个招呼！"
        else:
            print("问题输入", self.question_text)
        
        # 恢复后端调用
        answer = self.model.ask_stream(self.question_text, self.sys_prompt)
        
        all_response = ""

        # self.overlay_timer.start(30000)
        for token in answer:
            all_response += token
            self.text_stream.emit(token)
                # self.message_window.text_stream.emit(token)
        print("all_response", all_response)

        if ChatAgent.get_response_have_tag(all_response, "tool") and not ChatAgent.get_response_have_tag(all_response, "observation"):
            self.on_response_back(all_response)
        elif ChatAgent.get_response_have_tag(all_response, "final answer"):
             self.on_response_back(all_response)

    def to_get_response(self, question:str, history_messages):
        input_text = f"{self.SYSTEM_PROMPT}\n"

        model_memory = ResourceExtractor.get_setting_config()["Memory"]["current_memory"]
        if model_memory is not None:
            # print("model_memory", model_memory)
            input_text += f"#历史记忆#\n{model_memory}\n"
        input_text += f"#本次会话记录#\n{self.to_get_history(history_messages)}\n"
        time = datetime.datetime.now().strftime(self.string_manager.get("messageUi.time_table"))
        # input_text += f"#本次会话时间#\n{time}\n"
        self.question_text = self.add_extract_tag_content(question, "question")
        self.sys_prompt = input_text
        # self.update_response()

    def to_get_history(self, history_messages) -> str:
        history_message = self.string_manager.get("link_model.error_3")
        is_not_history = True
        self.stop_keywords = self.string_manager.get("link_model.stop_words")
        if history_messages is None:
            return history_message
        index = 0
        for message in history_messages:
            index += 1
            if index == history_messages.__len__():
                break
            if is_not_history:
                history_message = ""
                is_not_history = False
            if message[2] == 2:
                history_message += self.add_extract_tag_content(message[0],"answer")
            elif message[2] == 1:
                history_message += self.add_extract_tag_content(message[0],"question")
        return history_message

    def on_error_back(self, error_msg):
        # if self.message_window is not None:
        #     self.message_window.rebot_reply_message(error_msg)
        pass

    def init_send_message(self):
        if not self.is_start:
                return
        self.question_text = ""
        self.sys_prompt = f"{self.SYSTEM_PROMPT}\n"
        self.run_type = 1
        # self.start()

    @staticmethod
    def get_response_have_tag(response:str, tag:str) -> bool:
        return  f"<{tag}>" in response and f"</{tag}>" in response

    def on_response_back(self, response:str):

        true_response = response
        if ChatAgent.get_response_have_tag(response, "think"):
            true_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)

        if ChatAgent.get_response_have_tag(true_response, "final answer"):

            self.overlay_timer.stop()
            # 发送到消息窗口
            # if self.message_window is not None:
            #     self.message_window.final_answer(self.extract_tag_content(response, "final answer"))
            self.chain_text = ""
            self.tool_text = ""
            self.final_answer.emit(self.extract_tag_content(response, "final answer"))
            if self.is_start:
                self.show_overlay.emit()  # 10000毫秒 = 10秒
                self.is_start = False
                # self.message_window.toggle_overlay()
            return
        if ChatAgent.get_response_have_tag(true_response, "tool"):
            def parse_tool_content(text):
                self.overlay_timer.stop()
                tool_content = self.extract_tag_content(text, "tool")
                if tool_content == "":
                    return None, None
                func_pattern = re.compile(r'^(\w+)(?:\s*\((.*)\))?$')
                func_match = func_pattern.match(tool_content.strip())

                if not func_match:
                    return None, None

                func_name = func_match.group(1)
                arg_str = func_match.group(2)  # 可能是 None

                if arg_str is None or arg_str.strip() == "":
                    args = None  # 没有参数
                else:
                    # 这里可以根据需要拆分多个参数，比如用逗号分隔
                    args = [a.strip() for a in arg_str.split(",")]

                return func_name, args
            func_name,args = parse_tool_content(response)
            method = getattr(self.windows_tool, func_name, None)
            if callable(method):
                if args is None:
                    observation = method()
                else:
                    if not isinstance(args, (list, tuple)):
                        args = [args]
                    observation =  method(*args)
                self.chain_text = self.add_extract_tag_content(self.extract_tag_content(response,"think"), "think")
                self.tool_text = self.add_extract_tag_content(self.extract_tag_content(response, "tool"),"tool") + self.add_extract_tag_content("工具调用完成：" + str(observation),"observation")
                print("chain_text",self.chain_text)
                print("tool_text",self.tool_text)
                self.update_response(True)
            # else:
            #     print(f"方法 {func_name} 不存在或不可调用")

    def extract_tag_content(self, text: str, tag: str) -> str:
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"

        # 步骤1：找到最后一个闭合标签 `</final answer>` 的位置
        end_pos = text.rfind(end_tag)
        if end_pos == -1:  # 没有闭合标签，直接返回空
            return ""

        # 步骤2：从闭合标签位置向前，找到最近的开始标签 `<final answer>`
        start_pos = text.rfind(start_tag, 0, end_pos)
        if start_pos == -1:  # 开始标签不存在，返回空
            return ""

        # 步骤3：提取两个标签之间的内容并清理空白
        content_start = start_pos + len(start_tag)
        return text[content_start:end_pos].strip()

    def add_extract_tag_content(self, text: str, tag: str) -> str:
        return f"<{tag}>{text}</{tag}>"

    def update_system_prompt(self):
        self.set_config = ResourceExtractor.get_setting_config()
        index = self.set_config["General_Set"]["current_index"]

        nickname = self.set_config["Nick_Name"][f"nickname{index}"]
        profile_prompts:list = self.string_manager.get(f"Character_{index}").copy()
        profile_prompts[0] = profile_prompts[0].replace("{nickname}", nickname)
        if "{nickname}" in profile_prompts[2]:
            profile_prompts[2] = profile_prompts[2].replace("{nickname}", nickname)

        sys_prompts:list = self.string_manager.get("Extra_Rule") + profile_prompts
        self.SYSTEM_PROMPT = self.get_system_prompt(sys_prompts)

    def get_system_prompt(self, str_array: list):
        result = [str_array[0]]
        for i in range(1, len(str_array)):
            formatted_item = f"\n{str_array[i]}"
            result.append(formatted_item)
        return "".join(result)

    def on_update_memory(self):
        memory_str = ResourceExtractor.get_setting_config()["Memory"]["current_memory"]
        if memory_str is not None:
            memory_str += "\n"
        memory_str = self.update_history_memory()
        self.update_memory.emit(memory_str)

    def update_history_memory(self) -> str:
            his_prompt = self.string_manager.get("Summary_Prompt")[0:4]
            his_prompt = self.get_system_prompt(his_prompt)
            cur_memory = ResourceExtractor.get_setting_config()["Memory"]["current_memory"]
            def read_logs_from_file(start_filename):
                def get_logs_path():
                    # 获取当前运行目录（源码运行时是 .py 文件所在目录，打包后是 exe 所在目录）
                    if getattr(sys, 'frozen', False):  # 打包后的 exe
                        base_path = Path(sys.argv[0]).parent
                    else:  # 源码运行
                        base_path = Path(__file__).parent
                    return base_path / "logs"

                folder_path = get_logs_path()
                folder = Path(folder_path)
                # 获取所有 txt 文件并按文件名排序
                files = sorted([f for f in folder.glob("*.txt")])
                if files.__len__() == 0:
                    return 0,0
                # 找到起始文件的索引
                start_index = 0
                if start_filename is not "":
                    for i, f in enumerate(files):
                        if int(f.name.split(".")[0]) > int(start_filename):
                            start_index = i
                            break
                        # else:
                        #     print("排除文件", f.name)

                all_text = []
                index = 1
                last_filename = None  # 用于保存最后一个文件名
                for f in files[start_index:]:
                    text = f"#记录 {index} 开始#\n"
                    # 自动检测编码
                    with open(f, "rb") as fb:
                        raw_data = fb.read()
                        encoding = chardet.detect(raw_data)["encoding"] or "utf-8"
                    # 按检测到的编码解码
                    text += raw_data.decode(encoding, errors="ignore")
                    text += f"#记录 {index} 结束#"
                    all_text.append(text)
                    index += 1
                    last_filename = f.name.split(".")[0]

                return "\n".join(all_text), last_filename

            # 使用示例
            config = ResourceExtractor.get_setting_config()
            start_file = config["Memory"]["current_file"] # 从这个文件开始
            result_str, last_file = read_logs_from_file(start_file)
            if  start_file == last_file:
                print("无更新的记录可总结")
                return "-1"
            ResourceExtractor.set_setting_config(
                {
                    "Memory":
                        {
                            "current_memory": config["Memory"]["current_memory"],
                            "current_file":last_file
                        }
                }, None)

            input_text = f"#历史提取内容#\n{cur_memory}\n#真实输入#\n{result_str}\n#真实输入结束#\n现在帮我生成上面聊天记录的摘要:"
            # 编码输入
            print("input_text", input_text)
            data = dict()
            data["max_tokens"] = 1024
            data["temperature"] = 0
            data["top_p"] = 0.95
            data["top_k"] = 20

            full_response = self.model.ask(input_text, his_prompt, data)

            print(f"full_response", full_response)
            # 提取模型回复部分
            # if self.stop_keywords[1] in full_response:
            #     response = full_response.split(self.stop_keywords[1])[-1].strip()
            # else:
            response = full_response
            if "</think>" in response:
                response = response.split("</think>")[-1].strip()
                if "\n" in response:
                    response = response.lstrip('\n')

            return response

    def on_overlay_timeout(self):
        """10秒未收到final answer时的超时处理"""
        print("⚠️ 10秒未收到final answer，清除记录并重新请求")
        self.update_response()

@dataclass
class SamplingConfig:
    temperature: float = 0.6
    top_p: float = 0.75
    top_k: int = 50
    repeat_penalty: float = 1.2
    max_tokens: int = 1024
    stop: Optional[List[str]] = None

class LocalLLM():

        def __init__(self, samp = None):
            self.samp = SamplingConfig() if samp is None else samp


        def ask(self, question: str, system_prompt: str = "你是一位智能助手", set_data:dict = None) -> str:
            """一次性回答"""
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ]

            # 服务端地址
            set_config = ResourceExtractor.get_setting_config()
            url = set_config["Url"]["server_url"] + "/chat"#"/v1/completions" # "http://localhost:8000/v1/completions"

            # 请求体：指定提示词、生成长度等
            # print("prompt", f"system:\n{system_prompt}\nuser:\n{question}")
            # if set_data is not None:
            #     data = {
            #         "messages": messages,
            #         "max_tokens": set_data["max_tokens"],  # 生成文本的最大token数
            #         "temperature": set_data["temperature"],  # 随机性参数，0-1之间，越高越随机
            #         "top_p": set_data["top_p"],
            #         "top_k": set_data["top_k"],
            #         "stream": False,
            #     }
            # else:
            #     data = {
            #         "messages": messages,
            #         "max_tokens": self.samp.max_tokens,  # 生成文本的最大token数
            #         "temperature": self.samp.temperature,  # 随机性参数，0-1之间，越高越随机
            #         "top_p": self.samp.top_p,
            #         "top_k": self.samp.top_k,
            #         "stream": False,
            #     }
            # 发送POST请求
            payload = {
                "question": question,
                "character": "-1",
                "memory": "",
                "stream": False
            }

            response = requests.post(url, json=payload, timeout=120)

            if response.status_code == 200:
                response = requests.post(url, json=payload, timeout=120)

                # 2. 【关键】先打印响应头和原始内容，不要直接 json()
                print(f"DEBUG: 状态码: {response.status_code}")
                print(f"DEBUG: Content-Type: {response.headers.get('Content-Type')}")
                print(f"DEBUG: 原始内容: {response.text[:200]}")  # 只打印前200字符防止刷屏

                if response.status_code == 200:
                    # 只有当类型是 json 时才解析
                    if "application/json" in response.headers.get("Content-Type", ""):
                        result = response.json()
                        return result.get("response", "")
                    else:
                        # 如果返回了 text/plain，说明服务端依然在流式输出，配置没生效
                        print("❌ 错误：服务端返回了流式文本，而不是 JSON。请检查服务端代码是否重启。")
                        return response.text
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    return ""
            else:
                print(f"请求失败，状态码：{response.status_code}")
                print(f"错误信息：{response.text}")
                return ""


        def ask_stream(self, question: str, system_prompt: str = "You are a helpful assistant.") -> Iterable[str]:
            """流式回答"""
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ]
            # 服务端地址（端口与启动vLLM时一致，这里假设是8000）
            set_config = ResourceExtractor.get_setting_config()
            url = set_config["Url"]["server_url"]  + "/chat"#  "/v1/chat/completions" #"http://localhost:8000/v1/chat/completions"  # 服务器 IP

            # 请求体：指定提示词、生成长度等
            # print("prompt", f"system:\n{system_prompt}\nuser:\n{question}")
            data = {
                "messages": messages,
                "max_tokens": self.samp.max_tokens,  # 生成文本的最大token数
                "temperature": self.samp.temperature,  # 随机性参数，0-1之间，越高越随机
                "top_p": self.samp.top_p,
                "top_k": self.samp.top_k,
                "stop":["<observation>"],
                "stream": True,
                "stream_format": "json"  # 指定流式响应格式
            }

            index = set_config["General_Set"]["current_index"]
            character_key = f"New_Character_{index}"
            model_memory = set_config["Memory"]["current_memory"]
            if model_memory is not None:
                # print("model_memory", model_memory)
                model_memory = f"#历史记忆#\n{model_memory}\n"
            
            # 检查 question 是否包含图片
            image_data = None
            if "<question>image:" in question:
                # 提取图片路径
                # 假设格式为 <question>image:path/to/image.png</question>
                match = re.search(r'<question>image:(.*?)</question>', question)
                if match:
                    image_path = match.group(1)
                    try:
                        with open(image_path, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                            image_data = f"data:image/jpeg;base64,{encoded_string}"
                            # 将 question 替换为纯文本提示，或者保留作为描述
                            question = "请分析这张图片。" # 或者保留原问题
                    except Exception as e:
                        print(f"读取图片失败: {e}")

            def get_my_ip():
                """获取用户当前公网 IP"""
                try:
                    # 使用 ipify 获取纯文本 IP
                    return requests.get("https://api.ipify.org", timeout=5).text
                except:
                    return ""

            user_public_ip = get_my_ip()
            session_id = set_config["SessionID"]["id"]
            payload = {
                "question": question,
                "session_id": session_id,
                "user_ip": user_public_ip, # 👈 将真实 IP 发送给服务器
                "character": character_key,
                "memory": model_memory,
                "image": image_data # 添加图片数据字段
            }

            try:
                with requests.post(url, json=payload, stream=True) as response:
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                            if chunk:
                                yield chunk
                    else:
                        print(f"错误: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"请求失败: {e}")
                return None

        @classmethod
        def request_clear_history(self):
            set_config = ResourceExtractor.get_setting_config()
            index = set_config["General_Set"]["current_index"]
            session_id = set_config["SessionID"]["id"]
            character_key = f"New_Character_{index}"
            url = set_config["Url"]["server_url"] + "/clear_history"
            payload = {
                "session_id": session_id,  # 确保和你聊天时的 ID 一致
                "question": "clear_signal",  # 占位符
                "character": character_key
            }

            try:
                # 使用同步请求即可，因为清理内存极快
                response = requests.post(url, json=payload, timeout=5)
                if response.status_code == 200:
                    print("✅ 后端记忆已重置，现在是一个全新的灵魂了喵！")
                    # 同时也要清空你前端界面上的显示（可选）
                    # self.chat_display.clear()
                else:
                    print(f"❌ 清理失败: {response.status_code}")
            except Exception as e:
                print(f"网络异常: {e}")

if __name__ == "__main__":
    llm = LocalLLM()
    reponse = llm.ask("你好")
    print(reponse)