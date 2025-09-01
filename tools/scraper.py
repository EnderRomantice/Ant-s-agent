import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def scrape_website(site_name: str, website_map: dict) -> str:
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

        for script in soup(["script", "style"]): 
            script.decompose()

        # === 提取内容：保留原始文本 ===
        text_content = soup.get_text(strip=True)[:2000]

        # === 提取所有 a 标签链接（包括小说）===
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        all_links = []
        for a in soup.find_all('a', href=True):
            full_url = urljoin(base_url, a['href'])
            # 只保留同站链接
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                text = a.get_text(strip=True)
                if not text:
                    text = "[无文本]"
                all_links.append({
                    "text": text,
                    "url": full_url
                })

        # 返回结构化数据
        return json.dumps({
            "site_name": site_name,
            "url": url,
            "content": text_content,
            "all_links": all_links 
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"爬取失败: {str(e)}"}, ensure_ascii=False)


def scrape_link(link: str) -> str:
    try:
        response = requests.get(
            link,
            headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
},
            timeout=120
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        content = (text[:2000] + "...") if len(text) > 2000 else text
        
        return json.dumps({
            "link": link,
            "content": content
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"爬取失败: {str(e)}"}, ensure_ascii=False)


# 提取指定网站页面中的所有链接
def extract_links(site_name: str, website_map: dict, max_links: int = 50) -> str:
    """
    从指定网站主页中提取所有 <a> 标签的链接，供用户选择是否进一步爬取
    """
    if site_name not in website_map:
        return json.dumps({"error": f"未知网站: {site_name}"}, ensure_ascii=False)
    
    url = website_map[site_name]
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    
    try:
        response = requests.get(
            url,
            headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
},
            timeout=120
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            full_url = urljoin(base_url, href)  # 转为绝对路径

            # 只保留同一主域下的链接
            if urlparse(full_url).netloc != urlparse(base_url).netloc:
                continue

            link_text = a_tag.get_text(strip=True) or "[无文本]"
            links.append({
                "text": link_text,
                "url": full_url
            })

        # 去重（基于 URL）
        seen = set()
        unique_links = []
        for link in links:
            if link["url"] not in seen:
                seen.add(link["url"])
                unique_links.append(link)

        # 限制数量
        unique_links = unique_links[:max_links]

        return json.dumps({
            "site_name": site_name,
            "base_url": url,
            "total_links_found": len(links),
            "unique_internal_links": len(unique_links),
            "links": unique_links,
            "instruction": "请选择是否需要深入爬取以上某个链接，回复对应 URL 或序号。"
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"提取链接失败: {str(e)}"}, ensure_ascii=False)