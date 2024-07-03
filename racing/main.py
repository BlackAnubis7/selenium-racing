from time import sleep
import sys
import css
import util
from car import Car
from experiments.mockar import MockCar
from track import Track
from webdriver import *
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException, NoSuchWindowException

INTERVAL_S = 2
US = 317
URL = 'http://.../live-timing'
# LONG_STOP_MS = 4 * 60_000
LONG_STOP_MS = 30_000  # 30 seconds, for tests
COLOURS = {
    'us': '\033[47;30m',
    'racing': '\033[33m',
    'racing_close': '\033[31m',
    # 'lapping_once': '\033[94m',
    # 'un-lapping_once': '\033[92m',
    # 'lapping_more': '\033[34m',
    # 'un-lapping_more': '\033[32m',
    'lapping_once': '\033[94;1;3m',
    'un-lapping_once': '\033[92;1;3m',
    'lapping_more': '\033[94m',
    'un-lapping_more': '\033[92m',
    'other_class': '\033[95m',
    'default': '\033[0m',
}
RACING_CLOSE_METERS = 500
LOGS_TO_SHOW = 30

if len(sys.argv) <= 1:
    print('Should have one argument - track data folder')
    sys.exit(57)
CONFIG = sys.argv[1]
LOGFILE = open('selenium_racing.log', 'a')

cars: list[Car] = []
last_seen: dict = {}
our_car: Car | None = None
web: WebDriver = init_driver(URL)
track = Track(CONFIG)
logs = ['' for _ in range(LOGS_TO_SHOW)]


# positive if they are in front
def sector_diff(them: Car) -> int:
    a = our_car.micro_sector
    b = them.micro_sector
    half = track.micro_sectors / 2
    if a == b:
        return 0
    elif a < b:
        sig = 1
    else:
        sig = -1
    ud = sig * (b - a)
    if ud > half:  # if after half (excluding equality), use the way via the start
        ud -= track.micro_sectors
    return sig * ud


def print_car(diff_car: tuple):
    diff, car = diff_car
    if our_car is None or car.micro_sector < 0:
        return
    full = track.micro_sectors
    half = full / 2
    absolute_diff = car.absolute_micro_sector(track) - our_car.absolute_micro_sector(track)
    dist = util.signed(track.meters * diff)
    if car == our_car:
        timing_str = ''
        if our_car.best > 0 or our_car.last > 0:
            our_b = util.ms_to_time(our_car.best)
            our_l = util.ms_to_time(our_car.last)
            timing_str = f' (B={our_b}, L={our_l}) '
        print(f'{COLOURS["us"]}    #{our_car.place}: That is us {timing_str}  \033[0m')
    elif abs(diff) < full / 3:  # we don't need to see cars on the other side of the track
        if car.category == 'SC':
            return  # we don't want to render the safety car
        elif our_car.category != car.category:
            col = COLOURS['other_class']
            print(f'{col}[{dist}m] #{car.place}: <{car.category}> {car.full_name}\033[0m')
            return
        elif -half <= absolute_diff <= half:
            if track.meters * abs(diff) <= RACING_CLOSE_METERS:
                col = COLOURS['racing_close']
            else:
                col = COLOURS['racing']
        elif half < absolute_diff <= full + half:
            col = COLOURS['lapping_once']
        elif full + half < absolute_diff:
            col = COLOURS['lapping_more']
        elif -(full + half) <= absolute_diff < -half:
            col = COLOURS['un-lapping_once']
        elif absolute_diff < -(full + half):
            col = COLOURS['un-lapping_more']
        else:
            col = COLOURS['default']

        diff_b = diff_l = ''
        if car.best > 0 and our_car.best > 0:
            diff_b = f'B{util.ms_to_time(car.best - our_car.best, force_show_ms=True, force_sign=True, sign_multiplier=2)}, '
        if car.last > 0 and our_car.last > 0:
            diff_l = f'L{util.ms_to_time(car.last - our_car.last, force_show_ms=True, force_sign=True, sign_multiplier=2)}, '
        if car.laps == our_car.laps:
            lap_diff = 'Same lap'
        else:
            lap_diff = f'LAP{util.signed(car.laps - our_car.laps, sign_multiplier=2)}'

        print(f'{col}[{dist}m] #{car.place}: {car.full_name} | {diff_b}{diff_l}{lap_diff}\033[0m')


