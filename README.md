# Design Patterns Prototype
**GDT-110 | Week 5 Assignment**
**Student:** Levi
**Language:** Python 3.12 + Pygame

---

## GitHub Repository

https://github.com/JoeJeep/fps-prototype

## Video Demo

[Insert Loom link here after recording]

---

## Project Overview

This prototype is a top-down shooter that demonstrates two software design patterns — Singleton and State — applied to a working game. The game features a menu screen, full gameplay with enemies and shooting, a pause screen, and a game over screen, all managed cleanly through the two patterns.

---

## Design Patterns Used

**Singleton (game_manager.py)**
GameManager.get_instance() always returns the same shared object. Score, lives, and high score are tracked in one place and accessible from anywhere without passing references around.

**State (game_states.py)**
The game has four states: Menu, Playing, Paused, Game Over. Each is its own class with its own logic. GameManager.change_state() switches between them cleanly with no if/else chains in the main loop.

---

## How to Run

### Requirements
- Python 3.10, 3.11, or 3.12
- Pygame

### Install Pygame
```
py -3.12 -m pip install pygame
```

### Run the Game
```
py -3.12 main.py
```

---

## Controls

| Key | Action |
|---|---|
| ENTER | Start game from menu |
| WASD | Move player |
| SPACE | Shoot toward nearest enemy |
| ESC | Pause during gameplay |
| ESC | Resume from pause |
| R | Restart from game over |
| ESC | Quit from menu or game over |

---

## File Structure

```
design_patterns/
├── main.py           Entry point, game loop, Singleton and State setup
├── game_manager.py   Singleton pattern — GameManager class
├── game_states.py    State pattern — MenuState, PlayingState, PausedState, GameOverState
├── pseudocode.txt    High-level pseudocode outlining both patterns
└── README.md         This file
```

---

## References

Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). Design patterns: Elements of reusable object-oriented software. Addison-Wesley.

Pygame Community. (2024). Pygame documentation. https://www.pygame.org/docs/
