import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI
import streamlit as st

st.set_page_config(page_title="RAG 助手", page_icon="🤖")
st.title("🤖 RAG 知识库问答助手")
try:
    # 在 Streamlit 线上环境，读取你在网页后台配置的 API_KEY
    API_KEY = st.secrets["API_KEY"]
except Exception:
    # 在本地 PyCharm 环境运行（或者没配置 secrets）时，会走这里
    # 你本地测试可以填个真 Key，但上传前记得删掉或者留空
    API_KEY = ""
# 1. 缓存模型和数据库连接（不包含交互组件）
@st.cache_resource
def load_resources():
    model = SentenceTransformer('shibing624/text2vec-base-chinese')
    db_client = chromadb.PersistentClient(path="./chroma_store")
    ai_client = OpenAI(
        base_url="https://openai.cuc.edu.cn/v1",
        api_key=API_KEY,
    )
    return model, db_client, ai_client


# 2. 加载资源
with st.spinner("正在加载 AI 模型（首次运行较慢）..."):
    model, db_client, ai_client = load_resources()

# 3. 网页端交互：上传文件
uploaded_file = st.file_uploader("请上传你的 TXT 文档", type=["txt"])

if uploaded_file is not None:
    # 读取文件内容
    content = uploaded_file.read().decode("utf-8")
    chunks = [c.strip() for c in content.split("\n") if c.strip()]

    # 向量化并存入数据库（每次上传新文件，都创建一个新集合，防止冲突）
    collection_name = "uploaded_doc"
    # 删掉旧的以防报错
    try:
        db_client.delete_collection(name=collection_name)
    except:
        pass
    collection = db_client.create_collection(name=collection_name)

    with st.spinner("正在处理文档并存入向量数据库..."):
        collection.add(
            documents=chunks,
            embeddings=model.encode(chunks).tolist(),
            ids=[str(i) for i in range(len(chunks))]
        )

    st.success(f"文档处理完成！共切分 {len(chunks)} 个片段。")

    # 4. 提问区
    query = st.text_input("请输入你的问题：")
    if query:
        with st.spinner("正在翻找资料并生成回答..."):
            # 🌟 核心改动：判断问题类型
            # 如果用户问的是“列出所有”、“全面总结”这类需要全盘概览的问题
            # 我们就直接把所有的文档段落拼起来给它，不依赖向量检索
            if "所有" in query or "全面" in query or "总结" in query or "都" in query:
                context = "\n\n".join(chunks)  # 把切好的所有片段全拼起来
                st.info("检测到全局总结类问题，已切换为全量上下文模式。")
            else:
                # 普通问题，走向量检索
                query_vector = model.encode([query]).tolist()
                results = collection.query(query_embeddings=query_vector, n_results=2)
                context = "\n\n".join(results['documents'][0])

            # 生成
            prompt = f"你是一个老程序员。请根据以下资料回答：\n\n资料：{context}\n\n问题：{query}"
            response = ai_client.chat.completions.create(
                model="cuc/deepseek",
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content

            st.markdown("### 💡 回答：")
            st.write(answer)

            with st.expander("查看 AI 参考了哪些原文片段"):
                st.write(context)
else:
    st.info("请先在上方上传一个 TXT 格式的文档，然后即可开始提问。")
