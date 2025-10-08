from dataclasses import dataclass

@dataclass
class BasePiece:
    part: str
    x: int; y: int; z: int
    hp: int = 100

class BaseManager:
    def __init__(self):
        self.pieces = []  # list of BasePiece

    def place(self, part: str, x:int,y:int,z:int):
        self.pieces.append(BasePiece(part, x,y,z))
        return True

    def nearby(self, x:int,y:int,z:int, radius:int=2):
        return [p for p in self.pieces if abs(p.x-x)<=radius and abs(p.z-z)<=radius and abs(p.y-y)<=1]

    def to_dict(self):
        return {"pieces":[p.__dict__ for p in self.pieces]}

    def from_dict(self, d: dict):
        self.pieces.clear()
        for p in d.get("pieces",[]):
            self.pieces.append(BasePiece(**p))
