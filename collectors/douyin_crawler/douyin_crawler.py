import json
from playwright.sync_api import sync_playwright
from network_listener import DouyinNetworkListener
from author_page import DouyinAuthorPage
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.playwright_utils import find_pages_by_title, open_page

def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        listener = DouyinNetworkListener()

        with open("douyin_author_list.json", "r") as f:
            data = json.load(f)
        for item in data["author_list"]:
            name = item["name"]
            url = item["url"]
            page = open_page(context, url, listener=listener)
            # page = find_pages_by_title(context, "大师的AI小灶")[0]["page"]

            douyin = DouyinAuthorPage(page)
            # 👇 获取抖音博主的信息
            user_info = douyin.get_user_info()
            print(user_info)

            # 👇 触发接口加载（关键）
            # douyin.scroll_page()


            # 👇 打开视频并获取详情
            # douyin.open_video_and_get_detail()

            # 👇 直接拿接口数据
            for v in listener.video_list:
                print(v)
                # 👇 保存视频信息到数据库
                save_video_info(v, name)

if __name__ == "__main__":
    main()