import json
import os


class Track:
    base_div: int  # aimed divisions on longer track axis (for scaling purposes)
    x_div: int  # real maximum value among X values in full coordinate CSV
    y_div: int  # same as above, just Y
    mappings: list[list[int]]
    micro_sectors: int  # largest micro-sector number
    pit: dict  # minimal rectangle which fits the whole main pit lane
    meters: int  # average distance (in meters) between adjacent micro-sectors
    map_corrections: dict  # linear corrections needed for map image (may gods help you if you need this)

    @staticmethod
    def __between_inclusive(v1: int, v2: int):
        return range(min(v1, v2), max(v1, v2) + 1)

    def __init__(self, config_dir: str):
        print(f'\033[33mLoading track config\033[0m')
        with open(os.path.join(config_dir, 'config.json'), 'r') as f:
            conf = json.load(f)
        print(f'\033[92mConfig for {conf.get("name", "the track")} loaded\033[0m')

        self.base_div = conf['base_div']
        self.x_div = conf['x_div']
        self.y_div = conf['y_div']
        self.micro_sectors = conf['micro_sectors']
        self.pit = conf['pit']
        self.meters = conf['meters']
        self.map_corrections = conf.get('map_corrections', {
            "intercept_measurement_width": 1,
            "x_slope": 1,
            "x_intercept": 0,
            "y_slope": 1,
            "y_intercept": 0,
        })

        print(f'\033[33mLoading micro-sectors\033[0m')
        sqs = [[-1 for y in range(conf['y_div'] + 1)] for x in range(conf['x_div'] + 1)]
        ok = 0
        not_ok = 0
        with open(os.path.join(config_dir, 'full.csv'), 'r') as f:
            for line in f:
                x, y, sector = line.split(',')
                try:
                    sqs[int(x)][int(y)] = int(sector)
                    ok += 1
                except (IndexError, ValueError):
                    not_ok += 1
        xa, xb, ya, yb = self.pit['xa'], self.pit['xb'], self.pit['ya'], self.pit['yb']
        for x in self.__between_inclusive(xa, xb):
            for y in self.__between_inclusive(ya, yb):
                try:
                    if sqs[int(x)][int(y)] == -1:
                        sqs[int(x)][int(y)] = -0x10  # pit
                except IndexError:
                    pass

        print(f'\033[92mMicro-sectors loaded - {ok} ok, {not_ok} failed (don\'t worry if there are few problems)\033[0m')
        self.mappings = sqs
