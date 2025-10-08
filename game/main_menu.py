import sys
from .engine import GameEngine
from .saveio import SaveIO

BANNER = r"""
   ____      _     _   _   _               _             
  / ___|___ | | __| | | | | | ___  _ __ __| | ___  _ __  
 | |   / _ \| |/ _` | | |_| |/ _ \| '__/ _` |/ _ \| '_ \ 
 | |__| (_) | | (_| | |  _  | (_) | | | (_| | (_) | | | |
  \____\___/|_|\__,_| |_| |_|\___/|_|  \__,_|\___/|_| |_|
                 Text Edition  —  First-person survival
"""

def main_menu():
    io = SaveIO()
    while True:
        print(BANNER)
        print("[N] New Game   [L] Load Game   [Q] Quit")
        choice = input("> ").strip().lower()
        if choice in ("n", "new"):
            engine = GameEngine()
            engine.start_new()
            engine.loop()
        elif choice in ("l", "load"):
            data = io.load_latest()
            if data:
                engine = GameEngine()
                engine.load_from(data)
                engine.loop()
            else:
                print("No save found.")
        elif choice in ("q", "quit", "exit"):
            sys.exit(0)
        else:
            print("Not a menu option. Try N/L/Q.")
