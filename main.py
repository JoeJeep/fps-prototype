"""
main.py
GDT-110 | Week 3 | Memory Management Prototype

Expands on the Week 2 FPS prototype to demonstrate:
  1. Resource loading and unloading  (resource_manager.py)
  2. Texture caching and reuse       (resource_manager.py)
  3. Object pooling                  (object_pool.py)
  4. Performance comparison          (performance_stats.py)

Controls:
  WASD / Arrow keys  = Move player
  SPACE              = Shoot
  TAB                = Cycle FPS mode (30 / 60 / 480)
  L                  = Load all textures into cache
  U                  = Unload unused textures
  P                  = Toggle performance stats panel
  R (game over)      = Restart
  ESC (game over)    = Quit
"""

import pygame
import random
from object_pool      import BulletPool
from resource_manager import ResourceManager, SimulatedTexture
from performance_stats import PerformanceStats, StatsOverlay

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 960, 640
BG_COLOR    = (15,  15,  30)
WHITE       = (255, 255, 255)
UI_CLR      = (200, 200, 200)
GREEN       = (80,  220, 100)
ORANGE      = (255, 160, 40)
RED         = (255, 60,  60)
HEART_CLR   = (220, 60,  80)
GRAY        = (100, 100, 120)

FPS_MODES   = [30, 60, 480]
FPS_LABELS  = ["30 FPS", "60 FPS", "480 FPS"]

PLAYER_SPEED   = 4
ENEMY_SPAWN_MS = 1200
BULLET_SPEED   = 8
MAX_LIVES      = 3
INVINCIBLE_MS  = 2000

# Scene asset list — these are preloaded when the game starts
SCENE_ASSETS = [
    "player_texture",
    "enemy_texture",
    "bullet_texture",
    "background_tile",
]


