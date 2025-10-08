import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class Crafting:
    def __init__(self):
        with open(DATA_DIR / "recipes.json","r",encoding="utf-8") as f:
            self.recipes = json.load(f)

    def list_recipes(self):
        return sorted(self.recipes.keys())

    def can_craft(self, inv: dict, name: str, qty: int=1) -> bool:
        if name not in self.recipes: return False
        need = self.multiplied(self.recipes[name]["cost"], qty)
        return all(inv.get(k,0) >= v for k,v in need.items())

    def craft(self, inv: dict, name: str, qty: int=1) -> bool:
        if not self.can_craft(inv, name, qty): return False
        cost = self.multiplied(self.recipes[name]["cost"], qty)
        for k,v in cost.items():
            inv[k] -= v
            if inv[k]<=0: inv.pop(k, None)
        out = self.multiplied(self.recipes[name]["gives"], qty)
        for k,v in out.items():
            inv[k] = inv.get(k,0) + v
        return True

    @staticmethod
    def multiplied(d: dict, n: int) -> dict:
        return {k: v*n for k,v in d.items()}