def log(message: str):
    global logs
    race_hms = css.race_time_hms(web)
    record = f'[{race_hms}] {message}'
    logs = [record] + logs[:-1]
    LOGFILE.write(f'{message}\n')


def regenerate_stuff():
    global cars
    global our_car
    previous_cars = len(cars)
    rows = css.extract_rows(web)
    cars = []
    # cars = [  # for testing
    #     MockCar(123, 'Bob the Snob', '2008 Honda Civic', 'GT-M', 2, 111111, 109384, 3, 155),
    #     MockCar(987, 'The guy', '2014 Toyota Prius', 'GT-M', 3, 123456, 108357, 2, 17),
    #     MockCar(555, 'Hyper man', 'Lada', 'LMH', 9, 94624, 89624, 6, 211),
    #     MockCar(112, 'Safe man', 'Aston', 'SC', 14, 0, 0, 1, 123),
    #     MockCar(1, 'Pit man', 'Lambodżini', 'GT-M', 12, 0, 0, 1, -0x10),
    # ]
    our_car = None
    for r in rows:
        next_car = Car(web, r)
        if next_car.number == US or next_car.full_name == US:
            our_car = next_car
        cars.append(next_car)
    if previous_cars != len(cars):
        log(f'Refreshed car list - {len(cars)} found')


def destroy():
    LOGFILE.close()
    web.quit()


def acknowledge_car(car: Car, time_ms: int):
    global last_seen
    name = car.full_name
    if name in last_seen:
        if car.on_track() and time_ms >= 0:
            delta = last_seen[name] - time_ms  # it is a countdown, it goes down
            if delta >= LONG_STOP_MS:
                delta_hms = util.ms_to_time(delta)
                log(f'Car "{name}" returned to track after {delta_hms} - probably a long stop')
            last_seen[name] = time_ms
    else:
        log(f'We are seeing car "{name}" for the first time')
        last_seen[name] = -1


def iteration():
    race_time = css.race_time_ms(web)
    # race_hms = util.ms_to_time(race_time)
    # if len(cars) == 0 or our_car is None:
    #     regenerate_stuff()  # if there are no cars, try to find them
    for c in cars:
        c.update_times()
        c.update_micro_sector(web, track)
        acknowledge_car(c, race_time)
        # print(f'{c.name} on micro-sector {c.micro_sector}')
    util.clear_terminal()
    print('\033[0mClose the browser window to exit; refresh to reload data')
    print()
    if our_car is not None:
        grid = sorted([(sector_diff(c), c) for c in cars], key=util.first, reverse=True)
        for g in grid:
            print_car(g)
    print()
    print('--- Latest logs ---')
    for single_log in logs:
        print(single_log)


def loop():
    regenerate_stuff()
    try:
        while True:
            _ = web.window_handles  # raises exception when windows is closed
            try:
                iteration()
                sleep(INTERVAL_S)
            except StaleElementReferenceException:
                regenerate_stuff()
            except BaseException as e:
                if not isinstance(e, KeyboardInterrupt):
                    pass  # we want to avoid having any unexpected crashes while racing
                else:
                    raise KeyboardInterrupt
            # except IndexError as e:
            #     log(str(e))
            # except ValueError as e:
            #     log(str(e))
    except KeyboardInterrupt:
        pass
    except (WebDriverException, NoSuchWindowException):
        print('Window closed. Exiting...')
    finally:
        destroy()


def print_help():
    colour_helps = {
        'us': 'Our car',
        'racing': 'We are racing with them',
        'racing_close': f'Racing, and they are less than {RACING_CLOSE_METERS} meters from us',
        'lapping_once': 'Lapping us once',
        'un-lapping_once': 'They are lapped by us once',
        'lapping_more': 'Lapping us 2+ times',
        'un-lapping_more': 'They are lapped by us 2+ times',
        'other_class': 'They are a different class',
        'default': 'Default colour - probably an error of some kind',
    }
    print('--- Colours ---')
    for c in colour_helps:
        print(f'{COLOURS[c]} >> {colour_helps[c]}\033[0m')
    print('---------------')


print_help()
print('\033[92mENTER when ready (when the webpage loads)\033[0m')
LOGFILE.write('------\n')
input()
loop()
