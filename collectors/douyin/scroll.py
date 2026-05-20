import time
import random

def scroll_page(page, max_scroll=15):
    for i in range(max_scroll):
        page.mouse.wheel(0, random.randint(2000, 4000))

        sleep_time = random.uniform(1.0, 2.5)
        time.sleep(sleep_time)

        # 可加：检测是否还有新内容（进阶）
        # if not page.locator("xxx").is_visible():
        #     break