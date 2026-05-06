from datetime import datetime
import math
from datetime import timedelta
from time import sleep
import json
import yaml
from utils.file_utils import FileUtils
from playwright.sync_api import sync_playwright, Playwright
from collectors.douyin_crawler.network_listener import DouyinNetworkListener
from collectors.douyin_crawler.author_page import DouyinAuthorPage
from utils.playwright_utils import open_page
from feishu.robot_service import MsgBotService
from utils.date_utils import DateUtils
from loguru import logger


def begin_crawler(relative_time: str = "7天前", send_to_gf: bool = False):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        template_variable = {
            "news_list": []
        }
        x_days_ago = DateUtils.parse_relative_time(relative_time)

        author_list_file = FileUtils.get_path("collectors", "douyin_crawler", "author_list.yaml")
        with open(author_list_file, "r", encoding="utf-8") as f:
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
                        "date": DateUtils.str_to_str(v["create_time"], to_fmt="%m.%d"),
                        "title": f"{v['title']} - {v['digg_count']}赞 {v['nickname']}",
                        "content": v["desc"],
                        "url": v["play_url"],
                        "digg_count": v["digg_count"]
                    })

            # 👇 关闭页面
            page.close()
        
        # 构建飞书卡片数据
        # template_variable 的 new_list 按 digg_count 排序，并加上序号
        logger.info("构建飞书卡片数据...")
        template_variable["news_list"].sort(key=lambda x: x.get("digg_count", 0), reverse=True)
        for i, item in enumerate(template_variable["news_list"]):
            item["index"] = i + 1
        # template_variable 分每20条发送一次
        batch_size = 20
        total_batches = math.ceil(len(template_variable["news_list"]) / batch_size)

        # 发送飞书卡片消息
        logger.info("发送飞书卡片消息...")
        msg_bot_service = MsgBotService()
        for i in range(0, len(template_variable["news_list"]), batch_size):
            news_list = template_variable["news_list"][i:i+batch_size]
            # 👇 发送飞书卡片
            msg_bot_service.send_ai_news_card(template_variable={
                "card_title": f"{DateUtils.now_str(fmt='%m-%d')} {len(news_list)}条AI资讯 ({i//batch_size+1}/{total_batches})",
                "news_list": news_list
            })
            # 发送到广服正式群
            if send_to_gf:
                logger.info(f"发送到广服正式群...")
                sleep(1)
                msg_bot_service.send_ai_news_card(
                    chat_id=msg_bot_service.templates.ai_news_gf_chat_id,
                    template_variable={
                        "card_title": f"{DateUtils.now_str(fmt='%m-%d')} {len(news_list)}条AI资讯 ({i//batch_size+1}/{total_batches})",
                        "news_list": news_list
                    }
                )
            # 睡眠2秒，避免对抖音服务器造成过大压力
            sleep(2)

if __name__ == "__main__":
    begin_crawler("7天前")
