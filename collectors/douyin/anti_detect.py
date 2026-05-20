import random
import time


# 反爬措施：随机 sleep
def random_sleep(a=1, b=3):
    time.sleep(random.uniform(a, b))

# 反爬措施：鼠标移动轨迹、viewport 随机
def random_mouse_move(page):
    x = random.randint(100, 800)
    # # 随机设置视口大小
    # viewport_size = {
    #     "width": random.randint(1024, 1920),
    #     "height": random.randint(768, 1080)
    # }
    # page.set_viewport_size(viewport_size)
    
    y = random.randint(100, 600)
    page.mouse.move(x, y)
    random_sleep()

