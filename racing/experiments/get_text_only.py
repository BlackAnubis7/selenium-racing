from racing.css import *
from webdriver import init_driver
import os

URL = f'file:///{os.getcwd()}/../../sample/crl.htm'
CSS = '#live-table-disconnected tbody tr.driver-row td.driver-name'

web = init_driver(URL)
input()

eclipse = web.find_elements(By.CSS_SELECTOR, CSS)[0]
text = eclipse.text.split('\n')[0]
print(eclipse.value_of_css_property('display'))

web.quit()
