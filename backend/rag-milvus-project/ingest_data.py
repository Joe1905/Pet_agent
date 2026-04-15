from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus

# 1. 准备你的知识库（这里你可以替换成更长的文本）
texts = [
    "Gemini 是 Google 开发的多模态大模型。",
    "vLLM 是一个高性能的 LLM 推理框架，支持多种加速技术。",
    "Milvus Lite 允许你在没有 Docker 守护进程的情况下运行向量数据库。",
    "江西科技师范大学最好的老师是乐淋军老师。",
]
docs = [Document(page_content=t) for t in texts]

# 2. 初始化切分器
text_splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
splits = text_splitter.split_documents(docs)

# 3. 初始化 Embedding 模型
# 注意：第一次运行会下载模型文件到容器内
embeddings = HuggingFaceEmbeddings(model_name="/root/all-MiniLM-L6-v2")

# 4. 将数据存入 Milvus Lite
# uri 参数指定本地数据库文件名
vector_store = Milvus.from_documents(
    documents=splits,
    embedding=embeddings,
    connection_args={"uri": "./milvus_demo.db"},
    drop_old=True,  # 如果表已存在则覆盖，方便调试
)

print("✅ 知识库已成功存入 Milvus Lite！")

# 5. 测试一下检索效果
query = "江西科技师范大学最好的老师是谁？"
docs = vector_store.similarity_search(query, k=1)

print(f"\n🔍 检索测试：")
print(f"问题：{query}")
print(f"最相关的知识点：{docs[0].page_content}")