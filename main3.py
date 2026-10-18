from openai import OpenAI
import json
from pathlib import Path
import time

#调用存放聊天记录的转json文件
memory_path=Path("memory.json")

if memory_path.exists():
    with memory_path.open('r',encoding="utf-8") as f:
         messages_history = json.load(f)
    print("【系统提示：成功读取了之前的聊天记忆！】\n")
else:
    messages_history = [
        {"role": "system", "content": "你是一个脾气暴躁的老程序员，说话带刺，但技术很强。"}
    ]
    print("【系统提示：未找到历史记录，已启动全新会话。】\n")

# 1. 初始化客户端（填入地址和真实 Key）
client = OpenAI(
    base_url="https://openai.cuc.edu.cn/v1",
    api_key="",
)
now=time.strftime('%Y-%m-%d %H:%M:%S')

print(f"现在是{now},终端聊天机器人已启动！输入 'stop' 结束对话。\n")

while True:
    user_input=input('你：')

    if user_input=='stop':
        print(f"现在是{now},ai: 赶紧滚去写代码吧！再见！")
        break

    if user_input.strip()=='':
        print(f'现在是{now},输入为空，请重新输入')
        continue
    messages_history.append({"role": "user", "content": user_input})

    print(f'现在是{now}，正在思考...\n')
    try:
        completion = client.chat.completions.create(
            model="cuc/deepseek",
            messages=messages_history,
        )
        ai_reply = completion.choices[0].message.content

        messages_history.append({"role": "assistant", "content": ai_reply})
        print(f'现在是{now},ai: {ai_reply}\n')

        with open(memory_path,'w',encoding="utf-8") as f:
            json.dump(messages_history,f,ensure_ascii=False,indent=2)

    except Exception as e:
        print(f'出错了！错误类型：{e}')
