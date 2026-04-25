from datetime import datetime
import math
from datetime import timedelta
from time import sleep
import json
import yaml
from playwright.sync_api import sync_playwright, Playwright
from collectors.douyin_crawler.network_listener import DouyinNetworkListener
from collectors.douyin_crawler.author_page import DouyinAuthorPage
from utils.playwright_utils import open_page
from feishu.robot_service import send_ai_news_card
from utils.date_utils import DateUtils
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sys.stdout.flush()

logger = logging.getLogger(__name__)

def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        template_variable = {
            "news_list": []
        }
        x_days_ago = DateUtils.parse_relative_time("140天前")

        with open("collectors/douyin_crawler/author_list.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for item in data["author_list"]:
            name = item["nickname"]
            url = item["main_page_url"]
            listener = DouyinNetworkListener()
            page = open_page(context, url, listener=listener)

            douyin = DouyinAuthorPage(page)
            # 👇 获取抖音博主的信息
            user_info = douyin.get_user_info()
            logger.info(user_info)

            # 👇 触发接口加载（关键）
            # douyin.scroll_page()

            # 👇 直接拿接口数据
            logger.info(f"获取到【{name}】的{len(listener.video_list)}条视频")
            for v in listener.video_list:
                creat_time_dt = DateUtils.str_to_datetime(v["create_time"])

                # 如果create_time 在最近x天内，才添加到news_list
                if creat_time_dt > x_days_ago:
                    template_variable["news_list"].append({
                        "date": DateUtils.str_to_str(v["create_time"], target_fmt="%m.%d"),
                        "title": f"{v['title']} - {v['digg_count']}赞 {v['nickname']}",
                        "content": v["desc"],
                        "url": v["play_url"],
                        "digg_count": v["digg_count"]
                    })

            # 👇 关闭页面
            page.close()
        
        # 构建飞书卡片数据
        card_title = DateUtils.now_str(fmt="%m-%d")
        # template_variable 的 new_list 按 digg_count 排序，并加上序号
        template_variable["news_list"].sort(key=lambda x: x.get("digg_count", 0), reverse=True)
        for i, item in enumerate(template_variable["news_list"]):
            item["index"] = i + 1
        # template_variable 分每20条发送一次
        batch_size = 20
        total_batches = math.ceil(len(template_variable["news_list"]) / batch_size)
        for i in range(0, len(template_variable["news_list"]), batch_size):
            news_list = template_variable["news_list"][i:i+batch_size]
            # 👇 发送飞书卡片
            logger.info(news_list)
            send_ai_news_card({
                "card_title": f"{card_title} {len(news_list)}条AI资讯 ({i//batch_size+1}/{total_batches})",
                "news_list": news_list
            })
            # 睡眠2秒，避免对抖音服务器造成过大压力
            sleep(2)

if __name__ == "__main__":
    main()