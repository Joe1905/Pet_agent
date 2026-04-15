import os
import warnings

# --- 核心防坑护城河：防止环境干扰 Milvus 底层引擎 ---
# 1. 屏蔽 pkg_resources 的警告，防止干扰端口解析
warnings.filterwarnings("ignore", category=UserWarning)
# 2. 强制 gRPC 使用原生 DNS
os.environ['GRPC_DNS_RESOLVER'] = 'native'
# 3. 彻底清空所有代理，防止本地通信被拦截
for proxy_env in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(proxy_env, None)
# ---------------------------------------------

from langchain_milvus import Milvus
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. 强制离线，禁止一切联网检查
os.environ['TRANSFORMERS_OFFLINE'] = '1'

# 2. 指定你上传后的绝对路径
model_path = "/root/all-MiniLM-L6-v2"

embeddings = HuggingFaceEmbeddings(
    model_name=model_path,
    model_kwargs={'device': 'cpu'}  # 强制 CPU，节省 GPU 显存给 vLLM
)

# 3. 加载已经存好数据的 Milvus 数据库
vector_store = Milvus(
    embedding_function=embeddings,
    connection_args={"uri": "./milvus_demo.db"}
)
retriever = vector_store.as_retriever(search_kwargs={"k": 1})

# 4. 连接 vLLM
# 重要：model 名字请填你之前 curl 出来的 ID
llm = ChatOpenAI(
    model="Qwen/Qwen3-30B-A3B-GPTQ-Int4", 
    # model="Qwen/Qwen3.5-27B-GPTQ-Int4",
    openai_api_key="EMPTY", 
    openai_api_base="http://localhost:8001/v1"
)

# 5. RAG 链
template = """请根据提供的参考信息回答问题。
参考信息：{context}
问题：{question}
回答："""
prompt = ChatPromptTemplate.from_template(template)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("🚀 正在执行全离线 RAG 问答...")
try:
    print(rag_chain.invoke("vLLM 有哪些核心技术？"))
except Exception as e:
    print(f"❌ 依然报错: {e}")