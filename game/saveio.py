import json
from pathlib import Path

SAVE_DIR = Path(__file__).resolve().parent.parent / "saves"
SAVE_DIR.mkdir(parents=True, exist_ok=True)
SAVE_FILE = SAVE_DIR / "latest.json"

class SaveIO:
    def save_latest(self, snapshot: dict):
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
        print(f"Saved → {SAVE_FILE}")

    def load_latest(self):
        if not SAVE_FILE.exists():
            return None
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
