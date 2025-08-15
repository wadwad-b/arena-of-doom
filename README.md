# Arena of Doom

[![Python](https://img.shields.io/badge/python-3.13.5-blue.svg)](https://www.python.org/)  
[![Pygame](https://img.shields.io/badge/pygame-2.6.1-green.svg)](https://www.pygame.org/news)  

Arena of Doom is a 2D action combat game built with Python and Pygame. Players fight through waves of enemies across multiple levels, equip special moves, collect buffs, and test their skills in Infinity Mode.

---

## Features

- **15 Levels:** Progress through three themed backgrounds, each introducing different enemies.
- **Varied Enemies:** Encounter spiders, fennec foxes, and sharks with unique attack patterns.
- **Special Moves:** Unlock and select powerful abilities for strategic combat.
- **Buff System:** Collect buffs that temporarily increase size, speed, attack power, or other abilities.
- **Infinity Mode:** Endless waves of enemies with selectable difficulties.
- **Dynamic Combat:** Real-time melee and ranged attacks, and health bars.
- **Level Progression:** Completed levels are tracked with checkmarks in the Level Select screen.
- **UI Elements:** Interactive buttons, panels, and informative overlays.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/wadwad-b/arena-of-doom.git
cd arena-of-doom
```

2. Install dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python main.py
```
## OR

Download the [arena-of-doom.zip](https://drive.google.com/file/d/1uOTDWWpqoR8qzYo2cO62NDnj0ilm1G76/view?usp=sharing) and extract the files to run the executable file `main.exe`.

> Make sure all `assets/` folders (fonts, sprites, backgrounds, etc.) are included in the project directory.

---

## Controls

| Action | Key / Mouse |
|--------|-------------|
| Move Up | W / ↑ |
| Move Down | S / ↓ |
| Move Left | A / ← |
| Move Right | D / → |
| Main Attack | E / Left Click |
| Special Attack | Q / Right Click |
| Open Menu / Back | ESC |

---

## Gameplay Overview

### Level Select

- Choose levels 1–15.  
- Levels are grouped in sets of 5, each with a unique background and enemy type.  
- Completed levels are marked with checkmarks.

### Special Moves

- Access the Special Move Select screen from the Level menu.  
- Select your preferred move for use in combat.  
- “In Use” indicator shows the currently equipped move.

### Buffs

- Randomly spawn during combat in Infinity mode.  
- Types include:
  - **Bigger:** Increases player size (1.5x).
  - **Smaller:** Decreases player size (1.5x) and slightly increases speed (1.25x).
  - **Faster:** Increases movement speed (2x).
  - **Sharper Sword:** Increases attack damage (2x).
- Buff icons appear next to the health bar when active.

### Combat

- Player attacks enemies with melee or special attacks.  
- Enemies deal damage and can be staggered.  
- Health bars appear below players and enemies.

### Infinity Mode

- Continuous waves of enemies.  
- Choose difficulty to adjust enemy strength and wave patterns.  
- Compete for highest wave count.

---
