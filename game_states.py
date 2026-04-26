"""
game_states.py
GDT-110 | Week 5 | Design Patterns Prototype

Implements the STATE design pattern.

The State pattern organizes game behavior into separate state classes.
Each state handles its own input, update logic, and drawing. The GameManager
switches between states cleanly without needing large if/else chains.

States implemented:
  MenuState    - title screen, waits for ENTER
  PlayingState - main gameplay loop
  PausedState  - overlay pause screen, ESC to resume
  GameOverState - end screen, R to restart or ESC to quit

Each state follows the same interface:
  on_enter()        - called once when the state becomes active
  update(events, dt) - called every frame for logic and input
  draw(screen)      - called every frame for rendering
"""

import pygame
import random
import math
from game_manager import GameManager

# ── Colors ─────────────────────────────────────────────────────────────────────
BG_COLOR   = (15,  15,  30)
WHITE      = (255, 255, 255)
UI_CLR     = (200, 200, 200)
GREEN      = (80,  220, 100)
ORANGE     = (255, 160, 40)
RED        = (255, 60,  60)
BLUE       = (80,  180, 255)
YELLOW     = (255, 220, 50)
HEART_CLR  = (220, 60,  80)
GRAY       = (80,  80,  100)
DIM        = (0,   0,   0)

SCREEN_W   = 900
SCREEN_H   = 600
PLAYER_SPD = 4
BULLET_SPD = 8
MAX_LIVES  = 3


# =============================================================================
# BASE STATE CLASS
# All states inherit from this. Defines the shared interface.
# =============================================================================
class GameState:
    """
    Base class for all game states.
    Each state overrides on_enter(), update(), and draw().
    """
    def on_enter(self):
        pass

    def update(self, events, dt):
        pass

    def draw(self, screen):
        pass


