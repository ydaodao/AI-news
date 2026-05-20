from datetime import datetime, timedelta
from typing import Optional, Tuple, Union
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from storage.mysql import sync_we_mp_rss_articles_to_wechat_rss


def sync_window(
    days: int,
    *,
    batch_size: int = 200,
    max_loops: int = 200,
    force_overwrite: bool = False,
) -> Tuple[int, Optional[int]]:
    cutoff = datetime.now() - timedelta(days=days)
    publish_time_gt: Optional[Union[int, str, datetime]] = cutoff.strftime("%Y-%m-%d %H:%M:%S")

    total_inserted = 0
    cursor: Optional[int] = None
    for _ in range(max_loops):
        inserted, next_cursor = sync_we_mp_rss_articles_to_wechat_rss(
            batch_size=batch_size,
            publish_time_gt=publish_time_gt,
            force_overwrite=force_overwrite,
        )
        total_inserted += inserted
        if next_cursor is None:
            cursor = None
            break
        if cursor == next_cursor:
            break
        cursor = next_cursor
        publish_time_gt = next_cursor

        if inserted == 0 and next_cursor is None:
            break
    return total_inserted, cursor


def main() -> None:
    for days in (1, 3, 7):
        inserted, cursor = sync_window(days=days, batch_size=200, max_loops=200, force_overwrite=False)
        print(f"days={days} inserted={inserted} next_cursor={cursor}")


if __name__ == "__main__":
    # main()
    days = 7
    inserted, cursor = sync_window(days=days, batch_size=200, max_loops=200, force_overwrite=False)
    print(f"days={days} inserted={inserted} next_cursor={cursor}")

