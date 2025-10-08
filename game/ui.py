def hint(text: str):
    print(f"(hint) {text}")

def print_stats(p):
    s = p.stats
    print(f"Health {s.health} | Hunger {int(s.hunger)} | Thirst {int(s.thirst)} | Warmth {int(s.warmth)}")

def print_inv(p):
    if not p.inventory:
        print("Inventory empty.")
        return
    print("Inventory:")
    for k,v in sorted(p.inventory.items()):
        print(f" - {k} x{v}")
