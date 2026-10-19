# 🤖 RAG 本地知识库问答助手

👉 **[在线体验地址（点击直接试玩）](https://ai-chatbot-terminal-qypshskplb763mbr2s2h7z.streamlit.app/)**

基于本地文档和大语言模型（DeepSeek）构建的 RAG（检索增强生成）问答系统。支持用户在网页端上传私有 TXT 文档，系统通过向量检索与 Prompt 工程，生成基于文档内容的精准回答，有效解决大模型的“幻觉”问题。

## 🛠️ 技术栈

- **前端交互**：Streamlit
- **开发语言**：Python 3
- **向量模型**：Sentence-Transformers (`text2vec-base-chinese`)
- **向量数据库**：ChromaDB (支持本地持久化)
- **大模型接口**：DeepSeek API (通过 OpenAI SDK 调用)

## ⚙️ 核心功能

1. **网页端交互与文件上传**：使用 Streamlit 构建 Web 界面，支持用户上传自定义 TXT 文档，无需修改代码即可实时更新知识库。
2. **智能分块与向量持久化**：自动解析上传的文档并按字数智能切片（Chunking）。使用 ChromaDB 的 `PersistentClient` 实现向量数据的本地持久化存储，避免重复计算。
3. **检索路由与防幻觉设计（核心）**：
   - 系统能识别用户的提问意图。对于**“全局总结类”**问题（如“列出所有...”），自动切换为**全量上下文注入**模式；对于普通问题，使用**语义检索**提取最相关的 3 个片段（Top-K）。
   - 通过严格设计的 System Prompt，强制大模型仅根据检索到的上下文作答，无依据时直接拒绝回答，杜绝胡编乱造。

## 🚀 运行说明（本地部署）

 克隆仓库并在本地安装依赖：
   pip install streamlit sentence-transformers chromadb openai


📝 开发者踩坑与优化记录
文档切片（Chunking）导致的检索断裂：测试中发现，按空行切分容易导致上下文丢失（如列举类问题回答不全）。通过实现“全局总结路由”，在遇到特定关键词时绕过向量检索，直接向大模型注入全文上下文，完美解决了该问题。

环境依赖冲突：部署至 Streamlit Cloud 时，通过配置 requirements.txt 以及强制设置 HuggingFace 国内镜像源，解决了云端下载模型超时和依赖缺失的问题。
