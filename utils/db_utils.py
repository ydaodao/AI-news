import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence

import pymysql
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return value if value is not None else default


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


def load_db_config(database_env_name: str) -> DbConfig:
    return DbConfig(
        host=_env("ALI22_MYSQL_DATABASE_URL"),
        port=int(_env("ALI22_MYSQL_DATABASE_PORT", "3306")),
        user=_env("ALI22_MYSQL_DATABASE_USER"),
        password=_env("ALI22_MYSQL_DATABASE_PASSWORD"),
        database=_env(database_env_name),
    )


@contextmanager
def connect(database_env_name: str):
    cfg = load_db_config(database_env_name)
    conn = pymysql.connect(
        host=cfg.host,
        port=cfg.port,
        user=cfg.user,
        password=cfg.password,
        database=cfg.database,
        charset="utf8mb4",
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_all(
    database_env_name: str, sql: str, params: Optional[Sequence[Any]] = None
) -> List[Dict[str, Any]]:
    with connect(database_env_name) as conn:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, params or ())
            return list(cursor.fetchall())


def execute_many(
    database_env_name: str, sql: str, rows: Iterable[Sequence[Any]]
) -> int:
    with connect(database_env_name) as conn:
        with conn.cursor() as cursor:
            affected = cursor.executemany(sql, list(rows))
            return int(affected or 0)


def execute_one(
    database_env_name: str, sql: str, params: Optional[Sequence[Any]] = None
) -> int:
    with connect(database_env_name) as conn:
        with conn.cursor() as cursor:
            affected = cursor.execute(sql, params or ())
            return int(affected or 0)


if __name__ == "__main__":
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
            SELECT 
                mp_id, title, description, 
                FROM_UNIXTIME(publish_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS publish_time, 
                url
            FROM articles
            WHERE publish_time > UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 7 DAY))
        ) a
    LEFT JOIN feeds f ON a.mp_id = f.id
    ORDER BY a.publish_time ASC
    LIMIT 1
    """

    # 2. 函数调用变得非常清爽
    articles = fetch_all(
        database_env_name="ALI22_MYSQL_DATABASE_WECHATRSS_NAME", sql=SQL_QUERY
    )
    print(articles)
    print(articles[0].keys())
    for key in articles[0].keys():
        print(key)
