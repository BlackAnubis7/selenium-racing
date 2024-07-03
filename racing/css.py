from math import floor

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

import util
from track import Track

_TABLE_CSS = 'table#live-table > tbody > tr.driver-row'


def extract_rows(web: WebDriver) -> list[WebElement]:
    return web.find_elements(By.CSS_SELECTOR, _TABLE_CSS)


def extract_map(web: WebDriver) -> WebElement:
    return web.find_element(By.ID, 'map')


def row_to_car_data(row: WebElement) -> dict:
    return {
        'driver': row.find_element(By.CLASS_NAME, 'driver-link').text.split('\n')[0],
        'car': row.find_element(By.CLASS_NAME, 'driver-car').text,
    }


def __first_segment_or_none(element: WebElement, class_name: str) -> str | None:
    try:
        return element.find_element(By.CLASS_NAME, class_name).text.split()[0]
    except IndexError:
        return None


def row_to_car_timing(row: WebElement) -> dict:
    return {
        'last': __first_segment_or_none(row, 'last-lap'),
        'best': __first_segment_or_none(row, 'best-lap'),
        'place': __first_segment_or_none(row, 'driver-pos'),
        'laps': __first_segment_or_none(row, 'num-laps'),
    }


def find_my_dot(web: WebDriver, row: WebElement) -> WebElement | None:
    all_dots = extract_map(web).find_elements(By.CLASS_NAME, 'dot')
    button = row.find_element(By.CLASS_NAME, 'driver-link')
    states = {}
    for dot in all_dots:
        states[dot] = dot.find_element(By.CLASS_NAME, 'info').value_of_css_property('display')
    button.click()
    ret = None
    for dot in all_dots:
        if states[dot] != dot.find_element(By.CLASS_NAME, 'info').value_of_css_property('display'):
            if ret is None:
                ret = dot
            else:
                return None  # two changed, we have no way of knowing which is the correct one
    button.click()
    return ret


def get_scaled_position(web: WebDriver, dot: WebElement, track: Track) -> tuple:
    img = web.find_element(By.ID, 'trackMapImage')
    w = int(img.get_attribute('width')) * track.map_corrections['x_slope']
    h = int(img.get_attribute('height')) * track.map_corrections['y_slope']
    top = float(dot.value_of_css_property('top')[:-2])
    left = float(dot.value_of_css_property('left')[:-2])

    grid_scale = track.base_div / max(w, h)  # grid squares per pixel (usually less than one)
    image_scale = w / track.map_corrections['intercept_measurement_width']
    top_corrected = top * track.map_corrections['y_slope'] + (track.map_corrections['y_intercept'] * image_scale) + 5  # half of the dot's height
    left_corrected = left * track.map_corrections['x_slope'] + (track.map_corrections['x_intercept'] * image_scale) + 5  # half of the dot's width

    top_scaled = floor(grid_scale * top_corrected)
    left_scaled = floor(grid_scale * left_corrected)
    return left_scaled, top_scaled


def race_time_hms(web: WebDriver) -> str:
    return web.find_element(By.ID, 'race-time').text


def race_time_ms(web: WebDriver) -> int:
    clock = race_time_hms(web)
    try:
        return util.time_to_ms(clock)
    except ValueError:
        return -1
