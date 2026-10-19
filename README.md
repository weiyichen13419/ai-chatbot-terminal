# ai-chatbot-terminal
# RAG 本地知识库问答助手

基于本地文档和 DeepSeek 大模型构建的 RAG（检索增强生成）问答系统。通过向量检索与 Prompt 工程，解决大模型在特定领域知识上的“幻觉”问题。

## 🛠️ 技术栈
- **开发语言**：Python 3
- **向量模型**：Sentence-Transformers (`text2vec-base-chinese`)
- **向量数据库**：ChromaDB
- **大模型接口**：DeepSeek API (通过 OpenAI SDK 调用)

## ⚙️ 核心功能
1. **文档解析与切片**：自动读取本地 TXT 文档，按段落进行分块处理（Chunking）。
2. **语义检索**：将文本和用户问题转化为向量，在 ChromaDB 中计算余弦相似度，召回最相关的文档片段。
3. **精准问答与防幻觉**：将检索到的上下文与用户问题拼装进 Prompt，限制模型“仅根据资料回答”，有效防止模型胡编乱造。

## 🚀 运行说明
1. 安装依赖：`pip install sentence-transformers chromadb openai`
2. 在代码中填入你的大模型 API Key。
3. 准备你的本地知识库文件命名为 `doc.txt`，运行脚本即可。
