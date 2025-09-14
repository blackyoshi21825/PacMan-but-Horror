# 3D ASCII Horror Game

A terminal-based 3D Pac-Man-style horror game using ASCII raycasting with ghosts, health pickups, and flashlight mechanics.

## Features

- Real-time 3D rendering in terminal using raycasting
- First-person movement with mouse look support
- Jump mechanics with gravity
- Flashlight system with battery drain and flickering
- Textured brick walls with color variations
- Four Pac-Man-style ghosts with AI pathfinding
- Health system with damage and health pickups
- Minimap display
- Game over and victory screens
- Timed escape gate objective

## Controls

- **W/S** - Move forward/backward
- **A/D** - Turn left/right
- **Mouse** - Look around
- **SPACE** - Jump
- **Q/E** - Look up/down
- **F** - Toggle flashlight
- **X** - Quit

## Requirements

- Python 3.x
- Windows (current version uses `msvcrt`)
- For Mac/Linux: Replace `msvcrt` with `termios`/`tty` for keyboard input

## Usage

```bash
python render.py
```

## Gameplay

Survive in a dark maze while being hunted by four colored ghosts. After 2 minutes, a golden gate opens in the bottom-right corner of the map. Reach the gate to win! Use your flashlight to see, but watch the battery! Collect green health pickups to restore HP. Ghosts use pathfinding AI to hunt you down.

## Objective

Survive for 2 minutes until the escape gate opens, then reach it to win the game!

## Technical Details

Uses raycasting to render a 3D perspective from a 2D map. Features include:
- Textured walls with brick patterns
- Sprite rendering for ghosts and pickups
- Depth buffering for proper occlusion
- Dynamic lighting with flashlight cone
- AI pathfinding for ghost movement