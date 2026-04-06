"""
object_pool.py
Demonstrates Object Pooling — a key frame rate optimization technique.

Instead of creating and destroying bullet objects every frame (which
triggers garbage collection and spikes CPU cost), we pre-allocate a
fixed pool and reuse inactive objects.  This keeps memory pressure and
draw-call overhead predictable and low.
"""

import pygame

BULLET_CLR    = (255, 220, 50)
BULLET_RADIUS = 5


class Bullet:
    """A single reusable bullet object."""

    def __init__(self):
        self.x      = 0.0
        self.y      = 0.0
        self.vx     = 0.0
        self.vy     = 0.0
        self.active = False          # False = sitting in the pool, ready to reuse

    def fire(self, x, y, target_x, target_y, speed):
        """Activate and aim this bullet toward a target point."""
        self.x      = float(x)
        self.y      = float(y)
        self.active = True

        dx = target_x - x
        dy = target_y - y
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed

    def update(self):
        if not self.active:
            return
        self.x += self.vx
        self.y += self.vy
        # Deactivate (return to pool) when it leaves the screen
        if self.x < -20 or self.x > 920 or self.y < -20 or self.y > 620:
            self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.circle(surface, BULLET_CLR,
                               (int(self.x), int(self.y)), BULLET_RADIUS)


class BulletPool:
    """
    Pre-allocated pool of Bullet objects.

    Key concept: we NEVER call Bullet() during gameplay.  When a shot is
    fired we grab the first inactive bullet from the pool and re-initialise
    it.  When it goes off-screen we mark it inactive again — no allocation,
    no garbage collection, no frame stutter.
    """

    def __init__(self, size: int = 60):
        self._pool = [Bullet() for _ in range(size)]

    # ── Public API ─────────────────────────────────────────────────────────────

    def fire(self, x, y, target_x, target_y, speed):
        """Find a free bullet and launch it.  Does nothing if pool is full."""
        for bullet in self._pool:
            if not bullet.active:
                bullet.fire(x, y, target_x, target_y, speed)
                return

    def update(self):
        for bullet in self._pool:
            bullet.update()

    def draw(self, surface):
        for bullet in self._pool:
            bullet.draw(surface)

    def active_bullets(self):
        """Yield only the currently live bullets (for collision checks)."""
        for bullet in self._pool:
            if bullet.active:
                yield bullet

    def stats(self) -> dict:
        """Return pool usage info for the HUD display."""
        active = sum(1 for b in self._pool if b.active)
        return {
            "active": active,
            "pooled": len(self._pool) - active,
            "total":  len(self._pool),
        }
