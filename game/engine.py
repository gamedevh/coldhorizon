from .world import World
from .player import Player
from .commands import CommandRouter
from .saveio import SaveIO
from .timeweather import Clock
from .building import BaseManager
from .ui import hint

class GameEngine:
    def __init__(self):
        self.world = World(seed=1337)
        self.player = Player()
        self.clock = Clock()
        self.io = SaveIO()
        self.base = BaseManager()
        self.router = CommandRouter(self)

    def start_new(self):
        self.world.bootstrap()
        self.player.spawn(self.world)
        print("You awaken on a cold shore. The wind bites. You need food, water, and warmth.")

    def load_from(self, data: dict):
        self.world.from_dict(data["world"])
        self.player.from_dict(data["player"])
        self.clock.from_dict(data["clock"])
        self.base.from_dict(data.get("base", {"pieces": []}))
        print("Save loaded. The world feels familiar...")

    def snapshot(self):
        return {
            "world": self.world.to_dict(),
            "player": self.player.to_dict(),
            "clock": self.clock.to_dict(),
            "base": self.base.to_dict()
        }

    def loop(self):
        while True:
            if self.player.is_dead:
                print("You died. (Tip: stay warm, eat, and craft tools.)")
                return
            # Environment tick
            self.clock.tick()
            self.world.tick(self.clock, self.player)
            self.player.tick(self.world, self.clock)
            # Prompt
            cmd = input(f"\n[{self.clock.readable_time()} | {self.player.location_str()} | {self.player.facing}] > ").strip()
            if not cmd:
                hint("Type 'help' for commands.")
                continue
            try:
                done = self.router.handle(cmd)
                if done:  # quit
                    return
            except Exception as e:
                print(f"(!) {e}")
