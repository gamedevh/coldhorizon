def biome_for(cx:int, cz:int) -> str:
    key = (abs(cx)+abs(cz))%4
    return ["temperate","forest","desert","snow"][key]

class Clock:
    def __init__(self):
        self.ticks = 7*60  # start 07:00

    def tick(self):
        self.ticks = (self.ticks + 1) % (24*60)

    def is_daylight(self):
        # daylight 06:00 - 19:59
        h = self.ticks//60
        return 6 <= h < 20

    def readable_time(self):
        h = self.ticks//60
        m = self.ticks%60
        return f"{h:02d}:{m:02d}"

    def to_dict(self):
        return {"ticks": self.ticks}

    def from_dict(self, d):
        self.ticks = d["ticks"]
