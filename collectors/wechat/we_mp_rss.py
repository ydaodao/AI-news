from time import sleep

from loguru import logger
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

from utils.playwright_utils import human_click, open_page

CDP_URL = "http://127.0.0.1:9222"
LOGIN_URL = "https://wechat-rss.daodao10y.top/login"
MAX_ATTEMPTS = 2
RETRY_WAIT_SECONDS = 120 * 60
ACTION_TIMEOUT_MS = 30_000
SUCCESS_WAIT_MS = 8_000


def close_page_safely(page: Page | None) -> None:
    if not page:
        return
    try:
        page.close()
    except Exception:
        logger.exception("关闭页面失败")


def click_once_or_raise(
    page: Page,
    locator: Locator,
    step_name: str
) -> None:

    try:
        logger.info(f"{step_name}，开始执行")
        human_click(locator.first)

        logger.info(f"{step_name} 成功")
    except PlaywrightTimeoutError as e:
        logger.warning(f"{step_name} 超时，本轮结束并等待下一次整体重试: {e}")
        raise
    except Exception as e:
        logger.warning(f"{step_name} 失败，本轮结束并等待下一次整体重试: {e}")
        raise


def run_once(page: Page) -> None:
    page.set_default_timeout(ACTION_TIMEOUT_MS)
    page.set_default_navigation_timeout(ACTION_TIMEOUT_MS)
    page.bring_to_front()

    login_btn = page.locator("button").filter(has_text=" 登录 ")
    click_once_or_raise(page, login_btn, "点击登录")

    send_msg_tab = page.locator("span").filter(has_text="消息任务")
    click_once_or_raise(page, send_msg_tab, "打开消息任务")
    
    send_msg_action = page.locator("button").filter(has_text="执行")
    click_once_or_raise(page, send_msg_action, "点击执行")

    send_msg_confirm = page.locator("button").filter(has_text="确认")
    click_once_or_raise(page, send_msg_confirm, "点击确认")



def begin_crawler(max_attempts: int = MAX_ATTEMPTS, retry_wait_seconds: int = RETRY_WAIT_SECONDS):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0] if browser.contexts else browser.new_context()

        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            page = None
            try:
                logger.info(f"开始第 {attempt}/{max_attempts} 次整体尝试")
                page = open_page(context, LOGIN_URL, retries=0)
                run_once(page)
                logger.info("消息任务执行流程完成")
                return
            except Exception as e:
                last_error = e
                logger.exception(f"第 {attempt}/{max_attempts} 次整体尝试失败")
            finally:
                close_page_safely(page)

            if attempt < max_attempts:
                logger.warning(f"等待 {retry_wait_seconds} 秒后重新尝试")
                sleep(retry_wait_seconds)

        assert last_error is not None
        raise last_error

if __name__ == "__main__":
    begin_crawler()
