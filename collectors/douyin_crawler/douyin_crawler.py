import json
import yaml
from playwright.sync_api import sync_playwright
from collectors.douyin_crawler.network_listener import DouyinNetworkListener
from collectors.douyin_crawler.author_page import DouyinAuthorPage
from utils.playwright_utils import open_page
from feishu.robot_service import send_ai_news_card

def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        listener = DouyinNetworkListener()

        with open("collectors/douyin_crawler/author_list.yaml", "r") as f:
            data = yaml.safe_load(f)
        for item in data["author_list"]:
            name = item["nickname"]
            url = item["main_page_url"]
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

            template_variable = {
                "news_list": []
            }

            # template_variable = {
            #     "news_list": [
            #         {
            #             "title": "测试标题",
            #             "content": "测试内容",
            #             "url": "https://www.baidu.com",
            #         }
            #     ]
            # }

            for v in listener.video_list:
                print(v)
                template_variable["news_list"].append({
                    "title": v["title"],
                    "content": v["desc"],
                    "url": v["play_url"]
                })
                # print(v["play_url"])
                # 👇 保存视频信息到数据库
                # save_video_info(v, name)

            send_ai_news_card(template_variable)

if __name__ == "__main__":
    main()