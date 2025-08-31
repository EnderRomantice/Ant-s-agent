# config.py
WEBSITE_MAP = {
    "80小说": "https://www.8080txt.com/",
    "豆瓣": "https://movie.douban.com/top250",
}

API_KEY = "sk-4d6d53da8cd5438e9a11c5694327cee1"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"

# 工具函数描述
FUNCTIONS = [
    {
        "name": "scrape_website",
        "description": "根据网站名称爬取网页内容，分析有用信息并输出",
        "parameters": {
            "type": "object",
            "properties": {
                "site_name": {
                    "type": "string",
                    "description": "网站名称，如 '80小说', '豆瓣'",
                    "enum": list(WEBSITE_MAP.keys())
                }
            },
            "required": ["site_name"]
        }
    }
]