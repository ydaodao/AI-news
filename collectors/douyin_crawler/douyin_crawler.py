from datetime import datetime
from datetime import timedelta
import json
import yaml
from playwright.sync_api import sync_playwright
from collectors.douyin_crawler.network_listener import DouyinNetworkListener
from collectors.douyin_crawler.author_page import DouyinAuthorPage
from utils.playwright_utils import open_page
from feishu.robot_service import send_ai_news_card
from utils.date_utils import DateUtils

def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        listener = DouyinNetworkListener()

        template_variable = {
            "news_list": []
        }
        x_days_ago = DateUtils.parse_relative_time("100天前")

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

            

            for v in listener.video_list:
                creat_time_dt = DateUtils.str_to_datetime(v["create_time"])
                creat_time_to_strdate = DateUtils.datetime_to_str(creat_time_dt, fmt="%m.%d")

                # 如果create_time 在最近x天内，才添加到news_list
                if creat_time_dt > x_days_ago:
                    template_variable["news_list"].append({
                        "date": creat_time_to_strdate,
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