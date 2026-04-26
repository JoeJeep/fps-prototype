"""
main.py
GDT-110 | Week 5 | Design Patterns Prototype

Top-Down Shooter demonstrating two design patterns:

  SINGLETON (game_manager.py)
    GameManager.get_instance() always returns the same shared object.
    Score, lives, and high score are tracked in one place and accessible
    from anywhere in the codebase without passing references around.

  STATE (game_states.py)
    The game has four states: Menu, Playing, Paused, Game Over.
    Each state is its own class with its own update() and draw() logic.
    GameManager.change_state() switches between them cleanly.

Controls:
  ENTER        - Start game from menu
  WASD         - Move player
  SPACE        - Shoot toward nearest enemy
  ESC          - Pause / unpause during gameplay
  R            - Restart from game over screen
  ESC          - Quit from menu or game over screen
"""

import pygame
from game_manager import GameManager
from game_states   import MenuState

SCREEN_W = 900
SCREEN_H = 600
FPS      = 60


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Design Patterns Prototype — GDT-110 Week 5")
    clock  = pygame.time.Clock()

    # ── Singleton: get the one shared GameManager instance ──────────────────
    # No matter where in the codebase get_instance() is called, this same
    # object is returned. Score and lives are always in sync.
    manager = GameManager.get_instance()

    # ── State: start in the Menu state ──────────────────────────────────────
    # change_state() calls on_enter() on MenuState and stores it as active.
    # From here, all update() and draw() calls go through the active state.
    manager.change_state(MenuState())

    running = True
    while running:
        dt     = clock.tick(FPS)
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Delegate update and draw to whatever state is currently active.
        # This is the State pattern — main.py never needs to know which
        # state is running or what its logic is.
        manager.update(events, dt)
        manager.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
