from .ui import hint, print_stats, print_inv
from .crafting import Crafting
from .items import FOOD_VALUES, DRINK_VALUES, BUILD_PARTS
from .combat import attack

class CommandRouter:
    def __init__(self, engine):
        self.eg = engine
        self.craft = Crafting()

    def handle(self, raw: str):
        parts = raw.strip().split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("quit","exit"):
            print("Goodbye.")
            return True

        if cmd in ("help","?"):
            self._help(); return False

        if cmd == "save":
            self.eg.io.save_latest(self.eg.snapshot()); return False

        if cmd == "load":
            data = self.eg.io.load_latest()
            if data: self.eg.load_from(data)
            else: print("No save found.")
            return False

        if cmd in ("stats","status"):
            print_stats(self.eg.player); return False

        if cmd in ("inv","inventory"):
            print_inv(self.eg.player); return False

        if cmd == "where":
            print(f"You are at {self.eg.player.location_str()} facing {self.eg.player.facing}.")
            ch = self.eg.world.chunk_of(self.eg.player.x, self.eg.player.z)
            print(f"Biome: {ch.biome} | Nearby: {len(ch.resources)} resources, {len(ch.containers)} containers, {len(ch.wildlife)} wildlife.")
            return False

        if cmd == "time":
            print(self.eg.clock.readable_time()); return False

        if cmd in ("forward","back","left","right","up","down"):
            self._move(cmd); return False

        if cmd == "turn":
            if not args: print("Use: turn left|right"); return False
            if args[0] == "left": self.eg.player.turn_left()
            elif args[0] == "right": self.eg.player.turn_right()
            else: print("Use: turn left|right")
            return False

        if cmd in ("look","scan"):
            self._look(); return False

        if cmd == "gather":
            self._gather(args); return False

        if cmd == "recipes":
            for r in self.craft.list_recipes():
                print(f" - {r}")
            return False

        if cmd == "craft":
            self._craft(args); return False

        if cmd == "eat":
            self._eat(args); return False

        if cmd == "drink":
            self._drink(args); return False

        if cmd == "equip":
            self._equip(args); return False

        if cmd == "drop":
            self._drop(args); return False

        if cmd == "attack":
            print(attack(self.eg.player, self.eg.world)); return False

        if cmd == "build":
            self._build(args); return False

        if cmd == "base":
            nearby = self.eg.base.nearby(self.eg.player.x, self.eg.player.y, self.eg.player.z)
            if not nearby: print("No base parts nearby.")
            else:
                print("Nearby base pieces:")
                for p in nearby: print(f" - {p.part} at ({p.x},{p.y},{p.z}) HP {p.hp}")
            return False

        if cmd == "deconstruct":
            n = self.eg.base.nearby(self.eg.player.x, self.eg.player.y, self.eg.player.z)
            if n:
                piece = n[0]
                self.eg.base.pieces.remove(piece)
                print(f"Deconstructed {piece.part}.")
            else:
                print("No base piece nearby.")
            return False

        print("Unknown command. Type 'help'.")
        return False

    # --- helpers ---
    def _help(self):
        print("Commands: forward/back/left/right/up/down, turn left/right, look, scan, where, time")
        print("          stats, inv, eat <item>, drink <item>, equip <item>, drop <item> [qty]")
        print("          gather <tree|rock|ore|container>, recipes, craft <name> [qty]")
        print("          build <foundation|wall|door>, base, deconstruct")
        print("          attack, save, load, quit")

    def _move(self, cmd):
        p = self.eg.player
        dx=dz=dy=0
        if cmd=="up": dy=1
        elif cmd=="down": dy=-1
        elif cmd in ("left","right","forward","back"):
            # relative to facing
            fx = {"N":0,"E":1,"S":0,"W":-1}[p.facing]
            fz = {"N":1,"E":0,"S":-1,"W":0}[p.facing]
            if cmd=="forward": dx, dz = fx, fz
            elif cmd=="back": dx, dz = -fx, -fz
            elif cmd=="left": dx, dz = -fz, fx
            elif cmd=="right": dx, dz = fz, -fx
        p.move(dx,dy,dz)
        print(f"You move to {p.location_str()}.")

    def _look(self):
        ch = self.eg.world.chunk_of(self.eg.player.x, self.eg.player.z)
        print(f"You survey the area ({ch.biome}).")
        if ch.resources:
            kinds = {}
            for r in ch.resources:
                kinds[r.kind] = kinds.get(r.kind,0)+1
            print("Resources:", ", ".join(f"{k}×{v}" for k,v in kinds.items()))
        if ch.containers:
            print(f"Containers nearby: {len(ch.containers)}")
        if ch.wildlife:
            print("You notice wildlife:", ", ".join(w.species for w in ch.wildlife))

    def _gather(self, args):
        if not args:
            print("Use: gather <tree|rock|ore|container>")
            return
        target = args[0].lower()
        ch = self.eg.world.chunk_of(self.eg.player.x, self.eg.player.z)
        if target == "container":
            if not ch.containers:
                print("No containers here.")
                return
            c = ch.containers.pop(0)
            for k,v in c.loot.items():
                self.eg.player.add_item(k,v)
            if c.loot:
                print(f"You loot a container: +{', '.join(f'{k} x{v}' for k,v in c.loot.items())}")
            else:
                print("The container was empty.")
            return

        node = next((r for r in ch.resources if r.kind==target), None)
        if not node:
            print(f"No {target} here.")
            return
        tool = self.eg.player.equipped or "rock"
        dmg = {"rock":5, "hatchet":10, "pickaxe":10}.get(tool,5)
        node.hp -= dmg
        if node.hp <= 0:
            ch.resources.remove(node)
            if node.kind=="tree": self.eg.player.add_item("wood", 3)
            elif node.kind=="rock": self.eg.player.add_item("stone", 3)
            else: self.eg.player.add_item("ore", 2)
            print(f"You finish harvesting the {node.kind}. Loot goes into your inventory.")
        else:
            print(f"You hit the {node.kind}. It looks weaker (HP {node.hp}).")

    def _craft(self, args):
        if not args:
            print("Use: craft <recipe> [qty]")
            return
        name = args[0].lower()
        qty = 1
        if len(args)>1:
            try: qty = max(1, int(args[1]))
            except: pass
        if self.craft.craft(self.eg.player.inventory, name, qty):
            print(f"Crafted {name} x{qty}.")
        else:
            print("Cannot craft (missing ingredients or unknown recipe). Try 'recipes'.")

    def _eat(self, args):
        if not args: print("Use: eat <item>"); return
        item = args[0].lower()
        if self.eg.player.remove_item(item, 1):
            vals = FOOD_VALUES.get(item, {"hunger":5,"thirst":0,"warmth":0})
            s = self.eg.player.stats
            s.hunger = min(100, s.hunger + vals["hunger"])
            s.thirst = min(100, s.thirst + vals["thirst"])
            s.warmth = min(100, s.warmth + vals["warmth"])
            print(f"You eat {item}.")
        else:
            print("You don't have that.")

    def _drink(self, args):
        if not args: print("Use: drink <item>"); return
        item = args[0].lower()
        if self.eg.player.remove_item(item, 1):
            vals = DRINK_VALUES.get(item, {"thirst":10,"hunger":0,"warmth":0})
            s = self.eg.player.stats
            s.thirst = min(100, s.thirst + vals["thirst"])
            s.hunger = min(100, s.hunger + vals["hunger"])
            s.warmth = min(100, s.warmth + vals["warmth"])
            print(f"You drink {item}.")
        else:
            print("You don't have that.")

    def _equip(self, args):
        if not args: print("Use: equip <item>"); return
        item = args[0].lower()
        if item not in self.eg.player.inventory:
            print("You don't have that.")
            return
        self.eg.player.equipped = item
        print(f"You equip {item}.")

    def _drop(self, args):
        if not args: print("Use: drop <item> [qty]"); return
        item = args[0].lower()
        qty = 1
        if len(args)>1:
            try: qty = max(1, int(args[1]))
            except: pass
        ok = self.eg.player.remove_item(item, qty)
        if ok: print(f"Dropped {item} x{qty}. (the wind scatters it)")
        else: print("Not enough to drop.")

    def _build(self, args):
        if not args:
            print("Use: build <foundation|wall|door>")
            return
        part = args[0].lower()
        if part not in BUILD_PARTS:
            print("Unknown part.")
            return
        cost = {"foundation":{"wood":4}, "wall":{"wood":2}, "door":{"wood":3}}
        required = cost[part]
        inv = self.eg.player.inventory
        if not all(inv.get(k,0)>=v for k,v in required.items()):
            print("You lack materials.")
            return
        for k,v in required.items():
            inv[k] -= v
            if inv[k]<=0: inv.pop(k,None)
        x,y,z = self.eg.player.x, self.eg.player.y, self.eg.player.z
        self.eg.base.place(part, x, y, z)
        print(f"You place a {part} at your feet.")
