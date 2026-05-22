from datetime import datetime, timedelta
from typing import Optional, Tuple, Union
import os
import sys

from utils.db_utils import fetch_all
from utils.feishu_sheet_utils import FeishuSheetUtils


def list_wechat_articles():
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
        WHERE publish_time > UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 7 DAY))
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
    LIMIT 10
    """

    # 2. 函数调用变得非常清爽
    articles = fetch_all(
        database_env_name="ALI22_MYSQL_DATABASE_WECHATRSS_NAME", sql=SQL_QUERY
    )
    return articles


def save_wechat_articles_to_feishu_sheet(articles: list = None):
    articles = list_wechat_articles()
    if not articles:
        return
    fs = FeishuSheetUtils(spreadsheet_token="ZzgQstUP2h2fHWtCwrXco2kXnyb")

    if len(articles) == 0:
        return

    data = []
    # 第一行是表头
    sheet_title = ["type"] + list(articles[0].keys())
    data.append(sheet_title)
    for article in articles:
        # 根据 articles[0].keys() 来逐一获取数据，
        row = ["wechat"]
        row.extend([article[key] for key in sheet_title[1:]])
        data.append(row)
    fs.append_rows(range="9a768f!A:E", rows_data=data)


if __name__ == "__main__":
    save_wechat_articles_to_feishu_sheet()
