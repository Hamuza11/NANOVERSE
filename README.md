# NANOVERSE 
This project is a top-down sandbox game. The initial version is still very basic, but it would be very kind if you would contribute!

### Current version: Pre-Classic Pre-Dev 1 'Aura'

## Run locally

- Ensure Python 3.10+
- Install requirements:

```bash
pip install -r requirements.txt
```

- Run the game:

```bash
python main.py
```

If running in a headless environment (no display), you can set a dummy video driver:

```bash
SDL_VIDEODRIVER=dummy python main.py
```

## Controls

- WASD/Arrows: Move
- 1-5: Select inventory slot
- Left-click: Place material (consumes the selected item)
- Right-click: Collect material (only if there is free inventory space)
- G: Toggle grid overlay
- ESC: Quit
