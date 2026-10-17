from openai import OpenAI

# 1. 初始化客户端（填入地址和真实 Key）
client = OpenAI(
    base_url="https://openai.cuc.edu.cn/v1",
    api_key="sk-EYcFUVIYYFRus8CsGl4baRWrlf81rhrbpBsnMyNblJcoWr1W",
)

# 2. 发送请求给大模型
print("正在呼叫中传 DeepSeek，请稍候...\n")

completion = client.chat.completions.create(
    model="cuc/deepseek",
    messages=[
        {"role": "user", "content": "你好，请简短帮我介绍一下蛊真人这本书"}
    ],
)

# 3. 打印 AI 的回答
print(completion.choices[0].message.content)