from racing.css import *
from webdriver import init_driver
import os

URL = f'file:///{os.getcwd()}/../../sample/live_timing.htm'

web = init_driver(URL)
table = extract_rows(web)
dot = table[0].find_element(By.CSS_SELECTOR, 'td.driver-link > div.dot')
col = dot.value_of_css_property('background-color')
print(col)

img = web.find_element(By.ID, 'trackMapImage')
print(img.get_attribute('width'))

input()
img = web.find_element(By.ID, 'trackMapImage')
# after refreshing the page manually we need to take all elements again
# if there is nothing found, a selenium.common.exceptions.NoSuchElementException is raised
# if the referenced object has been removed or page refreshed, selenium.common.exceptions.StaleElementReferenceException
print(img.get_attribute('width'))

web.quit()
