from openai import OpenAI

# 1. 初始化客户端（填入地址和真实 Key）
client = OpenAI(
    base_url="https://openai.cuc.edu.cn/v1",
    api_key="",
)

messages_history = [
    {"role": "system", "content": "你是一个脾气暴躁的老程序员，说话带刺，但技术很强。"}
]

print("终端聊天机器人已启动！输入 'stop' 结束对话。\n")

while True:
    user_input=input('你：')

    if user_input=='stop':
        print("机器人: 赶紧滚去写代码吧！再见！")
        break

    if user_input.strip()=='':
        print('输入为空，请重新输入')
        continue
    messages_history.append({"role": "user", "content": user_input})

    print('正在思考...\n')
    try:
        completion = client.chat.completions.create(
            model="cuc/deepseek",
            messages=messages_history,
        )
        ai_reply = completion.choices[0].message.content

        messages_history.append({"role": "assistant", "content": ai_reply})
        print(f'ai: {ai_reply}')
    except Exception as e:
        print(f'出错了！错误类型：{e}')
