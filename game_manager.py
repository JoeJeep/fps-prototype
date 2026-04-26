"""
game_manager.py
GDT-110 | Week 5 | Design Patterns Prototype

Implements the SINGLETON design pattern.

The Singleton pattern ensures only one instance of GameManager ever exists.
Every part of the game calls GameManager.get_instance() to access the same
shared object. This prevents conflicts like two managers tracking different
scores or lives simultaneously.

In game development, Singletons are commonly used for:
  - Game managers (score, lives, state)
  - Audio managers
  - Input managers
  - Resource/asset managers
"""


class GameManager:
    # Class-level variable that holds the single instance.
    # None means no instance has been created yet.
    _instance = None

    def __init__(self):
        # Game data tracked by the single manager
        self.score       = 0
        self.lives       = 3
        self.high_score  = 0

        # The currently active GameState object.
        # All update() and draw() calls are delegated here.
        self.current_state = None

    # ── Singleton access point ──────────────────────────────────────────────
    @classmethod
    def get_instance(cls):
        """
        Return the single shared instance of GameManager.
        If it does not exist yet, create it first.

        This is the core of the Singleton pattern — no matter how many times
        get_instance() is called from anywhere in the codebase, the same
        object is always returned.
        """
        if cls._instance is None:
            cls._instance = GameManager()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """
        Destroy the existing instance so a fresh one can be created.
        Used when fully restarting the game.
        """
        cls._instance = None

    # ── State management ────────────────────────────────────────────────────
    def change_state(self, new_state):
        """
        Switch the game to a new state.
        Calls on_enter() on the new state so it can set itself up.
        This is where the Singleton and State patterns connect — the manager
        owns the state machine and all states call back into the manager.
        """
        self.current_state = new_state
        self.current_state.on_enter()

    # ── Game loop delegation ────────────────────────────────────────────────
    def update(self, events, dt):
        """Delegate the update call to whatever state is currently active."""
        if self.current_state:
            self.current_state.update(events, dt)

    def draw(self, screen):
        """Delegate the draw call to whatever state is currently active."""
        if self.current_state:
            self.current_state.draw(screen)

    # ── Score and lives helpers ─────────────────────────────────────────────
    def add_score(self, points: int):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score

    def lose_life(self):
        self.lives -= 1

    def reset_game(self):
        """Reset score and lives for a new game without destroying the instance."""
        self.score = 0
        self.lives = 3
