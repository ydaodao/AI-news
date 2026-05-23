from datetime import datetime, timedelta
from typing import Optional, Tuple, Union
import os
import sys

from utils.date_utils import DateUtils
from utils.db_utils import fetch_all
from utils.feishu_sheet_utils import FeishuSheetUtils
from loguru import logger

SPREADSHEET_TOKEN = "KAu1sigLPhMLxlt0odDcXDbPnmx"


def list_wechat_articles(x_days):
    # 1. 将 SQL 提取为独立变量，并去掉了无意义的子查询
    SQL_QUERY = """
    SELECT
        a.mp_id,
        f.mp_name,
        a.publish_time,
        a.title,
        a.description,
        a.url
    FROM
    (
        -- 1. 筛选 publish_time 大于 7天前的数据
        SELECT 
        mp_id, title, description, 
        FROM_UNIXTIME(publish_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS publish_time, 
        url
        FROM articles
        WHERE publish_time > UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL %s DAY))
    ) a
    LEFT JOIN
    (
        -- 2. 右表 feeds 的查询
        SELECT id, mp_name FROM feeds
    ) f ON a.mp_id = f.id
    WHERE
        f.mp_name NOT IN ('全球风口')
    ORDER BY
        a.publish_time ASC
    """

    # 2. 函数调用变得非常清爽
    articles = fetch_all(
        database_env_name="ALI22_MYSQL_DATABASE_WECHATRSS_NAME",
        sql=SQL_QUERY,
        params=(x_days,),
    )
    return articles


def save_wechat_articles_to_feishu_sheet(x_days):
    articles = list_wechat_articles(x_days)
    if not articles:
        return

    if len(articles) == 0:
        return

    data = []
    # 第一行是表头
    sheet_title = ["类型", "公众号", "发布时间", "标题", "描述", "链接"]
    data.append(sheet_title)
    for article in articles:
        # 根据 articles[0].keys() 来逐一获取数据，
        row = ["公众号"]
        row.append(article["mp_name"])
        row.append(article["publish_time"])
        row.append(article["title"])
        row.append(article["description"])
        row.append(article["url"])
        data.append(row)

    logger.info(f"写入公众号文章 {len(data)-1}篇 至飞书表格")
    fs = FeishuSheetUtils(spreadsheet_token=SPREADSHEET_TOKEN)
    new_sheet = fs.add_sheet(
        title=f"{DateUtils.now_str(fmt='%m.%d')}公众号-近{x_days}天",
        index=0,
        delete_if_exists=True,
    )
    new_sheet_id = new_sheet["replies"][0]["addSheet"]["properties"]["sheetId"]

    fs.append_rows(range=f"{new_sheet_id}!A:E", rows_data=data)
    logger.info(f"写入完毕")


if __name__ == "__main__":
    # 测试环境用这个 token
    SPREADSHEET_TOKEN = "ZzgQstUP2h2fHWtCwrXco2kXnyb"
    save_wechat_articles_to_feishu_sheet(7)
