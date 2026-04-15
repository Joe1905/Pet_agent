import json
import os
import asyncio
import re
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_milvus import Milvus
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults # 👈 新增

# --- 1. 初始化配置 ---
print("系统启动：正在初始化环境配置...")
os.environ['TRANSFORMERS_OFFLINE'] = '1'
# 🔑 请在这里填入你的 Tavily API Key
os.environ["TAVILY_API_KEY"] = "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"

print(f"正在加载向量模型：{os.path.basename('/root/all-MiniLM-L6-v2')}...")
model_path = "/root/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_path, model_kwargs={'device': 'cpu'})

print("正在连接 Milvus 数据库...")
vector_store = Milvus(
    embedding_function=embeddings,
    connection_args={"uri": "./milvus_demo.db"}
)
retriever = vector_store.as_retriever(search_kwargs={"k": 1})

# 初始化 Tavily
print("正在初始化 Tavily 联网搜索工具...")
search_tool = TavilySearchResults(max_results=3)

print("正在连接 LLM 后端 (Qwen)...")
llm = ChatOpenAI(
    model="Qwen/Qwen3-30B-A3B-GPTQ-Int4",
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:8001/v1",
    max_tokens=2048,
    model_kwargs={
        "stop": ["<|im_end|>", "<|endoftext|>", "<|im_start|>", "User:", "<observation>"]
    },
    streaming=True
)

# --- 2. API 定义 (增加了 session_id 方便追踪历史) ---
class Query(BaseModel):
    session_id: str = "default_user" # 👈 建议加上，用于区分对话
    question: str
    character: str = "New_Character_1"
    memory: str = ""
    stream: bool = True

app = FastAPI()
chat_sessions_store = {} # 简单存储短期历史

# --- 3. 提示词构建 ---
print("正在读取系统 Prompt 配置文件...")
with open("system_prompt.json", "r", encoding="utf-8") as f:
    PROMPT_DATA = json.load(f)

def build_system_prompt(query: Query):
    character_key = query.character
    memory_str = query.memory
    rules_list = PROMPT_DATA.get("Extra_Rule", [])
    rules_str = "".join(rules_list)

    if character_key == "-1":
        return "\n".join(PROMPT_DATA.get("Summary_Prompt", []))
        
    char_list = PROMPT_DATA.get(character_key, [])
    char_str = "".join(char_list)
    
    # 针对 web_search 的硬性优化指令
    search_rule = "\n#注意：调用 web_search 时，只需提取核心关键词，禁止加入时间/地点等冗余词。最终答案包裹在 <final answer> 中。"
    
    return f"{rules_str}\n{memory_str}\n{char_str}{search_rule}"

template = """{system_message}
【参考知识库】: {context}
【历史记录】: {history}
【用户问题】: {question}
"""
prompt_template = ChatPromptTemplate.from_template(template)

# --- 新增：清理历史记录接口 ---
@app.post("/clear_history")
async def clear_history(query: Query):
    session_id = query.session_id
    if session_id in chat_sessions_store:
        chat_sessions_store[session_id] = []
        print(f"🧹 [系统] 会话 {session_id} 的历史记录已清空。")
        return {"status": "success", "message": f"History for {session_id} cleared."}
    return {"status": "not_found", "message": "Session not found."}

# --- 可选：查看当前内存中的历史记录（方便调试） ---
@app.get("/debug_history/{session_id}")
async def get_history(session_id: str):
    return {"history": chat_sessions_store.get(session_id, [])}
    
@app.post("/chat")
async def chat(query: Query):
    # 初始化历史
    print(f"\n[{query.session_id}] 收到新请求: {query.question}")
    if query.session_id not in chat_sessions_store:
        print(f"[{query.session_id}] 初始化新会话缓存...")
        chat_sessions_store[query.session_id] = []
    
    history_str = "\n".join(chat_sessions_store[query.session_id][-6:]) # 取最近3轮
    print(f"[{query.session_id}] 已提取历史记录，长度: {len(history_str)}")

    print(f"[{query.session_id}] 正在构建角色 Prompt: {query.character}")
    dynamic_system_prompt = build_system_prompt(query)
    
    def create_chain(curr_history):
        return (
            {
                "context": retriever, 
                "question": RunnablePassthrough(),
                "system_message": lambda x: dynamic_system_prompt,
                "history": lambda x: curr_history
            }
            | prompt_template | llm | StrOutputParser()
        )

    async def generate():
        full_response = ""
        try:
            # 第一轮生成
            print(f"[{query.session_id}] [Round 1] 开始推理生成...")
            async for chunk in create_chain(history_str).astream(query.question):
                full_response += chunk
                yield chunk
            
            # 🔍 核心：拦截 web_search
            tool_match = re.search(r'<tool>web_search\("(.*?)"\)</tool>', full_response)
            if tool_match:
                search_query = tool_match.group(1).strip()
                print(f"[{query.session_id}] ⚠️ 拦截到工具请求: web_search")
                print(f"[{query.session_id}] 🔍 提取搜索关键词: 【{search_query}】")
                
                yield f"\n\n🔍 [系统执行联网搜索: {search_query}...]\n"
                
                try:
                    # 执行搜索
                    print(f"[{query.session_id}] 🌐 正在请求 Tavily API...")
                    search_res = await asyncio.wait_for(
                        asyncio.to_thread(search_tool.invoke, search_query), timeout=15.0
                    )
                    clean_res = str(search_res).replace("{", "[").replace("}", "]")
                    print(f"[{query.session_id}] ✅ 搜索成功，获取数据片段长度: {len(clean_res)}")
                except Exception as e:
                    clean_res = f"搜索失败: {e}"
                    print(f"[{query.session_id}] ❌ 搜索发生异常: {str(e)}")

                # 第二轮生成：带上 Observation 结果
                obs_context = f"\n<observation>\n{clean_res}\n</observation>\n"
                new_history = history_str + f"\nUser: {query.question}\nAI: {full_response}{obs_context}"
                
                print(f"[{query.session_id}] [Round 2] 正在结合搜索结果生成最终答复...")
                yield f"📄 [搜索完成，正在生成最终答案...]\n\n"
                async for chunk in create_chain(new_history).astream("请根据搜索结果输出 <final answer>。"):
                    full_response += chunk
                    yield chunk
            else:
                print(f"[{query.session_id}] 本轮未检测到工具调用，直接返回结果。")

        except Exception as e:
            print(f"[{query.session_id}] 运行时发生错误: {str(e)}")
            yield f"Error: {str(e)}"
        finally:
            # 记录历史
            if full_response and "Error" not in full_response:
                print(f"[{query.session_id}] 任务完成，正在将对话存入历史记录库。")
                chat_sessions_store[query.session_id].append(f"User: {query.question}")
                chat_sessions_store[query.session_id].append(f"AI: {full_response}")
            else:
                print(f"[{query.session_id}] 对话包含错误或为空，未记录进历史。")

    if query.stream:
        return StreamingResponse(generate(), media_type="text/plain")
    else:
        print(f"[{query.session_id}] 采用非流式模式返回结果...")
        final_ans = ""
        async for chunk in generate(): final_ans += chunk
        return {"response": final_ans, "finished": True}

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 服务已就绪，正在监听端口 8010...")
    uvicorn.run(app, host="0.0.0.0", port=8010)