# ── Player ─────────────────────────────────────────────────────────────────────
class Player:
    SIZE = 22

    def __init__(self, texture: SimulatedTexture):
        self.x = SCREEN_W // 2
        self.y = SCREEN_H // 2
        self.shoot_cooldown   = 0
        self.lives            = MAX_LIVES
        self.invincible_until = 0
        # Store the texture reference — resource manager tracks its ref count
        self.texture = texture

    def is_invincible(self):
        return pygame.time.get_ticks() < self.invincible_until

    def take_hit(self):
        if self.is_invincible():
            return
        self.lives -= 1
        self.invincible_until = pygame.time.get_ticks() + INVINCIBLE_MS

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y = max(self.SIZE, self.y - PLAYER_SPEED)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y = min(SCREEN_H - self.SIZE, self.y + PLAYER_SPEED)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x = max(self.SIZE, self.x - PLAYER_SPEED)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x = min(SCREEN_W - self.SIZE, self.x + PLAYER_SPEED)

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, surface):
        # Use the texture color for the player circle
        color = self.texture.color
        if self.is_invincible():
            flash = (pygame.time.get_ticks() // 100) % 2 == 0
            color = WHITE if flash else self.texture.color
        pygame.draw.circle(surface, color, (self.x, self.y), self.SIZE)
        pygame.draw.circle(surface, WHITE,  (self.x, self.y), self.SIZE, 2)


# ── Enemy ──────────────────────────────────────────────────────────────────────
class Enemy:
    SIZE = 16

    def __init__(self, texture: SimulatedTexture):
        self.texture = texture
        self.reset()

    def reset(self):
        edge = random.randint(0, 3)
        if edge == 0:   self.x, self.y = random.randint(0, SCREEN_W), -self.SIZE
        elif edge == 1: self.x, self.y = SCREEN_W + self.SIZE, random.randint(0, SCREEN_H)
        elif edge == 2: self.x, self.y = random.randint(0, SCREEN_W), SCREEN_H + self.SIZE
        else:           self.x, self.y = -self.SIZE, random.randint(0, SCREEN_H)
        self.speed  = random.uniform(1.2, 2.8)
        self.active = True

    def update(self, tx, ty):
        dx, dy = tx - self.x, ty - self.y
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

    def draw(self, surface):
        rect = pygame.Rect(self.x - self.SIZE, self.y - self.SIZE,
                           self.SIZE * 2, self.SIZE * 2)
        pygame.draw.rect(surface, self.texture.color, rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=4)


# ── Helpers ────────────────────────────────────────────────────────────────────
def draw_heart(surface, cx, cy, size, color):
    r = size // 2
    pygame.draw.circle(surface, color, (cx - r // 2, cy - 2), r // 2 + 1)
    pygame.draw.circle(surface, color, (cx + r // 2, cy - 2), r // 2 + 1)
    pts = [(cx - size // 2, cy), (cx + size // 2, cy), (cx, cy + size // 2 + 2)]
    pygame.draw.polygon(surface, color, pts)


def show_game_over(screen, font_lg, font_sm, score):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    screen.blit(font_lg.render("GAME OVER", True, RED),
                (SCREEN_W // 2 - 110, SCREEN_H // 2 - 70))
    screen.blit(font_lg.render(f"Score: {score}", True, WHITE),
                (SCREEN_W // 2 - 80, SCREEN_H // 2 - 30))
    screen.blit(font_sm.render("Press R to restart  |  ESC to quit",
                                True, UI_CLR),
                (SCREEN_W // 2 - 160, SCREEN_H // 2 + 20))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:     return True
                if event.key == pygame.K_ESCAPE: return False


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Memory Management Prototype — GDT-110 Week 3")
    clock   = pygame.time.Clock()

    font_lg = pygame.font.SysFont("consolas", 20, bold=True)
    font_sm = pygame.font.SysFont("consolas", 13)
    font_xs = pygame.font.SysFont("consolas", 11)

    # Initialise subsystems
    # ResourceManager handles all asset loading, caching, and unloading
    res_mgr      = ResourceManager()
    perf_stats   = PerformanceStats()
    stats_overlay = StatsOverlay()

    while True:     # outer loop handles restarts

        # ── Scene preload ─────────────────────────────────────────────────────
        # Load only what this scene needs upfront (lazy loading for the rest)
        # This mirrors Unity's scene loading — allocate assets before gameplay.
        res_mgr.preload_scene(SCENE_ASSETS, compression=SimulatedTexture.FULL)
        perf_stats.record_actual_alloc()   # count the real allocations

        player_tex = res_mgr.load_texture("player_texture")
        enemy_tex  = res_mgr.load_texture("enemy_texture")

        # Object pool pre-allocates 60 bullets at startup — no runtime allocs
        bullet_pool  = BulletPool(size=60)
        perf_stats.record_actual_alloc()   # pool itself is one allocation event

        player       = Player(player_tex)
        enemies      = []
        score        = 0
        fps_mode_idx = 1
        last_enemy_t = pygame.time.get_ticks()
        fps_samples  = []
        sample_timer = 0.0
        show_stats   = True    # P key toggles the performance panel

        running = True
        while running:
            dt = clock.tick(FPS_MODES[fps_mode_idx]) / 1000.0
            sample_timer += dt
            perf_stats.record_frame(dt)

            # ── Events ────────────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        fps_mode_idx = (fps_mode_idx + 1) % len(FPS_MODES)

                    if event.key == pygame.K_SPACE and player.shoot_cooldown == 0:
                        mx, my = pygame.mouse.get_pos()
                        bullet_pool.fire(player.x, player.y, mx, my, BULLET_SPEED)
                        player.shoot_cooldown = 12
                        # Simulate what no-pool would cost (one alloc per bullet)
                        perf_stats.record_baseline_alloc()
                        perf_stats.record_pool_reuse()

                    # L = manually load all catalogue textures into cache
                    # Demonstrates preloading optional / non-scene assets
                    if event.key == pygame.K_l:
                        for name in ResourceManager.ASSET_CATALOGUE:
                            res_mgr.load_texture(name)
                            if res_mgr.total_cache_hits > perf_stats.cache_hits:
                                perf_stats.record_cache_hit()
                            else:
                                perf_stats.record_actual_alloc()

                    # U = unload unused textures (simulate scene transition)
                    if event.key == pygame.K_u:
                        res_mgr.unload_unused()

                    # P = toggle performance stats overlay
                    if event.key == pygame.K_p:
                        show_stats = not show_stats

            # Auto-shoot toward nearest enemy
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and player.shoot_cooldown == 0 and enemies:
                nearest = min(enemies,
                              key=lambda e: (e.x - player.x)**2 + (e.y - player.y)**2)
                bullet_pool.fire(player.x, player.y, nearest.x, nearest.y, BULLET_SPEED)
                player.shoot_cooldown = 12
                perf_stats.record_baseline_alloc()
                perf_stats.record_pool_reuse()

            # ── Spawn enemies ──────────────────────────────────────────────────
            now = pygame.time.get_ticks()
            if now - last_enemy_t > ENEMY_SPAWN_MS:
                # Enemy texture served from cache — no new allocation needed
                tex = res_mgr.load_texture("enemy_texture")
                perf_stats.record_cache_hit()          # texture reused
                perf_stats.record_baseline_alloc(2)    # baseline would alloc enemy + texture
                enemies.append(Enemy(tex))
                last_enemy_t = now

            # ── Update ─────────────────────────────────────────────────────────
            player.handle_input()
            player.update()
            bullet_pool.update()
            for enemy in enemies:
                enemy.update(player.x, player.y)

            # Bullet / enemy collision
            for bullet in bullet_pool.active_bullets():
                for enemy in enemies:
                    if abs(bullet.x - enemy.x) < enemy.SIZE + 4 and \
                       abs(bullet.y - enemy.y) < enemy.SIZE + 4:
                        bullet.active = False
                        enemy.active  = False
                        score += 10
                        # Unload the enemy's texture reference when it dies
                        res_mgr.unload_texture("enemy_texture")

            # Player / enemy collision
            for enemy in enemies:
                if abs(enemy.x - player.x) < player.SIZE + enemy.SIZE - 6 and \
                   abs(enemy.y - player.y) < player.SIZE + enemy.SIZE - 6:
                    player.take_hit()
                    enemy.active = False
                    res_mgr.unload_texture("enemy_texture")

            enemies = [e for e in enemies if e.active]

            if player.lives <= 0:
                running = False

            # ── FPS sampling ───────────────────────────────────────────────────
            raw_fps = clock.get_fps()
            if sample_timer >= 0.25:
                fps_samples.append(raw_fps)
                if len(fps_samples) > 40:
                    fps_samples.pop(0)
                sample_timer = 0.0
            avg_fps   = sum(fps_samples) / len(fps_samples) if fps_samples else raw_fps
            pool_info = bullet_pool.stats()

            # ── Draw ───────────────────────────────────────────────────────────
            screen.fill(BG_COLOR)

            for gx in range(0, SCREEN_W, 60):
                pygame.draw.line(screen, (25, 25, 45), (gx, 0), (gx, SCREEN_H))
            for gy in range(0, SCREEN_H, 60):
                pygame.draw.line(screen, (25, 25, 45), (0, gy), (SCREEN_W, gy))

            bullet_pool.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            player.draw(screen)

            # ── HUD: top-left panel ────────────────────────────────────────────
            fps_color = GREEN if avg_fps >= 55 else (ORANGE if avg_fps >= 28 else RED)

            panel = pygame.Surface((310, 200), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            screen.blit(panel, (8, 8))

            screen.blit(font_lg.render(f"FPS: {avg_fps:5.1f}",
                                        True, fps_color), (16, 12))
            screen.blit(font_sm.render(f"Mode   : {FPS_LABELS[fps_mode_idx]}  [TAB]",
                                        True, UI_CLR), (16, 40))
            screen.blit(font_sm.render(f"Bullets: {pool_info['active']:>3} active  "
                                        f"{pool_info['pooled']:>3} pooled",
                                        True, UI_CLR), (16, 58))
            screen.blit(font_sm.render(f"Enemies: {len(enemies):>3}",
                                        True, UI_CLR), (16, 76))
            screen.blit(font_sm.render(f"Score  : {score}",
                                        True, WHITE),  (16, 94))
            screen.blit(font_sm.render(f"Cached : {res_mgr.cached_assets} assets  "
                                        f"{res_mgr.total_memory_kb:.1f} KB",
                                        True, (150, 220, 255)), (16, 112))
            screen.blit(font_sm.render(f"Loads  : {res_mgr.total_loads}  "
                                        f"Hits: {res_mgr.total_cache_hits}  "
                                        f"Unloads: {res_mgr.total_unloads}",
                                        True, (150, 220, 255)), (16, 130))

            # Cache hit ratio bar
            total_requests = res_mgr.total_loads + res_mgr.total_cache_hits
            hit_ratio = res_mgr.total_cache_hits / max(1, total_requests)
            bar_w = 280
            pygame.draw.rect(screen, (60, 60, 80), (16, 152, bar_w, 10), border_radius=3)
            pygame.draw.rect(screen, GREEN,
                             (16, 152, int(bar_w * hit_ratio), 10), border_radius=3)
            screen.blit(font_xs.render(f"Cache hit ratio: {hit_ratio*100:.0f}%",
                                        True, (150, 200, 150)), (16, 165))

            # ── Hearts ─────────────────────────────────────────────────────────
            for i in range(player.lives):
                draw_heart(screen, SCREEN_W - 30 - i * 35, 30, 22, HEART_CLR)
            for i in range(player.lives, MAX_LIVES):
                draw_heart(screen, SCREEN_W - 30 - i * 35, 30, 22, GRAY)

            if player.is_invincible():
                t_left = (player.invincible_until - pygame.time.get_ticks()) / 1000
                screen.blit(font_sm.render(f"Invincible: {t_left:.1f}s",
                                            True, ORANGE),
                            (SCREEN_W - 200, 60))

            # ── FPS graph ──────────────────────────────────────────────────────
            if len(fps_samples) > 1:
                gw, gh, gx0, gy0 = 180, 50, SCREEN_W - 190, 80
                pygame.draw.rect(screen, (0, 0, 0, 180), (gx0, gy0, gw, gh))
                pygame.draw.rect(screen, (60, 60, 80),   (gx0, gy0, gw, gh), 1)
                pts = []
                for i, v in enumerate(fps_samples[-gw:]):
                    px = gx0 + int(i * gw / max(len(fps_samples), 1))
                    py = gy0 + gh - int(min(v, 120) / 120 * gh)
                    pts.append((px, py))
                if len(pts) > 1:
                    pygame.draw.lines(screen, fps_color, False, pts, 2)
                screen.blit(font_xs.render("FPS Graph", True, (150, 150, 170)),
                            (gx0 + 4, gy0 + 2))

            # ── Performance stats panel (toggle with P) ────────────────────────
            if show_stats:
                stats_overlay.draw(screen, perf_stats,
                                   res_mgr.total_memory_kb,
                                   x=SCREEN_W - 435, y=SCREEN_H - 295)

            # ── Resource event log (bottom-left) ──────────────────────────────
            log_lines = res_mgr.event_log[-6:]
            for i, line in enumerate(log_lines):
                screen.blit(font_xs.render(line, True, (120, 160, 120)),
                            (10, SCREEN_H - 110 + i * 16))

            # ── Controls hint ─────────────────────────────────────────────────
            hints = "WASD=Move  SPACE=Shoot  TAB=FPS  L=Load  U=Unload  P=Stats"
            screen.blit(font_xs.render(hints, True, (100, 100, 120)),
                        (10, SCREEN_H - 16))

            pygame.display.flip()

        restart = show_game_over(screen, font_lg, font_sm, score)
        if not restart:
            break
        # On restart, unload everything and start fresh
        res_mgr.unload_unused()

    pygame.quit()


if __name__ == "__main__":
    main()
