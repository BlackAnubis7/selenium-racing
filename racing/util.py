import re
import os
import platform

_RGB_REGEX = r'^rgba?\((?<r>\d+),? (?<g>\d+),? (?<b>\d+),?.*$'


def time_to_ms(hms: str) -> int:
    hms = hms.strip()
    major = hms.split(':')
    minor = major[-1].split('.')
    ms: int = 1000 * int(minor[0])
    if len(minor) >= 2:
        ms += int(minor[1])
    if len(major) >= 2:
        ms += 60_000 * int(major[-2])
        if len(major) >= 3:
            ms += 3_600_000 * int(major[-3])
    return ms


def __expand_to_digits(x: int, digits: int) -> str:
    return str(1_000_000 + x)[-digits:]


def ms_to_time(ms: int, force_show_ms: bool = False, force_sign: bool = False, sign_multiplier: int = 1) -> str:
    original_sign = ms
    if ms == 0:
        return '0'
    elif ms < 0:
        ms = -ms
    millis = ms % 1000
    ms //= 1000
    secs = ms % 60
    ms //= 60
    mins = ms % 60
    ms //= 60
    hrs = ms
    ret = ''
    if millis != 0 or force_show_ms:
        ret = f'.{__expand_to_digits(millis, 3)}'
    ret = f'{__expand_to_digits(secs, 2)}{ret}'
    if hrs == 0:
        ret = f'{__expand_to_digits(mins, 1)}:{ret}'
    else:
        ret = f'{__expand_to_digits(mins, 2)}:{ret}'
        ret = f'{hrs}:{ret}'

    if original_sign < 0:
        return f'{"-" * sign_multiplier}{ret}'
    elif force_sign:
        return f'{"+" * sign_multiplier}{ret}'
    return ret


def colour_hash(col: str) -> int:
    if col.startswith('rgb'):
        rgb = re.search(_RGB_REGEX, col)
        ret = 0
        ret += int(rgb.group('r') * 0x10000)
        ret += int(rgb.group('g') * 0x100)
        ret += int(rgb.group('b') * 0x1)
        return ret
    elif col.startswith('#'):
        return int(col[1:7], 16)
    else:
        raise ValueError(f'Unsupported colour format: "{col}"')


def first(t: tuple):
    if len(t) > 0:
        return t[0]
    else:
        raise IndexError('Cannot extract first element from an empty tuple')


def signed(x: int, sign_multiplier: int = 1) -> str:
    if x > 0:
        return f'{"+" * sign_multiplier}{x}'
    elif x < 0:
        return f'{"-" * sign_multiplier}{-x}'
    else:  # x == 0
        return '0'


def clear_terminal():
    # Check the operating system
    current_os = platform.system()
    if current_os == "Windows":
        os.system('cls')  # Clear the terminal on Windows
    else:
        os.system('clear')  # Clear the terminal on Unix/Linux/MacOS


def __test_time_to_ms():
    examples = {
        '12': 12_000,
        '12.345': 12_345,
        '12:34': 754_000,
        '12:34.567': 754_567,
        '12:34:56': 45_296_000,
        '12:34:56.789': 45_296_789,
    }
    ok = True
    for e in examples:
        if time_to_ms(e) != examples[e]:
            print(f'{e} should be {examples[e]}, was {time_to_ms(e)}')
            ok = False
    if ok:
        print('Everything ok')


# __test_time_to_ms()

