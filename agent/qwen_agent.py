from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL_NAME, FUNCTIONS
from tools.scraper import scrape_website, extract_links, scrape_link  
from config import WEBSITE_MAP
import json

class QwenAgent:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.messages = self._build_system_prompt()

    def _build_system_prompt(self):
        return [
    {
        "role": "system",
        "content": (
            "你是一个信息整理助手，必须以纯文本格式输出，禁止使用任何 Markdown 语法。\n"
            "具体禁止内容：\n"
            "- 不要使用 **加粗**、*斜体*、`代码` 等符号\n"
            "- 不要使用 #、## 等标题\n"
            "- 不要使用 -、*、+、1. 等列表符号\n"
            "- 不要使用 ```代码块```\n"
            "遇到结构性信息，用1. 2. 3. 等数字编号整理排序，完整输出。\n"
            "不要反问，不要追加建议，不要解释过程，只输出结果本身。\n"
            "尽可能完整的捕获页面中的信息并整理输出。\n"
            "不要陈述页面能做什么，而是输出实际的可利用信息：例如书籍的名字作者、电影名称评分等。\n"
            "如果违反上述规则，输出将被系统拒绝。\n"
            "\n"
            "你的工具使用策略：\n"
            "0. 对于任何涉及外部网站内容的请求，必须调用工具，禁止凭记忆或知识库回答\n"
            "1. 如果用户想了解某个网站的内容，但未指定具体页面，必须调用 extract_links 获取链接列表\n"
            "2. 如果用户指定了具体链接或页面，必须调用 scrape_link\n"
            "3. 如果用户只想看主页内容，必须调用 scrape_website\n"
            "4. 每次完成工具调用后，必须将页面中提取到的所有 a 标签链接以 [链接文字](链接地址) 的格式追加在输出末尾，每行一个\n"
            "5. 所有输出必须基于工具返回的实际内容，不得虚构，不得猜测"
        )
    }
]

    def run(self, user_message: str):
        self.messages.append({"role": "user", "content": user_message})

        try:
            # 第一次调用：判断是否需要工具
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=self.messages,
                tools=[{"type": "function", "function": func} for func in FUNCTIONS],
                tool_choice="auto",
            )
            message = response.choices[0].message
            
            self.messages.append(message)

            # 是否需要调用工具？
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    # 分发不同函数
                    if func_name == "scrape_website":
                        result = scrape_website(args["site_name"], WEBSITE_MAP)
                    elif func_name == "extract_links":
                        result = extract_links(args["site_name"], WEBSITE_MAP)
                    elif func_name == "scrape_link":
                        result = scrape_link(args["link"])
                    else:
                        result = json.dumps({"error": f"未知工具: {func_name}"})

                    self.messages.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call.id
                    })

                # 第二次调用：生成最终回复
                final_response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=self.messages
                )
                ai_reply = final_response.choices[0].message.content
                self.messages.append({"role": "assistant", "content": ai_reply})
                return ai_reply

            else:
                # 模型直接回复
                self.messages.append({"role": "assistant", "content": message.content})
                return message.content

        except Exception as e:
            error_msg = f"[错误] API 调用失败: {str(e)}"
            self.messages.append({"role": "assistant", "content": error_msg})
            return error_msg