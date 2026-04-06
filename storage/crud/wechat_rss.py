from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from storage.models import WechatRss


def create_wechat_rss(
    db: Session,
    *,
    link: Optional[str] = None,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    content: Optional[str] = None,
    published: Optional[datetime] = None,
    created: Optional[datetime] = None,
) -> WechatRss:
    row = WechatRss(
        link=link,
        title=title,
        summary=summary,
        content=content,
        published=published,
        created=created,
    )
    db.add(row)
    db.flush()
    db.refresh(row)
    return row


def get_wechat_rss_by_id(db: Session, rss_id: int) -> Optional[WechatRss]:
    return db.get(WechatRss, rss_id)


def get_wechat_rss_by_link(db: Session, link: str) -> Optional[WechatRss]:
    stmt = select(WechatRss).where(WechatRss.link == link).order_by(WechatRss.id.desc()).limit(1)
    return db.scalars(stmt).first()


def list_wechat_rss(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
    title_contains: Optional[str] = None,
) -> List[WechatRss]:
    stmt = select(WechatRss).order_by(WechatRss.id.desc()).offset(offset).limit(limit)
    if title_contains:
        stmt = stmt.where(WechatRss.title.like(f"%{title_contains}%"))
    return list(db.scalars(stmt).all())


def update_wechat_rss(
    db: Session,
    rss_id: int,
    *,
    link: Optional[str] = None,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    content: Optional[str] = None,
    published: Optional[datetime] = None,
    created: Optional[datetime] = None,
) -> Optional[WechatRss]:
    row = db.get(WechatRss, rss_id)
    if row is None:
        return None
    if link is not None:
        row.link = link
    if title is not None:
        row.title = title
    if summary is not None:
        row.summary = summary
    if content is not None:
        row.content = content
    if published is not None:
        row.published = published
    if created is not None:
        row.created = created
    db.flush()
    db.refresh(row)
    return row


def delete_wechat_rss(db: Session, rss_id: int) -> bool:
    row = db.get(WechatRss, rss_id)
    if row is None:
        return False
    db.delete(row)
    return True


def exists_wechat_rss(
    db: Session,
    *,
    link: Optional[str] = None,
    title: Optional[str] = None,
) -> bool:
    conditions = []
    if link is not None:
        conditions.append(WechatRss.link == link)
    if title is not None:
        conditions.append(WechatRss.title == title)
    if not conditions:
        raise ValueError("At least one of link/title must be provided")
    stmt = select(WechatRss.id).where(and_(*conditions)).limit(1)
    return db.execute(stmt).first() is not None
