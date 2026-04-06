"""
FPS Optimization Prototype
GDT-110 | Topic 2 Assignment
Demonstrates frame rate capping, object pooling, and live FPS monitoring
"""

import pygame
import random
from object_pool import BulletPool

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 900, 600
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0)
BG_COLOR    = (15,  15,  30)
PLAYER_CLR  = (80,  180, 255)
BULLET_CLR  = (255, 220, 50)
ENEMY_CLR   = (220, 60,  60)
UI_CLR      = (200, 200, 200)
GREEN       = (80,  220, 100)
ORANGE      = (255, 160, 40)
RED         = (255, 60,  60)
HEART_CLR   = (220, 60,  80)
GRAY        = (100, 100, 120)

FPS_MODES   = [30, 60, 480]
FPS_LABELS  = ["30 FPS", "60 FPS", "480 FPS"]

PLAYER_SPEED    = 4
ENEMY_SPAWN_MS  = 1200
BULLET_SPEED    = 8
MAX_LIVES       = 3
INVINCIBLE_MS   = 2000


# ── Player ─────────────────────────────────────────────────────────────────────
class Player:
    SIZE = 22

    def __init__(self):
        self.x = SCREEN_W // 2
        self.y = SCREEN_H // 2
        self.shoot_cooldown   = 0
        self.lives            = MAX_LIVES
        self.invincible_until = 0

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
        if self.is_invincible():
            flash = (pygame.time.get_ticks() // 100) % 2 == 0
            color = WHITE if flash else PLAYER_CLR
        else:
            color = PLAYER_CLR
        pygame.draw.circle(surface, color, (self.x, self.y), self.SIZE)
        pygame.draw.circle(surface, WHITE, (self.x, self.y), self.SIZE, 2)


# ── Enemy ──────────────────────────────────────────────────────────────────────
class Enemy:
    SIZE = 16

    def __init__(self):
        self.reset()

    def reset(self):
        edge = random.randint(0, 3)
        if edge == 0:   self.x, self.y = random.randint(0, SCREEN_W), -self.SIZE
        elif edge == 1: self.x, self.y = SCREEN_W + self.SIZE, random.randint(0, SCREEN_H)
        elif edge == 2: self.x, self.y = random.randint(0, SCREEN_W), SCREEN_H + self.SIZE
        else:           self.x, self.y = -self.SIZE, random.randint(0, SCREEN_H)
        self.speed  = random.uniform(1.2, 2.8)
        self.active = True

    def update(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

    def draw(self, surface):
        rect = pygame.Rect(self.x - self.SIZE, self.y - self.SIZE,
                           self.SIZE * 2, self.SIZE * 2)
        pygame.draw.rect(surface, ENEMY_CLR, rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=4)


# ── Helper: draw heart ─────────────────────────────────────────────────────────
def draw_heart(surface, cx, cy, size, color):
    r = size // 2
    pygame.draw.circle(surface, color, (cx - r // 2, cy - 2), r // 2 + 1)
    pygame.draw.circle(surface, color, (cx + r // 2, cy - 2), r // 2 + 1)
    points = [(cx - size // 2, cy), (cx + size // 2, cy), (cx, cy + size // 2 + 2)]
    pygame.draw.polygon(surface, color, points)


# ── Game Over Screen ───────────────────────────────────────────────────────────
def show_game_over(screen, font_lg, font_sm, score):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    screen.blit(font_lg.render("GAME OVER", True, RED),
                (SCREEN_W // 2 - 110, SCREEN_H // 2 - 70))
    screen.blit(font_lg.render(f"Score: {score}", True, WHITE),
                (SCREEN_W // 2 - 80, SCREEN_H // 2 - 30))
    screen.blit(font_sm.render("Press R to restart  |  ESC to quit", True, UI_CLR),
                (SCREEN_W // 2 - 160, SCREEN_H // 2 + 20))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False


# ── Main Game ──────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("FPS Optimization Prototype — GDT-110")
    clock   = pygame.time.Clock()

    font_lg = pygame.font.SysFont("consolas", 22, bold=True)
    font_sm = pygame.font.SysFont("consolas", 15)

    while True:
        player       = Player()
        bullet_pool  = BulletPool(size=60)
        enemies      = []
        score        = 0
        fps_mode_idx = 1
        last_enemy_t = pygame.time.get_ticks()
        fps_samples  = []
        sample_timer = 0.0

        running = True
        while running:
            dt = clock.tick(FPS_MODES[fps_mode_idx]) / 1000.0
            sample_timer += dt

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

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and player.shoot_cooldown == 0 and enemies:
                nearest = min(enemies,
                              key=lambda e: (e.x - player.x)**2 + (e.y - player.y)**2)
                bullet_pool.fire(player.x, player.y, nearest.x, nearest.y, BULLET_SPEED)
                player.shoot_cooldown = 12

            now = pygame.time.get_ticks()
            if now - last_enemy_t > ENEMY_SPAWN_MS:
                enemies.append(Enemy())
                last_enemy_t = now

            player.handle_input()
            player.update()
            bullet_pool.update()

            for enemy in enemies:
                enemy.update(player.x, player.y)

            for bullet in bullet_pool.active_bullets():
                for enemy in enemies:
                    if abs(bullet.x - enemy.x) < enemy.SIZE + 4 and \
                       abs(bullet.y - enemy.y) < enemy.SIZE + 4:
                        bullet.active = False
                        enemy.active  = False
                        score += 10

            for enemy in enemies:
                if abs(enemy.x - player.x) < player.SIZE + enemy.SIZE - 6 and \
                   abs(enemy.y - player.y) < player.SIZE + enemy.SIZE - 6:
                    player.take_hit()
                    enemy.active = False

            enemies = [e for e in enemies if e.active]

            if player.lives <= 0:
                running = False

            raw_fps = clock.get_fps()
            if sample_timer >= 0.25:
                fps_samples.append(raw_fps)
                if len(fps_samples) > 40:
                    fps_samples.pop(0)
                sample_timer = 0.0

            avg_fps   = sum(fps_samples) / len(fps_samples) if fps_samples else raw_fps
            pool_info = bullet_pool.stats()

            screen.fill(BG_COLOR)

            for gx in range(0, SCREEN_W, 60):
                pygame.draw.line(screen, (25, 25, 45), (gx, 0), (gx, SCREEN_H))
            for gy in range(0, SCREEN_H, 60):
                pygame.draw.line(screen, (25, 25, 45), (0, gy), (SCREEN_W, gy))

            bullet_pool.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            player.draw(screen)

            if avg_fps >= 55:   fps_color = GREEN
            elif avg_fps >= 28: fps_color = ORANGE
            else:               fps_color = RED

            panel = pygame.Surface((300, 160), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 160))
            screen.blit(panel, (8, 8))

            screen.blit(font_lg.render(f"FPS: {avg_fps:5.1f}", True, fps_color),        (16, 14))
            screen.blit(font_sm.render(f"Mode  : {FPS_LABELS[fps_mode_idx]}  [TAB]",
                                        True, UI_CLR), (16, 46))
            screen.blit(font_sm.render(f"Active: {pool_info['active']:>3} bullets",
                                        True, UI_CLR), (16, 66))
            screen.blit(font_sm.render(f"Pooled: {pool_info['pooled']:>3} waiting",
                                        True, UI_CLR), (16, 86))
            screen.blit(font_sm.render(f"Enemies:{len(enemies):>3}",
                                        True, UI_CLR), (16, 106))
            screen.blit(font_sm.render(f"Score : {score}",
                                        True, WHITE),  (16, 126))

            for i in range(player.lives):
                draw_heart(screen, SCREEN_W - 30 - i * 35, 30, 22, HEART_CLR)
            for i in range(player.lives, MAX_LIVES):
                draw_heart(screen, SCREEN_W - 30 - i * 35, 30, 22, GRAY)

            if player.is_invincible():
                t_left = (player.invincible_until - pygame.time.get_ticks()) / 1000
                screen.blit(font_sm.render(f"Invincible: {t_left:.1f}s", True, ORANGE),
                            (SCREEN_W - 200, 60))

            hints = ["WASD / Arrows = Move",
                     "SPACE = Shoot  |  TAB = Cycle FPS Mode"]
            for i, h in enumerate(hints):
                screen.blit(font_sm.render(h, True, (130, 130, 150)),
                            (10, SCREEN_H - 36 + i * 18))

            if len(fps_samples) > 1:
                gw, gh, gx0, gy0 = 180, 50, SCREEN_W - 190, 80
                pygame.draw.rect(screen, (0, 0, 0, 180), (gx0, gy0, gw, gh))
                pygame.draw.rect(screen, (60, 60, 80), (gx0, gy0, gw, gh), 1)
                pts = []
                for i, v in enumerate(fps_samples[-gw:]):
                    px = gx0 + int(i * gw / max(len(fps_samples), 1))
                    py = gy0 + gh - int(min(v, 120) / 120 * gh)
                    pts.append((px, py))
                if len(pts) > 1:
                    pygame.draw.lines(screen, fps_color, False, pts, 2)
                screen.blit(font_sm.render("FPS Graph", True, (150, 150, 170)),
                            (gx0 + 4, gy0 + 2))

            pygame.display.flip()

        restart = show_game_over(screen, font_lg, font_sm, score)
        if not restart:
            break

    pygame.quit()


if __name__ == "__main__":
    main()
