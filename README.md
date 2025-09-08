# 3D ASCII Game

A terminal-based 3D renderer that creates a first-person view using ASCII characters and raycasting.

## Features

- Real-time 3D rendering in terminal
- First-person movement and look controls
- Jump mechanics with gravity
- Dynamic lighting and shadows
- Textured walls using ASCII patterns
- Colored wall types: A (red), B (green), C (yellow), D (blue), E (magenta)
- Orange NPCs that walk around the map autonomously

## Controls

- **W/S** - Move forward/backward
- **A/D** - Turn left/right
- **SPACE** - Jump
- **Q/E** - Look up/down
- **X** - Quit

## Requirements

- Python 3.x
- Windows (current version uses `msvcrt`)
- For Mac/Linux: Replace `msvcrt` with `termios`/`tty` for keyboard input

## Usage

```bash
python render.py
```

## How it Works

Uses raycasting to render a 3D perspective from a 2D map. Each column of the screen casts a ray to determine wall distance and height, creating the illusion of 3D depth with ASCII characters.