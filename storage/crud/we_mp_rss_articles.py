import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from storage.models import WechatRss, WechatRssSourceArticle


def list_source_articles_by_publish_time(
    db: Session,
    *,
    publish_time_gt: Optional[int] = None,
    limit: int = 200,
) -> List[WechatRssSourceArticle]:
    stmt: Select = (
        select(WechatRssSourceArticle)
        .where(WechatRssSourceArticle.publish_time.is_not(None))
        .order_by(WechatRssSourceArticle.publish_time.asc())
        .limit(limit)
    )
    if publish_time_gt is not None:
        stmt = stmt.where(WechatRssSourceArticle.publish_time > publish_time_gt)
    return list(db.scalars(stmt).all())


def _to_datetime_from_unix_seconds(value: Optional[int]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc).replace(tzinfo=None)
    except Exception:
        return None


def _parse_publish_time_gt(value: Optional[Union[int, str, datetime]]) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return int(value.timestamp())
        return int(time.mktime(value.timetuple()))
    if isinstance(value, str):
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(dt.timetuple()))
    raise TypeError("publish_time_gt must be int, datetime, str, or None")


def _existing_rows_by_link(db: Session, links: List[str]) -> Dict[str, WechatRss]:
    if not links:
        return {}
    stmt = select(WechatRss).where(WechatRss.link.in_(links))
    rows = list(db.scalars(stmt).all())
    by_link: Dict[str, WechatRss] = {}
    for row in rows:
        if row.link and row.link not in by_link:
            by_link[row.link] = row
    return by_link


def sync_we_mp_rss_articles_to_wechat_rss(
    source_db: Session,
    target_db: Session,
    *,
    batch_size: int = 200,
    publish_time_gt: Optional[Union[int, str, datetime]] = None,
    force_overwrite: bool = False,
) -> Tuple[int, Optional[int]]:
    publish_time_gt_seconds = _parse_publish_time_gt(publish_time_gt)
    rows = list_source_articles_by_publish_time(
        source_db,
        publish_time_gt=publish_time_gt_seconds,
        limit=batch_size,
    )
    if not rows:
        return 0, None

    links = []
    for r in rows:
        if r.url:
            links.append(r.url)
    existing_by_link = _existing_rows_by_link(target_db, links)

    inserted = 0
    updated = 0
    max_publish_time: Optional[int] = publish_time_gt_seconds
    for r in rows:
        if r.publish_time is not None:
            max_publish_time = max(max_publish_time or r.publish_time, r.publish_time)

        link = r.url
        existing_row = existing_by_link.get(link) if link else None
        if existing_row is not None:
            if not force_overwrite:
                continue
            published_dt = _to_datetime_from_unix_seconds(r.publish_time)
            existing_row.title = r.title
            existing_row.summary = r.description
            existing_row.published = published_dt
            if existing_row.created is None:
                existing_row.created = r.created_at or published_dt
            updated += 1
            continue

        published_dt = _to_datetime_from_unix_seconds(r.publish_time)
        summary = r.description
        title = r.title

        target_db.add(
            WechatRss(
                link=link,
                title=title,
                summary=summary,
                published=published_dt,
                created=r.created_at or published_dt,
            )
        )
        inserted += 1

    target_db.flush()
    return inserted + updated, max_publish_time
