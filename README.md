# Cold Horizon (Text Edition)

A strictly text-based, first-person survival game inspired by Rust, built in Python.

## Features
- First-person position & facing in a simple 3D grid world (x, y, z)
- Biomes, day/night & temperature effects
- Gathering nodes (wood, stone, ore), containers & loot
- Crafting system (recipes), simple building (foundations/walls/doors)
- Hunger, thirst, health, warmth & status effects
- Simple wildlife NPCs that roam and can attack
- Save/Load (JSON), clean modular code
- In-game help (`help`) and suggestions

## Run
```bash
python run.py
```

## Basic Commands
- Movement: `forward`, `back`, `left`, `right`, `up`, `down`, `turn left`, `turn right`
- World: `look`, `scan`, `time`, `where`
- Survival: `stats`, `eat <item>`, `drink <item>`, `rest`
- Inventory: `inv`, `equip <item>`, `drop <item> [qty]`
- Gathering: `gather <target>` (e.g., `gather tree`, `gather rock`)
- Crafting: `recipes`, `craft <recipe> [qty]`
- Building: `build <part>` (foundation, wall, door), `deconstruct`, `base`
- Combat: `attack [target]`
- Misc: `help`, `save`, `load`, `quit`

## Saves
Saves to `saves/latest.json`.
