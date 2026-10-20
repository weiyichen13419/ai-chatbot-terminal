import os
from dotenv import load_dotenv
load_dotenv()
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI
import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="RAG 助手", page_icon="🤖")
st.title("🤖 RAG 知识库问答助手")

try:
    # 优先去 Streamlit 云端后台找 Secrets
    API_KEY = st.secrets["API_KEY"]
except Exception:
    # 在本地电脑跑，就去 .env 文件里找
    API_KEY = os.getenv("API_KEY")

# 为了防止出错，加个判断
if not API_KEY:
    st.error("⚠️ 未检测到 API Key！请配置 .env 文件或 Streamlit Secrets。")

@st.cache_resource
def load_resources():
    model = SentenceTransformer('shibing624/text2vec-base-chinese')
    db_client = chromadb.PersistentClient(path="./chroma_store")
    ai_client = OpenAI(
        base_url="https://openai.cuc.edu.cn/v1",
        api_key=API_KEY,
    )
    return model, db_client, ai_client

with st.spinner("正在加载 AI 模型（首次运行较慢）..."):
    model, db_client, ai_client = load_resources()

# 2. 文档解析函数（修复了 endswith 拼写错误，并增加了 PDF 换行处理）
def parse_file(uploaded_file):
    text = ""
    if uploaded_file.name.endswith(".txt") or uploaded_file.name.endswith(".md"):
        text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                # PDF 提取出来的文本往往没有分段，加上换行符方便后续切块
                text += page_text + "\n\n"
    return text

# 3. 网页交互
uploaded_file = st.file_uploader("请上传你的文档 (支持 TXT, MD, PDF)", type=["txt", "md", "pdf"])

if uploaded_file is not None:
    with st.spinner("正在解析文档..."):
        content = parse_file(uploaded_file)
        if not content.strip():
            st.error("❌ 解析失败：该文档可能是扫描版（纯图片），或者没有可提取的文本层。请换一个包含纯文本的 PDF/TXT 文件。")
            st.stop()  # 停止往下执行
        # 修复了按单换行切分的问题，改为按连续字符智能切分（每300字一块）
        chunk_size = 300
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size) if content[i:i+chunk_size].strip()]

    # 向量化并存入数据库
    collection_name = "uploaded_doc_v2"
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
            # 判断全局总结
            if "所有" in query or "全面" in query or "总结" in query or "都" in query:
                best_chunks = chunks  # 全量模式，所有块都给它
                st.info("检测到全局总结类问题，已切换为全量上下文模式。")
            else:
                # 普通问题，走向量检索
                query_vector = model.encode([query]).tolist()
                results = collection.query(query_embeddings=query_vector, n_results=3) # 多捞一点
                best_chunks = results['documents'][0] # 定义了之前漏掉的变量

            # 拼装带标号的上下文
            context_with_citations = ""
            for i, chunk in enumerate(best_chunks):
                context_with_citations += f"[{i + 1}] {chunk}\n\n"

            prompt = f"""
            你是一个严谨的 AI 助手。请严格根据以下带编号的参考资料回答问题。
            在回答时，如果你使用了某一段资料，请在句子末尾标注它的编号（例如 [1]）。
            如果你在资料中找不到答案，请直接回答“不知道”，绝对不要编造。

            【参考资料】：
            {context_with_citations}

            【问题】：
            {query}
            """

            # ⚠️ 修复了这里缩进跑到 try 外面的问题
            try:
                response = ai_client.chat.completions.create(
                    model="cuc/deepseek",
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response.choices[0].message.content

                st.markdown("### 💡 回答：")
                st.write(answer)

                # 展示带编号的原文，让用户能追溯
                with st.expander("查看 AI 参考了哪些原文片段"):
                    for i, chunk in enumerate(best_chunks):
                        st.markdown(f"**出处 [{i+1}]**：{chunk}")
            except Exception as e:
                st.error(f"调用大模型失败：{e}")
else:
    st.info("请先在上方上传一个文档，然后即可开始提问。")