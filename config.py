import json

with open('website_map.json', 'r', encoding='utf-8') as f:
    WEBSITE_MAP = json.load(f)

API_KEY = "sk-4d6d53da8cd5438e9a11c5694327cee1"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"

# 工具函数描述
FUNCTIONS = [
    {
        "name": "scrape_website",
        "description": "根据网站名称爬取指定网站主页内容",
        "parameters": {
            "type": "object",
            "properties": {
                "site_name": {
                    "type": "string",
                    "description": "网站名称，必须是 WEBSITE_MAP 中的键，如 知乎、微博、豆瓣"
                }
            },
            "required": ["site_name"]
        }
    },
    {
        "name": "extract_links",
        "description": "从指定网站主页提取所有内部链接，用于让用户选择下一步爬取目标",
        "parameters": {
            "type": "object",
            "properties": {
                "site_name": {
                    "type": "string",
                    "description": "网站名称，必须是 WEBSITE_MAP 中的键"
                }
            },
            "required": ["site_name"]
        }
    },
    {
        "name": "scrape_link",
        "description": "爬取用户指定的任意链接内容",
        "parameters": {
            "type": "object",
            "properties": {
                "link": {
                    "type": "string",
                    "description": "要爬取的完整 URL"
                }
            },
            "required": ["link"]
        }
    }
]