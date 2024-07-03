import css
from track import Track
from util import time_to_ms
from webdriver import *
from selenium.webdriver.remote.webelement import WebElement


def split_driver(driver: str) -> tuple:
    try:
        splat = driver.split(' ', 1)
        number = int(splat[0])
        name = splat[1]
        return number, name
    except (ValueError, IndexError):
        return 0, driver


# hardcoded, because I don't care; can be adjusted accordingly to needs
def get_category(car: str) -> str:
    if 'GT' in car:
        return 'GT-M'
    elif 'Moyoda' in car:
        return 'LMH'
    elif 'Loire' in car:
        return 'LMP2'
    elif 'Aston' in car:
        return 'SC'
    else:
        return '?'


class Car:
    def __init__(self, web: WebDriver, row: WebElement):
        elems = css.row_to_car_data(row)
        driver = elems['driver']
        car = elems['car']
        self.row: WebElement = row
        self.dot: WebElement | None = css.find_my_dot(web, self.row)
        self.full_name = driver
        self.number, self.name = split_driver(driver)
        self.car = car
        self.category = get_category(car)
        self.place: int = 0
        self.last: int = 0
        self.best: int = 0
        self.laps: int = 0
        self.micro_sector: int = -1

    def update_times(self):
        elems = css.row_to_car_timing(self.row)
        if elems['place'] is not None:
            self.place = int(elems['place'])
        if elems['last'] is not None:
            self.last = time_to_ms(elems['last'])
        if elems['best'] is not None:
            self.best = time_to_ms(elems['best'])
        if elems['laps'] is not None:
            self.laps = int(elems['laps'])

    def update_micro_sector(self, web: WebDriver, track: Track):
        if self.dot is None:
            self.dot = css.find_my_dot(web, self.row)  # we try to find the dot again
            if self.dot is None:  # ...but we fail again - set position as unknown
                self.micro_sector = -1
                return
        try:
            x, y = css.get_scaled_position(web, self.dot, track)
            x = max(0, min(track.x_div, x))  # cap to track bounds
            y = max(0, min(track.y_div, y))
            sector = track.mappings[x][y]
            # print(f'x = {x}, y = {y}, sector {sector}')
            if sector != -1:  # if out of track, do not update
                self.micro_sector = sector
        except (IndexError, ValueError, ZeroDivisionError):
            pass  # do not update sector if dot is not set yet, image is not properly loaded, or we're out of bounds

    def on_track(self):
        return self.micro_sector > 0

    # how many micro-sectors we have driven through from the race start
    def absolute_micro_sector(self, track: Track) -> int:
        non_neg = self.micro_sector
        if non_neg < 0:
            non_neg = 0
        return self.laps * track.micro_sectors + non_neg
