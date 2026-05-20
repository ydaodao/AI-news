import random
import time
from utils.playwright_utils import find_element
from collectors.douyin.anti_detect import random_sleep, random_mouse_move

class DouyinAuthorPage:
    def __init__(self, page):
        self.page = page
    
    # 触发接口加载（关键）
    def scroll_page(self):
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        random_sleep()
        self.page.wait_for_timeout(3000)
    
    # # 打开抖音博主的主页
    # def open_user_page(self, url):
    #     self.page.goto(url)
    #     random_sleep()
    #     self.page.wait_for_timeout(3000)
    
    # # 加载已有的page
    # def load_user_page(self, page):
    #     self.page = page
    #     random_sleep()
    #     self.page.wait_for_timeout(3000)
    
    # 获取抖音博主的信息
    def get_user_info(self):
        ele_dy_name = ('抖音号名字', 'div[data-e2e="user-info"] > div:nth-child(1)')
        # ele_dy_name = ('抖音号名称', '#user_detail_element > div > div.a3i9GVfe.nZryJ1oM._6lTeZcQP.y5Tqsaqg > div.IGPVd8vQ > div.HjcJQS1Z > h1 > span > span > span > span > span > span')

        return {
            "dy_name": find_element(self.page, ele_dy_name).inner_text()
        }
    
    # 打开视频并获取详情
    def open_video_and_get_detail(self, card):
        random_sleep()
        card.click()
        self.page.wait_for_timeout(2000)

        # 获取当前 URL（关键）
        random_sleep()
        url = self.page.url

        # 可扩展：标题 / 点赞 / 评论
        title = self.page.locator("xxx").inner_text()

        # 关闭弹窗
        self.page.keyboard.press("Escape")

        return {
            "url": url,
            "title": title
        }
