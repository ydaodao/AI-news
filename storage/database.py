import os
from contextlib import contextmanager
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

def _build_database_url(database: str) -> str:
    host = os.getenv("ALI22_MYSQL_DATABASE_URL", "")
    port = os.getenv("ALI22_MYSQL_DATABASE_PORT", "3306")
    user = os.getenv("ALI22_MYSQL_DATABASE_USER", "")
    password = quote_plus(os.getenv("ALI22_MYSQL_DATABASE_PASSWORD", ""))
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


MAIN_DATABASE_NAME = os.getenv("ALI22_MYSQL_DATABASE_NAME", "")
WECHATRSS_DATABASE_NAME = os.getenv("ALI22_MYSQL_DATABASE_WECHATRSS_NAME", "")

DATABASE_URL = _build_database_url(MAIN_DATABASE_NAME)
WECHATRSS_DATABASE_URL = _build_database_url(WECHATRSS_DATABASE_NAME)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

wechat_rss_engine = create_engine(WECHATRSS_DATABASE_URL, echo=False, pool_pre_ping=True)
WechatRssSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=wechat_rss_engine)
WechatRssBase = declarative_base()


def init_db() -> None:
    import storage.models

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_wechat_rss_db():
    db = WechatRssSessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def wechat_rss_session_scope():
    db = WechatRssSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
