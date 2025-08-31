# tools/scraper.py
import json
import requests
from bs4 import BeautifulSoup

def scrape_website(site_name: str, website_map) -> str:
    if site_name not in website_map:
        return json.dumps({"error": f"未知网站: {site_name}"})
    
    url = website_map[site_name]
    try:
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 清理
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 提取文本并截断
        text = soup.get_text(separator=' ', strip=True)
        content = (text[:2000] + "...") if len(text) > 2000 else text

        return json.dumps({
            "site_name": site_name,
            "url": url,
            "content": content
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"爬取失败: {str(e)}"}, ensure_ascii=False)