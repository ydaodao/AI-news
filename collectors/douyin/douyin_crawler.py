from datetime import datetime
import math
from datetime import timedelta
from time import sleep
import json
import yaml
from utils.file_utils import FileUtils
from playwright.sync_api import sync_playwright, Playwright
from collectors.douyin.network_listener import DouyinNetworkListener
from collectors.douyin.author_page import DouyinAuthorPage
from utils.playwright_utils import open_page
from feishu.robot_service import MsgBotService
from utils.date_utils import DateUtils
from loguru import logger
from utils.feishu_sheet_utils import FeishuSheetUtils

SPREADSHEET_TOKEN = "KAu1sigLPhMLxlt0odDcXDbPnmx"


def begin_crawler(relative_time: str = "7天前", write_to_sheet: bool = False):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        template_variable = {"news_list": []}
        x_days_ago = DateUtils.parse_relative_time(relative_time)

        author_list_file = FileUtils.get_path(
            "collectors", "douyin", "author_list.yaml"
        )
        with open(author_list_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        video_list = []
        for item in data["author_list"]:
            name = item["nickname"]
            url = item["main_page_url"]
            listener = DouyinNetworkListener()
            page = open_page(context, url, listener=listener)

            douyin = DouyinAuthorPage(page)
            # 👇 获取抖音博主的信息
            user_info = douyin.get_user_info()
            logger.info(user_info)

            # 👇 直接拿接口数据
            logger.info(f"获取到【{name}】的{len(listener.video_list)}条视频")
            video_list.extend(listener.video_list)

            # 👇 关闭页面
            page.close()

        # video_list 按 creat_time_dt > x_days_ago 过滤
        video_list = [
            v
            for v in video_list
            if DateUtils.str_to_datetime(v["create_time"]) > x_days_ago
        ]
        # video_list 按 digg_count 排序
        video_list.sort(key=lambda x: x.get("digg_count", 0), reverse=True)

        # template_variable 的 new_list 按 digg_count 排序
        template_variable["news_list"].sort(
            key=lambda x: x.get("digg_count", 0), reverse=True
        )

        # 提取 relative_time 的数字
        x_days = int(relative_time.replace("天前", ""))

        # 构建飞书卡片数据
        send_feishu_card(video_list, x_days)

        # 写入飞书表格
        if write_to_sheet:
            save_douyin_videos_to_feishu_sheet(video_list, x_days)


def send_feishu_card(video_list, x_days):
    template_variable = {"news_list": []}
    for i, v in enumerate(video_list):
        template_variable["news_list"].append(
            {
                "index": i + 1,
                "date": DateUtils.str_to_str(v["create_time"], to_fmt="%m.%d"),
                "title": f"{v['title']} - {v['digg_count']}赞 {v['nickname']}",
                "content": v["desc"],
                "url": v["play_url"],
                "digg_count": v["digg_count"],
            }
        )

    logger.info("构建飞书卡片数据...")
    batch_size = 20
    total_batches = math.ceil(len(template_variable["news_list"]) / batch_size)

    # 发送飞书卡片消息
    logger.info("发送飞书卡片消息...")
    msg_bot_service = MsgBotService()
    for i in range(0, len(template_variable["news_list"]), batch_size):
        news_list = template_variable["news_list"][i : i + batch_size]
        # 👇 发送飞书卡片
        msg_bot_service.send_ai_news_card(
            template_variable={
                "card_title": f"{DateUtils.now_str(fmt='%m.%d')}-近{x_days}天 {len(news_list)}条AI资讯 ({i//batch_size+1}/{total_batches})",
                "news_list": news_list,
            }
        )
        sleep(2)


def save_douyin_videos_to_feishu_sheet(video_list, x_days):
    if not video_list:
        return
    if len(video_list) == 0:
        return
    data = []
    # 第一行是表头
    sheet_title = ["类型", "抖音号", "标题", "描述", "点赞", "链接", "发布时间"]
    data.append(sheet_title)
    for video in video_list:
        row = ["抖音视频"]
        row.append(video["nickname"])
        row.append(video["title"])
        row.append(video["desc"])
        row.append(video["digg_count"])
        row.append(video["play_url"])
        row.append(video["create_time"])
        data.append(row)

    logger.info(f"写入抖音视频 {len(data)-1}条 至飞书表格")
    fs = FeishuSheetUtils(spreadsheet_token=SPREADSHEET_TOKEN)
    new_sheet = fs.add_sheet(
        title=f"{DateUtils.now_str(fmt='%m.%d')}抖音-近{x_days}天",
        index=0,
        delete_if_exists=True,
    )
    new_sheet_id = new_sheet["replies"][0]["addSheet"]["properties"]["sheetId"]
    fs.append_rows(range=f"{new_sheet_id}!A:G", rows_data=data)
    logger.info(f"写入完毕")


if __name__ == "__main__":
    # 测试环境用这个 token
    SPREADSHEET_TOKEN = "ZzgQstUP2h2fHWtCwrXco2kXnyb"
    begin_crawler("14天前", write_to_sheet=True)
