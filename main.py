import os
import time
import feedparser
import requests
import json
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, SSLError
from urllib.parse import urlparse
from urllib3.util.retry import Retry

# RSS_URL = "https://www.google.com.hk/alerts/feeds/08373742189599090702/14816707195864267476"
RSS_URL = "https://wechat-rss.daodao10y.top/feed/all.rss"
# RSS_URL = "http://100.104.81.103:8000/feed/all.rss"

def fetch_rss_news():
    """从 RSS 源抓取新闻并存储到数据库"""
    print("开始抓取谷歌快讯...")
    
    try:
        # 根据环境决定是否使用代理
        response = requests.get(RSS_URL)
        response.raise_for_status()
        feed = feedparser.parse(response.text)
        
        if not feed.entries:
            print("RSS源中没有新内容。")
            return 0
            
        for entry in feed.entries:
            print(json.dumps(entry, ensure_ascii=False, indent=2))
            break
        
        print(f"成功抓取 {len(feed.entries)} 条新闻并存入数据库。")
        return len(feed.entries)
        
    except Exception as e:
        print(f"抓取RSS源或数据库操作失败：{e}")
        return 0

if __name__ == "__main__":
    while True:
        fetch_rss_news()
        time.sleep(10000)
