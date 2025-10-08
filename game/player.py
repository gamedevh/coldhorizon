from dataclasses import dataclass, asdict, field

FACINGS = ["N","E","S","W"]

@dataclass
class Stats:
    health: int = 100
    hunger: float = 50.0
    thirst: float = 50.0
    warmth: float = 50.0

@dataclass
class Player:
    x: int = 0
    y: int = 0
    z: int = 0
    facing: str = "N"
    is_dead: bool = False
    stats: Stats = field(default_factory=Stats)
    inventory: dict = None
    equipped: str = ""

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = {"berry": 2, "water": 1}

    @property
    def pos(self):
        return (self.x, self.y, self.z)

    def location_str(self):
        return f"({self.x},{self.y},{self.z})"

    def spawn(self, world):
        self.x, self.y, self.z = 0, 0, 0
        self.facing = "N"
        self.is_dead = False
        self.stats = Stats()
        self.inventory = {"berry": 2, "water": 1}
        self.equipped = ""

    def move(self, dx, dy, dz):
        self.x += dx; self.y += dy; self.z += dz

    def turn_left(self):
        i = FACINGS.index(self.facing)
        self.facing = FACINGS[(i-1)%4]

    def turn_right(self):
        i = FACINGS.index(self.facing)
        self.facing = FACINGS[(i+1)%4]

    def tick(self, world, clock):
        # Passive needs drain
        self.stats.hunger = max(0.0, self.stats.hunger - 0.05)
        self.stats.thirst = max(0.0, self.stats.thirst - 0.07)
        # Temperature from biome/time
        ch = world.chunk_of(self.x, self.z)
        cold_factor = 0.0
        if ch.biome in ("snow","tundra"):
            cold_factor += 0.15
        if not clock.is_daylight():
            cold_factor += 0.10
        self.stats.warmth = max(0.0, self.stats.warmth - cold_factor)
        # Health effects
        dmg = 0
        if self.stats.thirst == 0: dmg += 1
        if self.stats.hunger == 0: dmg += 1
        if self.stats.warmth < 15: dmg += 1
        if dmg>0:
            self.stats.health -= dmg
        else:
            # slight regen if safe
            if self.stats.hunger>50 and self.stats.thirst>50 and self.stats.warmth>40 and self.stats.health<100:
                self.stats.health += 1
        if self.stats.health <= 0:
            self.is_dead = True

    def add_item(self, name, qty=1):
        self.inventory[name] = self.inventory.get(name, 0) + qty

    def remove_item(self, name, qty=1) -> bool:
        have = self.inventory.get(name, 0)
        if have < qty: return False
        if have == qty: self.inventory.pop(name, None)
        else: self.inventory[name] = have - qty
        return True

    def to_dict(self):
        return {
            "x": self.x, "y": self.y, "z": self.z,
            "facing": self.facing,
            "is_dead": self.is_dead,
            "stats": asdict(self.stats),
            "inventory": dict(self.inventory),
            "equipped": self.equipped
        }

    def from_dict(self, d: dict):
        self.x, self.y, self.z = d["x"], d["y"], d["z"]
        self.facing = d["facing"]
        self.is_dead = d["is_dead"]
        st = d["stats"]
        self.stats = Stats(**st)
        self.inventory = dict(d["inventory"])
        self.equipped = d.get("equipped","")
