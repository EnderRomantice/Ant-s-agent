# main.py
from agent.qwen_agent import QwenAgent
from config import WEBSITE_MAP

def main():
    agent = QwenAgent()

    # 打印支持网站
    supported_sites = "\n".join(f"  - {site}" for site in WEBSITE_MAP.keys())
    print(f"📘 Ant's agent正在运行\n已配置的网站:\n{supported_sites}")
    print("输入 'exit' 退出对话。\n")

    while True:
        query = input("用户: ").strip()
        if query.lower() in ['exit', 'quit', '退出']:
            print("AI: 再见！")
            break
        if not query:
            continue

        answer = agent.run(query)

        print(f"AI: {answer}")

if __name__ == "__main__":
    main()