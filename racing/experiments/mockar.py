from racing.car import Car
from racing.track import Track
from racing.webdriver import WebDriver


class MockCar:
    def __init__(self, number, name, car, category, place, last, best, laps, micro_sector):
        self.full_name = f'{number} {name}'
        self.number, self.name = number, car
        self.car = category
        self.category = category
        self.place = place
        self.last = last
        self.best = best
        self.laps = laps
        self.micro_sector = micro_sector

    def update_times(self):
        pass

    def update_micro_sector(self, web: WebDriver, track: Track):
        pass

    def on_track(self):
        return self.micro_sector > 0

    def absolute_micro_sector(self, track: Track) -> int:
        non_neg = self.micro_sector
        if non_neg < 0:
            non_neg = 0
        return self.laps * track.micro_sectors + non_neg
