from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text, text
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.schema import Index

from storage.database import Base, WechatRssBase


class WechatRss(Base):
    __tablename__ = "wechat_rss"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    link = Column(String(500), nullable=True)
    title = Column(String(1000), nullable=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    published = Column(DateTime, nullable=True)
    created = Column(DateTime, nullable=True)
    updated = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )


class WechatRssSourceArticle(WechatRssBase):
    __tablename__ = "articles"

    id = Column(String(255), primary_key=True)
    mp_id = Column(String(255), nullable=True)
    title = Column(String(1000), nullable=True)
    pic_url = Column(String(500), nullable=True)
    url = Column(String(500), nullable=True)
    description = Column(MEDIUMTEXT, nullable=True)
    extinfo = Column(MEDIUMTEXT, nullable=True)
    status = Column(Integer, nullable=True)
    publish_time = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(BigInteger, nullable=True)
    updated_at_millis = Column(BigInteger, nullable=True)
    is_export = Column(Integer, nullable=True)
    is_read = Column(Integer, nullable=True)
    is_favorite = Column(Integer, nullable=True)
    content = Column(MEDIUMTEXT, nullable=True)
    content_html = Column(MEDIUMTEXT, nullable=True)


Index("ix_articles_updated_at_millis", WechatRssSourceArticle.updated_at_millis)
Index("ix_articles_publish_time", WechatRssSourceArticle.publish_time)
