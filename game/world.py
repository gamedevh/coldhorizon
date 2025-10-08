import random
from dataclasses import dataclass
from typing import Dict, Tuple, List
from .entities import ResourceNode, Container, Wildlife
from .timeweather import biome_for

Vec3 = Tuple[int, int, int]  # (x,y,z)

@dataclass
class Chunk:
    pos: Tuple[int, int]  # (cx, cz)
    resources: List[ResourceNode]
    containers: List[Container]
    wildlife: List[Wildlife]
    biome: str = "temperate"

    def to_dict(self):
        return {
            "pos": self.pos,
            "biome": self.biome,
            "resources": [r.to_dict() for r in self.resources],
            "containers": [c.to_dict() for c in self.containers],
            "wildlife": [w.to_dict() for w in self.wildlife]
        }

    @staticmethod
    def from_dict(d: dict) -> "Chunk":
        return Chunk(
            pos=tuple(d["pos"]),
            biome=d["biome"],
            resources=[ResourceNode.from_dict(x) for x in d["resources"]],
            containers=[Container.from_dict(x) for x in d["containers"]],
            wildlife=[Wildlife.from_dict(x) for x in d["wildlife"]],
        )

class World:
    def __init__(self, seed=0):
        self.seed = seed
        self.rng = random.Random(seed)
        self.chunks: Dict[Tuple[int,int], Chunk] = {}

    def bootstrap(self):
        # Pre-populate some chunks around origin
        for cx in range(-1, 2):
            for cz in range(-1, 2):
                self._ensure_chunk(cx, cz)

    def _ensure_chunk(self, cx: int, cz: int):
        key = (cx, cz)
        if key in self.chunks:
            return self.chunks[key]
        biome = biome_for(cx, cz)
        resources = []
        containers = []
        wildlife = []
        # Sprinkle resources
        for _ in range(self.rng.randint(3,6)):
            kind = self.rng.choice(["tree","rock","ore"])
            resources.append(ResourceNode.spawn_random(kind, cx, cz, self.rng))
        # A few containers
        for _ in range(self.rng.randint(1,3)):
            containers.append(Container.spawn_random(cx, cz, self.rng))
        # Some wildlife
        for _ in range(self.rng.randint(1,3)):
            wildlife.append(Wildlife.spawn_random(cx, cz, self.rng))
        ch = Chunk(pos=(cx, cz), resources=resources, containers=containers, wildlife=wildlife, biome=biome)
        self.chunks[key] = ch
        return ch

    def chunk_of(self, x: int, z: int) -> Chunk:
        cx, cz = x // 16, z // 16
        return self._ensure_chunk(cx, cz)

    def tick(self, clock, player):
        # Wildlife roam & may aggro (lightweight)
        ppos = player.pos
        for ch in list(self.chunks.values()):
            for w in list(ch.wildlife):
                w.tick(ch, ppos, clock, self.rng)

    def to_dict(self):
        return {
            "seed": self.seed,
            "chunks": {f"{k[0]},{k[1]}": ch.to_dict() for k, ch in self.chunks.items()}
        }

    def from_dict(self, d: dict):
        self.seed = d["seed"]
        self.rng = random.Random(self.seed)
        self.chunks.clear()
        for k, chd in d["chunks"].items():
            cx, cz = map(int, k.split(","))
            self.chunks[(cx,cz)] = Chunk.from_dict(chd)
