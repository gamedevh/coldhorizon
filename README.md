# Cold Horizon — Web-Native FPS (No Unity, GitHub Pages Ready)

A **browser-native 3D first-person** mini survival starter built with **Three.js** (via CDN).
No build tools, no Unity. Drop these files into a GitHub repo, enable **GitHub Pages**, and play.

## Quick start (local)
- Open `index.html` directly in a local server (needed for module/CORS):
  ```bash
  python -m http.server 8000
  # then visit http://localhost:8000
  ```

## Deploy on GitHub Pages (no build step)
1. Create a new GitHub repo and add all files from this folder.
2. **Option A (simplest)**: Settings → Pages → Build and Deployment → **Deploy from a branch** → Branch: `main` → Folder: `/ (root)`.
3. **Option B (Actions)**: Leave Pages set to "GitHub Actions" and keep `.github/workflows/deploy.yml`. It uploads the site on every push to `main`.

Then visit your Pages URL to play.

## Controls
- Click the game to lock the mouse (pointer lock).
- **WASD** move, **Space** jump, **Shift** sprint, **E** interact/gather
- **Tab** toggle inventory/crafting, **Esc** unlock mouse

## Features
- True first-person mouselook + WASD, gravity/jump, sprint
- Flat world with scattered resource nodes (Tree/Rock/Ore)
- Harvesting with raycast, floating hit text
- Minimal inventory + crafting (hatchet/pickaxe/spear/tea)
- Day/night cycle with ambient / sun changes
- HUD overlay (crosshair, messages, inventory panel)
- Pure static site; works on GitHub Pages

MIT licensed. Use this as a base for your Rust-like browser game.