# =============================================================================
# MENU STATE
# =============================================================================
class MenuState(GameState):
    """
    Displays the title screen.
    Waits for the player to press ENTER before transitioning to PlayingState.
    """

    def __init__(self):
        self.font_title = pygame.font.SysFont("consolas", 48, bold=True)
        self.font_sub   = pygame.font.SysFont("consolas", 22)
        self.font_sm    = pygame.font.SysFont("consolas", 16)
        self.pulse_t    = 0.0

    def on_enter(self):
        # Nothing to set up for the menu
        pass

    def update(self, events, dt):
        self.pulse_t += dt / 1000.0
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Transition to the playing state — State pattern in action
                    GameManager.get_instance().change_state(PlayingState())
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

    def draw(self, screen):
        screen.fill(BG_COLOR)

        # Animated grid background
        for gx in range(0, SCREEN_W, 60):
            pygame.draw.line(screen, (22, 22, 42), (gx, 0), (gx, SCREEN_H))
        for gy in range(0, SCREEN_H, 60):
            pygame.draw.line(screen, (22, 22, 42), (0, gy), (SCREEN_W, gy))

        # Title
        title = self.font_title.render("TOP-DOWN SHOOTER", True, BLUE)
        screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 160))

        # Subtitle
        sub = self.font_sub.render("Design Patterns Prototype  |  GDT-110", True, GRAY)
        screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 230))

        # Pulsing prompt
        alpha = int(180 + 75 * math.sin(self.pulse_t * 3))
        prompt = self.font_sub.render("Press ENTER to Start", True,
                                       (alpha, alpha, alpha))
        screen.blit(prompt, (SCREEN_W // 2 - prompt.get_width() // 2, 320))

        # Pattern info
        p1 = self.font_sm.render("Singleton Pattern: GameManager", True, (100, 180, 100))
        p2 = self.font_sm.render("State Pattern: Menu / Playing / Paused / Game Over",
                                  True, (100, 180, 100))
        screen.blit(p1, (SCREEN_W // 2 - p1.get_width() // 2, 420))
        screen.blit(p2, (SCREEN_W // 2 - p2.get_width() // 2, 445))

        hint = self.font_sm.render("ESC = Quit", True, GRAY)
        screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 510))


# =============================================================================
# PLAYING STATE
# =============================================================================
class PlayingState(GameState):
    """
    Main gameplay loop.
    Handles player movement, enemy spawning, shooting, collision detection,
    score tracking, and transitions to PausedState or GameOverState.
    """

    def __init__(self):
        self.font_lg = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 14)

    def on_enter(self):
        """Reset all gameplay objects when entering this state."""
        self.player_x    = float(SCREEN_W // 2)
        self.player_y    = float(SCREEN_H // 2)
        self.player_size = 22
        self.inv_until   = 0      # invincibility timestamp after hit

        self.bullets     = []     # list of [x, y, vx, vy]
        self.enemies     = []     # list of [x, y, speed]
        self.shoot_cd    = 0

        self.enemy_timer = 0.0
        self.enemy_spawn_ms = 1200

        self.fps_samples = []
        self.sample_t    = 0.0

    def update(self, events, dt):
        manager = GameManager.get_instance()   # Singleton access
        self.sample_t    += dt / 1000.0
        self.enemy_timer += dt
        if self.shoot_cd > 0:
            self.shoot_cd -= 1

        # ── Input ──────────────────────────────────────────────────────────
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Transition to PausedState — State pattern
                    GameManager.get_instance().change_state(
                        PausedState(self))
                if event.key == pygame.K_SPACE and self.shoot_cd == 0:
                    mx, my = pygame.mouse.get_pos()
                    self._fire(self.player_x, self.player_y, mx, my)
                    self.shoot_cd = 12

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player_y = max(self.player_size,
                                self.player_y - PLAYER_SPD)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player_y = min(SCREEN_H - self.player_size,
                                self.player_y + PLAYER_SPD)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player_x = max(self.player_size,
                                self.player_x - PLAYER_SPD)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player_x = min(SCREEN_W - self.player_size,
                                self.player_x + PLAYER_SPD)

        # Auto shoot toward nearest enemy
        if keys[pygame.K_SPACE] and self.shoot_cd == 0 and self.enemies:
            nearest = min(self.enemies,
                          key=lambda e: (e[0] - self.player_x)**2 +
                                        (e[1] - self.player_y)**2)
            self._fire(self.player_x, self.player_y,
                       nearest[0], nearest[1])
            self.shoot_cd = 12

        # ── Spawn enemies ──────────────────────────────────────────────────
        if self.enemy_timer >= self.enemy_spawn_ms:
            self._spawn_enemy()
            self.enemy_timer = 0.0

        # ── Update bullets ────────────────────────────────────────────────
        for b in self.bullets:
            b[0] += b[2]
            b[1] += b[3]
        self.bullets = [b for b in self.bullets
                        if 0 <= b[0] <= SCREEN_W and 0 <= b[1] <= SCREEN_H]

        # ── Update enemies ────────────────────────────────────────────────
        for e in self.enemies:
            dx = self.player_x - e[0]
            dy = self.player_y - e[1]
            dist = max(1, math.sqrt(dx**2 + dy**2))
            e[0] += (dx / dist) * e[2]
            e[1] += (dy / dist) * e[2]

        # ── Bullet / enemy collisions ──────────────────────────────────────
        alive_enemies = []
        for e in self.enemies:
            hit = False
            for b in self.bullets:
                if abs(b[0] - e[0]) < 20 and abs(b[1] - e[1]) < 20:
                    b[0] = -999   # mark bullet as off screen
                    hit = True
                    manager.add_score(10)   # Singleton updates the score
                    break
            if not hit:
                alive_enemies.append(e)
        self.enemies  = alive_enemies
        self.bullets  = [b for b in self.bullets if b[0] != -999]

        # ── Enemy / player collisions ──────────────────────────────────────
        now = pygame.time.get_ticks()
        alive_enemies = []
        for e in self.enemies:
            if (abs(e[0] - self.player_x) < self.player_size + 14 and
                    abs(e[1] - self.player_y) < self.player_size + 14):
                if now >= self.inv_until:
                    manager.lose_life()     # Singleton tracks lives
                    self.inv_until = now + 2000
            else:
                alive_enemies.append(e)
        self.enemies = alive_enemies

        # ── Check game over ────────────────────────────────────────────────
        if manager.lives <= 0:
            GameManager.get_instance().change_state(GameOverState())

        # ── FPS sampling ───────────────────────────────────────────────────
        if self.sample_t >= 0.25:
            self.sample_t = 0.0

    def draw(self, screen):
        manager = GameManager.get_instance()
        screen.fill(BG_COLOR)

        # Grid
        for gx in range(0, SCREEN_W, 60):
            pygame.draw.line(screen, (25, 25, 45), (gx, 0), (gx, SCREEN_H))
        for gy in range(0, SCREEN_H, 60):
            pygame.draw.line(screen, (25, 25, 45), (0, gy), (SCREEN_W, gy))

        # Bullets
        for b in self.bullets:
            pygame.draw.circle(screen, YELLOW, (int(b[0]), int(b[1])), 5)

        # Enemies
        for e in self.enemies:
            r = pygame.Rect(e[0] - 16, e[1] - 16, 32, 32)
            pygame.draw.rect(screen, RED, r, border_radius=4)
            pygame.draw.rect(screen, WHITE, r, 2, border_radius=4)

        # Player
        now = pygame.time.get_ticks()
        inv  = now < self.inv_until
        flash = (now // 100) % 2 == 0
        color = WHITE if (inv and flash) else BLUE
        pygame.draw.circle(screen, color,
                           (int(self.player_x), int(self.player_y)),
                           self.player_size)
        pygame.draw.circle(screen, WHITE,
                           (int(self.player_x), int(self.player_y)),
                           self.player_size, 2)

        # HUD panel
        panel = pygame.Surface((310, 110), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        screen.blit(panel, (8, 8))

        screen.blit(self.font_lg.render(
            f"Score : {manager.score}", True, WHITE), (16, 12))
        screen.blit(self.font_sm.render(
            f"Best  : {manager.high_score}", True, GRAY), (16, 40))
        screen.blit(self.font_sm.render(
            f"Enemies: {len(self.enemies)}", True, UI_CLR), (16, 58))

        # Hearts
        for i in range(manager.lives):
            self._draw_heart(screen,
                             SCREEN_W - 30 - i * 35, 28, 22, HEART_CLR)
        for i in range(manager.lives, MAX_LIVES):
            self._draw_heart(screen,
                             SCREEN_W - 30 - i * 35, 28, 22, GRAY)

        if inv:
            t = (self.inv_until - now) / 1000
            screen.blit(self.font_sm.render(
                f"Invincible: {t:.1f}s", True, ORANGE),
                (SCREEN_W - 200, 58))

        # State label (shows the pattern working)
        lbl = self.font_sm.render("STATE: PLAYING  [ESC = Pause]",
                                   True, (80, 80, 110))
        screen.blit(lbl, (10, SCREEN_H - 20))

        hints = "WASD=Move  SPACE=Shoot"
        screen.blit(self.font_sm.render(hints, True, (80, 80, 110)),
                    (SCREEN_W - 200, SCREEN_H - 20))

    # ── Private helpers ─────────────────────────────────────────────────────
    def _fire(self, x, y, tx, ty):
        dx, dy = tx - x, ty - y
        dist = max(1, math.sqrt(dx**2 + dy**2))
        vx = (dx / dist) * BULLET_SPD
        vy = (dy / dist) * BULLET_SPD
        self.bullets.append([float(x), float(y), vx, vy])

    def _spawn_enemy(self):
        edge = random.randint(0, 3)
        if edge == 0:   x, y = random.randint(0, SCREEN_W), -16
        elif edge == 1: x, y = SCREEN_W + 16, random.randint(0, SCREEN_H)
        elif edge == 2: x, y = random.randint(0, SCREEN_W), SCREEN_H + 16
        else:           x, y = -16, random.randint(0, SCREEN_H)
        self.enemies.append([float(x), float(y),
                              random.uniform(1.2, 2.8)])

    @staticmethod
    def _draw_heart(surface, cx, cy, size, color):
        r = size // 2
        pygame.draw.circle(surface, color, (cx - r // 2, cy - 2), r // 2 + 1)
        pygame.draw.circle(surface, color, (cx + r // 2, cy - 2), r // 2 + 1)
        pts = [(cx - size // 2, cy),
               (cx + size // 2, cy),
               (cx, cy + size // 2 + 2)]
        pygame.draw.polygon(surface, color, pts)


# =============================================================================
# PAUSED STATE
# =============================================================================
class PausedState(GameState):
    """
    Overlay pause screen.
    Stores a reference to the PlayingState so gameplay can resume exactly
    where it left off when ESC is pressed again.
    """

    def __init__(self, playing_state: PlayingState):
        # Keep the playing state alive so we can return to it
        self.playing_state = playing_state
        self.font_lg = pygame.font.SysFont("consolas", 48, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 20)

    def on_enter(self):
        pass

    def update(self, events, dt):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Resume — transition back to the playing state
                    GameManager.get_instance().change_state(
                        self.playing_state)

    def draw(self, screen):
        # Draw the playing state underneath so it shows through the overlay
        self.playing_state.draw(screen)

        # Dark overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        paused = self.font_lg.render("PAUSED", True, WHITE)
        screen.blit(paused,
                    (SCREEN_W // 2 - paused.get_width() // 2,
                     SCREEN_H // 2 - 60))

        hint = self.font_sm.render("Press ESC to Resume", True, UI_CLR)
        screen.blit(hint,
                    (SCREEN_W // 2 - hint.get_width() // 2,
                     SCREEN_H // 2 + 20))

        lbl = self.font_sm.render("STATE: PAUSED", True, (80, 80, 110))
        screen.blit(lbl, (10, SCREEN_H - 20))


# =============================================================================
# GAME OVER STATE
# =============================================================================
class GameOverState(GameState):
    """
    End screen shown when the player runs out of lives.
    R restarts the game, ESC quits.
    Calls manager.reset_game() to clear score and lives through the Singleton.
    """

    def __init__(self):
        self.font_lg = pygame.font.SysFont("consolas", 48, bold=True)
        self.font_md = pygame.font.SysFont("consolas", 24)
        self.font_sm = pygame.font.SysFont("consolas", 18)

    def on_enter(self):
        pass

    def update(self, events, dt):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset through the Singleton and start a new game
                    GameManager.get_instance().reset_game()
                    GameManager.get_instance().change_state(PlayingState())
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

    def draw(self, screen):
        manager = GameManager.get_instance()
        screen.fill(BG_COLOR)

        for gx in range(0, SCREEN_W, 60):
            pygame.draw.line(screen, (22, 22, 42), (gx, 0), (gx, SCREEN_H))
        for gy in range(0, SCREEN_H, 60):
            pygame.draw.line(screen, (22, 22, 42), (0, gy), (SCREEN_W, gy))

        go = self.font_lg.render("GAME OVER", True, RED)
        screen.blit(go, (SCREEN_W // 2 - go.get_width() // 2,
                          SCREEN_H // 2 - 100))

        score = self.font_md.render(f"Score: {manager.score}",
                                     True, WHITE)
        screen.blit(score, (SCREEN_W // 2 - score.get_width() // 2,
                             SCREEN_H // 2 - 30))

        best = self.font_md.render(f"Best: {manager.high_score}",
                                    True, YELLOW)
        screen.blit(best, (SCREEN_W // 2 - best.get_width() // 2,
                            SCREEN_H // 2 + 10))

        hint = self.font_sm.render("R = Restart   ESC = Quit",
                                    True, UI_CLR)
        screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2,
                            SCREEN_H // 2 + 70))

        lbl = self.font_sm.render("STATE: GAME OVER", True, (80, 80, 110))
        screen.blit(lbl, (10, SCREEN_H - 20))
