import random
import time

def random_sleep(a=1, b=3):
    time.sleep(random.uniform(a, b))

def random_mouse_move(page):
    x = random.randint(100, 800)
    y = random.randint(100, 600)
    page.mouse.move(x, y)
    random_sleep()