from datetime import datetime
from typing import Optional, Tuple, Union

from storage.crud.we_mp_rss_articles import (
    sync_we_mp_rss_articles_to_wechat_rss as _sync_we_mp_rss_articles_to_wechat_rss,
)
from storage.crud.wechat_rss import (
    create_wechat_rss as _create_wechat_rss,
    delete_wechat_rss as _delete_wechat_rss,
    get_wechat_rss_by_id as _get_wechat_rss_by_id,
    get_wechat_rss_by_link as _get_wechat_rss_by_link,
    list_wechat_rss as _list_wechat_rss,
    update_wechat_rss as _update_wechat_rss,
)
from storage.database import (
    Base,
    SessionLocal,
    WechatRssSessionLocal,
    engine,
    get_db,
    get_wechat_rss_db,
    init_db,
    session_scope,
    wechat_rss_engine,
    wechat_rss_session_scope,
)
from storage.models import WechatRss, WechatRssSourceArticle

def create_wechat_rss(
    *,
    link: Optional[str] = None,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    content: Optional[str] = None,
    published: Optional[datetime] = None,
    created: Optional[datetime] = None,
) -> WechatRss:
    with session_scope() as db:
        return _create_wechat_rss(
            db,
            link=link,
            title=title,
            summary=summary,
            content=content,
            published=published,
            created=created,
        )


def get_wechat_rss_by_id(rss_id: int) -> Optional[WechatRss]:
    with session_scope() as db:
        return _get_wechat_rss_by_id(db, rss_id)


def get_wechat_rss_by_link(link: str) -> Optional[WechatRss]:
    with session_scope() as db:
        return _get_wechat_rss_by_link(db, link)


def list_wechat_rss(limit: int = 50, offset: int = 0, title_contains: Optional[str] = None):
    with session_scope() as db:
        return _list_wechat_rss(db, limit=limit, offset=offset, title_contains=title_contains)


def update_wechat_rss(
    rss_id: int,
    *,
    link: Optional[str] = None,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    content: Optional[str] = None,
    published: Optional[datetime] = None,
    created: Optional[datetime] = None,
) -> Optional[WechatRss]:
    with session_scope() as db:
        return _update_wechat_rss(
            db,
            rss_id,
            link=link,
            title=title,
            summary=summary,
            content=content,
            published=published,
            created=created,
        )


def delete_wechat_rss(rss_id: int) -> bool:
    with session_scope() as db:
        return _delete_wechat_rss(db, rss_id)


def sync_we_mp_rss_articles_to_wechat_rss(
    *,
    batch_size: int = 200,
    publish_time_gt: Optional[Union[int, str, datetime]] = None,
    force_overwrite: bool = False,
) -> Tuple[int, Optional[int]]:
    with wechat_rss_session_scope() as source_db:
        with session_scope() as target_db:
            return _sync_we_mp_rss_articles_to_wechat_rss(
                source_db,
                target_db,
                batch_size=batch_size,
                publish_time_gt=publish_time_gt,
                force_overwrite=force_overwrite,
            )


__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "wechat_rss_engine",
    "WechatRssSessionLocal",
    "WechatRss",
    "WechatRssSourceArticle",
    "init_db",
    "get_db",
    "session_scope",
    "get_wechat_rss_db",
    "wechat_rss_session_scope",
    "create_wechat_rss",
    "get_wechat_rss_by_id",
    "get_wechat_rss_by_link",
    "list_wechat_rss",
    "update_wechat_rss",
    "delete_wechat_rss",
    "sync_we_mp_rss_articles_to_wechat_rss",
]


if __name__ == "__main__":
    init_db()
