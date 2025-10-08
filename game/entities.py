import random
from dataclasses import dataclass, asdict
from typing import Tuple

Vec3 = Tuple[int,int,int]

@dataclass
class ResourceNode:
    kind: str  # tree/rock/ore
    x: int; y: int; z: int
    hp: int

    @staticmethod
    def spawn_random(kind, cx, cz, rng: random.Random) -> "ResourceNode":
        x = cx*16 + rng.randint(0,15)
        z = cz*16 + rng.randint(0,15)
        y = 0
        hp = {"tree": 30, "rock": 40, "ore": 50}[kind]
        return ResourceNode(kind, x,y,z, hp)

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return ResourceNode(**d)

@dataclass
class Container:
    x: int; y: int; z: int
    loot: dict

    @staticmethod
    def spawn_random(cx, cz, rng: random.Random) -> "Container":
        x = cx*16 + rng.randint(0,15)
        z = cz*16 + rng.randint(0,15)
        y = 0
        loot = {}
        if rng.random()<0.6: loot["berry"] = rng.randint(1,3)
        if rng.random()<0.4: loot["water"] = rng.randint(1,2)
        if rng.random()<0.3: loot["scrap"] = rng.randint(1,4)
        return Container(x,y,z,loot)

    def to_dict(self):
        return {"x": self.x, "y": self.y, "z": self.z, "loot": dict(self.loot)}

    @staticmethod
    def from_dict(d):
        return Container(d["x"], d["y"], d["z"], dict(d["loot"]))

@dataclass
class Wildlife:
    species: str   # "boar", "wolf"
    x: int; y: int; z: int
    hp: int
    hostile: bool

    @staticmethod
    def spawn_random(cx, cz, rng: random.Random) -> "Wildlife":
        species = rng.choice(["boar","wolf"])
        x = cx*16 + rng.randint(0,15)
        z = cz*16 + rng.randint(0,15)
        y = 0
        hp = 25 if species=="boar" else 35
        hostile = species=="wolf"
        return Wildlife(species, x,y,z, hp, hostile)

    def tick(self, chunk, player_pos, clock, rng: random.Random):
        # Random walk
        if rng.random()<0.5:
            self.x += rng.choice([-1,0,1])
            self.z += rng.choice([-1,0,1])
        # Prune if dead
        if self.hp<=0:
            try: chunk.wildlife.remove(self)
            except ValueError: pass

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return Wildlife(**d)
