# 🤖 RAG 本地知识库问答助手

👉 **[在线体验地址（点击直接试玩）]（https://ai-chatbot-terminal-qvpshskplb763mbr2s2h7z.streamlit.app/)*

基于本地文档和大语言模型（DeepSeek）构建的 RAG（检索增强生成）问答系统。支持用户在网页端上传私有 TXT、Markdown 和 PDF 文档。系统通过向量检索与 Prompt 工程，生成基于文档内容的精准回答，并附带**原文引用溯源**，有效解决大模型的“幻觉”问题。

## 🛠️ 技术栈

- **前端交互**：Streamlit (单页面应用)
- **开发语言**：Python 3
- **文档解析**：PyPDF (支持 PDF 提取), 内置原生读写 (TXT/MD)
- **向量模型**：Sentence-Transformers (`text2vec-base-chinese`)
- **向量数据库**：ChromaDB (支持本地持久化)
- **大模型接口**：DeepSeek API (通过 OpenAI SDK 调用)
- **安全配置**：`python-dotenv` / `Streamlit Secrets` 密钥隔离

## ⚙️ 核心功能

1. **多格式文档解析与上传**：支持上传 TXT、Markdown 以及真实场景下的 PDF 文档。系统自动提取文本，并按固定长度进行智能切片（Chunking），过滤无效空行。
2. **引用溯源（Citation）与防幻觉**：
   - 系统将检索到的相关片段拼接时，自动为每个片段打上 `[1]`、`[2]` 的标签。
   - 通过严谨的 System Prompt 限制大模型：必须根据资料回答，并标注引用的标签；无依据时直接回答“不知道”，从根源上杜绝大模型胡编乱造。
3. **检索路由机制**：对于“全局总结类”问题（如“列出所有规定”），系统自动识别并切换为**全量上下文注入**模式；对于具体细节问题，则采用**语义检索（Top-K）**模式，兼顾了回答的全面性与精准度。
4. **向量数据库持久化**：使用 ChromaDB 的 `PersistentClient` 将向量保存至本地磁盘，避免每次启动时的重复计算开销。

## 🚀 运行说明（本地部署）

1. 克隆仓库并在本地安装依赖：
   ```bash
   pip install -r requirements.txt
   在项目根目录下创建 .env 文件，配置你的大模型 API 密钥：
2.在项目根目录下创建 .env 文件，配置你的大模型 API 密钥：
text
API_KEY=你的_sk_开头的_API_KEY
(注：云端部署时，请在 Streamlit Cloud 的 Secrets 中配置 API_KEY)

3.启动 Streamlit 应用：
bash
streamlit run web_app.py

📝 开发者踩坑与优化记录
PDF 提取空白导致向量化报错：真实场景下部分 PDF 为扫描件，提取文本为空，导致 ChromaDB 报错。系统加入了防空值拦截，若解析出空文本则提示用户更换文档。

文档切片断裂导致检索不全：按空行切分易导致长段落上下文丢失。后续加入了“全局总结路由”机制，遇到特定关键词时跳过检索，直接注入全文，完美解决宏观总结遗漏的问题。
