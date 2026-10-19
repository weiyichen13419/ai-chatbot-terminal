import os
from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI

# 1. 读取文档、切块、加载模型、存入数据库
def split_into_chunks(file_path):
    with open(file_path,'r',encoding='utf-8') as f:
        content = f.read()
    raw_chunks = content.split("\n\n")
    return[chunk.strip()for chunk in raw_chunks if chunk.strip()]


print("正在初始化知识库...")
chunks = split_into_chunks("doc.txt")
model=SentenceTransformer('shibing624/text2vec-base-chinese')
client = chromadb.Client()

try:
    client.delete_collection(name="manwei_vs_gu")
except:
    pass
collection = client.get_or_create_collection(name="manwei_vs_gu")
embeddings = model.encode(chunks).tolist()
ids = [str(i) for i in range(len(chunks))]
collection.add(documents=chunks,embeddings=embeddings,ids=ids)

ai_client = OpenAI(
    base_url="https://openai.cuc.edu.cn/v1",
    api_key="",
)

print("\n✅ 知识库加载完毕！你现在可以开始提问了。")
print("（输入 '退出' 结束程序）\n" + "-"*30)

while True:
    user_query = input("\n你问：").strip()  # .strip() 可以去除你不小心打出的空格

    if user_query == "退出":
        print("再见！")
        break

    if user_query == "":
        print("你什么都没输入啊！")
        continue

    print("正在翻找资料...")
    query_embeddings = model.encode([user_query]).tolist()
    results = collection.query(
        query_embeddings=query_embeddings,
        n_results=3
    )

    best_chunk = results['documents'][0][0]

    print("正在让暴躁老哥组织语言...")
    prompt = f"""
    你是一个脾气暴躁的老程序员。请严格根据下面的【参考资料】回答我的问题。如果资料里没有，你就直接骂街说不知道，绝对不要瞎编。

    【参考资料】：
    {best_chunk}

    【我的问题】：
    {user_query}
    """

    try:
        # ⚠️ 注意：下面这 4 行代码，前面必须对齐，不能多空格，也不能少空格！
        response = ai_client.chat.completions.create(
            model="cuc/deepseek",
            messages=[{"role": "user", "content": prompt}]
        )
        print(f"\n【暴躁老哥的回答】：\n{response.choices[0].message.content}")

    except Exception as e:
        print(f"哎呀出错了：{e}")