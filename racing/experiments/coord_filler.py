import os


def x8(_center: tuple, _delta: tuple) -> list[tuple]:
    cx, cy = _center
    dx, dy = _delta
    as_set = {
        (cx+dx, cy+dy),
        (cx-dx, cy+dy),
        (cx+dx, cy-dy),
        (cx-dx, cy-dy),
        (cx+dy, cy+dx),
        (cx-dy, cy+dx),
        (cx+dy, cy-dx),
        (cx-dy, cy-dx)
    }
    return list(as_set)


def spill_level(_center: tuple, _level: int) -> list[tuple]:
    if _level < 1:
        return [_center, ]
    dx = dy = 0
    while _level > 0:
        if dy < dx:
            dy += 1
        else:
            dx += 1
            dy = 0
        _level -= 1
    return x8(_center, (dx, dy))


def can_cross_daytona(a: tuple, b: tuple) -> bool:
    if a == b:
        return True  # "no crossing" is always allowed
    ax, ay = a
    bx, by = b
    crosses_finish = ay < 15 and by < 15 and (ax - 101.5) * (bx - 101.5) < 0  # one before finish, one after
    return not crosses_finish


DAYTONA_FREE = {
    'div_x': 201,  # based on real max values in input CSV, not on what we tried to achieve :)
    'div_y': 101,
    'can_cross': can_cross_daytona,
    'max_level': 6,
    'csv_in': f'{os.getcwd()}\\..\\..\\tracks\\daytona_free\\raw.csv',
    'csv_out': f'{os.getcwd()}\\..\\..\\tracks\\daytona_free\\full.csv',
    'interval_meters': 20,
}


DAYTONA_PRO = {
    'div_x': 201,  # based on real max values in input CSV, not on what we tried to achieve :)
    'div_y': 101,
    'can_cross': can_cross_daytona,
    'max_level': 15,
    'csv_in': f'{os.getcwd()}\\..\\..\\tracks\\daytona_pro\\raw.csv',
    'csv_out': f'{os.getcwd()}\\..\\..\\tracks\\daytona_pro\\full.csv',
    'interval_meters': 20,
}

DATASET = DAYTONA_PRO

track = [[-1 for y in range(DATASET['div_y'] + 1)] for x in range(DATASET['div_x'] + 1)]
records = {}
with open(DATASET['csv_in'], 'r') as csv_in:
    for line in csv_in:
        point, x, y = line.strip().split(',')
        try:
            point = int(point)
            x = int(x)
            y = int(y)
            records[point] = (x, y)
        except ValueError:
            print(f'Unable to parse row "{line.strip()}" (ignore if that\'s the header)')
        except IndexError:
            print(f'Row "{line.strip()}" went out of bounds')

for lvl in range(DATASET['max_level'] + 1):
    for rid in sorted(records.keys(), reverse=True):
        center = records[rid]
        spill = spill_level(center, lvl)

        def can_spill(sq: tuple):  # spillage outside the track must be prevented
            in_bounds = 0 <= sq[0] <= DATASET['div_x'] and 0 <= sq[1] <= DATASET['div_y']
            return DATASET['can_cross'](center, sq) and in_bounds

        ltd_spill = filter(can_spill, spill)
        for to_fill in ltd_spill:
            if track[to_fill[0]][to_fill[1]] == -1:
                track[to_fill[0]][to_fill[1]] = rid

with open(DATASET['csv_out'], 'x') as csv_out:
    csv_out.write('x,y,micro_sector\n')
    for x in range(DATASET['div_x'] + 1):
        for y in range(DATASET['div_y'] + 1):
            rid = track[x][y]
            if rid >= 0:
                csv_out.write(f'{x},{y},{rid}\n')
