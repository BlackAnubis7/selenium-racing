from math import floor

from webdriver import init_driver
from racing.css import *
import os
from time import sleep

URL = f'http://85.10.193.130:8840/live-timing'
# URL = f'file:///{os.getcwd()}/../../sample/live_timing.htm'

FOUT = f'{os.getcwd()}\\..\\..\\tracks\\daytona\\raw.csv'

MAX_DIVISION = 200  # longer

# snapshot will be taken every X meters on pit limiter speed
INTERVAL_METERS = 20
INTERVAL_SECONDS = INTERVAL_METERS / (80 / 3.6)

web = init_driver(URL)
input('ENTER to continue')

mp = extract_map(web)
img = mp.find_element(By.ID, 'trackMapImage')

w = int(img.get_attribute('width'))
h = int(img.get_attribute('height'))
w_div = min(w / h, 1) * MAX_DIVISION
h_div = min(h / w, 1) * MAX_DIVISION
print(f'Divs - W={w_div}, H={h_div}')
# For Daytona - W=200, H=101.55339805825243

dot = mp.find_element(By.CLASS_NAME, 'dot')
table = extract_rows(web)

lap = 0
point = 0
with open(FOUT, 'x') as csv:
    csv.write(f'point,x,y\n')
    while lap < 2:
        w = int(img.get_attribute('width'))
        h = int(img.get_attribute('height'))
        top = float(dot.value_of_css_property('top')[:-2]) + 5  # half of the dot's height
        left = float(dot.value_of_css_property('left')[:-2]) + 5  # half of the dot's width
        top_pc = floor(h_div * top / h)
        left_pc = floor(w_div * left / w)
        print(f'w={w}px, h={h}px, top={top}px {top_pc}%%, left={left}px {left_pc}%%')
        if lap == 1:
            csv.write(f'{point},{left_pc},{top_pc}\n')
            point += 1
        try:
            sleep(INTERVAL_SECONDS)
        except KeyboardInterrupt:
            break
        lap = int(table[0].find_element(By.CSS_SELECTOR, 'td.num-laps').text)

# sleep(20)
web.quit()
