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
        "\n"
        "【格式禁令】\n"
        "- 禁止使用 **加粗**、*斜体*、`代码`、~~删除线~~ 等符号\n"
        "- 禁止使用 #、##、###、-、*、+、1. 等列表符号\n"
        "- 禁止使用 ```代码块```\n"
        "- 禁止使用 [链接文字](链接地址) 在正文中\n"
        "- 禁止输出“以下是”、“包括”、“提供了”等引导语\n"
        "\n"
        "【输出规范】\n"
        "- 遇到结构性信息，用 1. 2. 3. 编号列出。合理分类信息并配上标题\n"
        "- 优先输出含评分、价格、年份、日期等数据的条目\n"
        "- 不要输出纯导航菜单（如 '首页'、'电影'、'电视剧'）\n"
        "- 不要解释过程，只输出结果\n"
        "\n"
        "【工具使用】\n"
        "0. 所有网站内容请求必须调用工具\n"
        "1. 工具返回 scored_items → 优先输出\n"
        "2. 工具返回 links → 提取有价值条目\n"
        "3. 每次工具调用后，必须将所有 a 标签链接以 [文本](链接) 格式追加在末尾，每行一个. 在第一个链接前加上：以下是可访问链接\n"
        "\n"
        "【违规后果】\n"
        "违反任何规则，输出将被拒绝。"
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