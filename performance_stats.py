"""
performance_stats.py
GDT-110 | Week 3 | Memory Management Prototype

Tracks and compares performance between:
  - No pooling / no caching  (baseline: dynamic allocation every frame)
  - With pooling + caching   (optimized: reuse everything)

Metrics tracked:
  - Simulated allocation count (how many times memory would be allocated)
  - Simulated GC pressure (how often the garbage collector would fire)
  - Frame time consistency (how stable the frame loop is)
  - Memory footprint (how much is held in the resource cache)
"""

import time
import pygame


class PerformanceStats:

    # How many simulated allocations before a "GC pause" is triggered.
    # This mirrors Unity's managed heap threshold behaviour.
    GC_THRESHOLD = 50

    def __init__(self):
        # ── Baseline (no optimisation) counters ──────────────────────────────
        # These simulate what would happen if we created and destroyed objects
        # every frame instead of pooling and caching them.
        self.baseline_allocs      = 0    # total allocations that would have occurred
        self.baseline_gc_pauses   = 0    # how many GC pauses would have fired
        self.baseline_alloc_since_gc = 0 # allocations since last simulated GC

        # ── Optimised counters ───────────────────────────────────────────────
        self.pool_reuses          = 0    # times an object was reused from the pool
        self.cache_hits           = 0    # times a texture was served from cache
        self.actual_allocs        = 0    # real allocations (pool init + cache misses)

        # ── Frame timing ─────────────────────────────────────────────────────
        self.frame_times: list[float] = []   # rolling last-60 frame durations
        self.start_time = time.perf_counter()

    # ── Recording ────────────────────────────────────────────────────────────

    def record_frame(self, dt: float):
        """Call once per frame with the delta time in seconds."""
        self.frame_times.append(dt)
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)

    def record_baseline_alloc(self, count: int = 1):
        """
        Simulate what would happen without pooling/caching.
        Every bullet fired, every enemy spawned, every texture loaded would
        be a new allocation in a naive implementation.
        """
        self.baseline_allocs      += count
        self.baseline_alloc_since_gc += count
        if self.baseline_alloc_since_gc >= self.GC_THRESHOLD:
            self.baseline_gc_pauses      += 1
            self.baseline_alloc_since_gc  = 0

    def record_pool_reuse(self):
        """Record that an object was reused from the pool (not allocated)."""
        self.pool_reuses += 1

    def record_cache_hit(self):
        """Record that a texture was served from cache (not reallocated)."""
        self.cache_hits += 1

    def record_actual_alloc(self):
        """Record a real allocation (pool init or cache miss)."""
        self.actual_allocs += 1

    # ── Computed metrics ─────────────────────────────────────────────────────

    @property
    def avg_frame_ms(self) -> float:
        if not self.frame_times:
            return 0.0
        return (sum(self.frame_times) / len(self.frame_times)) * 1000

    @property
    def frame_variance_ms(self) -> float:
        """
        Measures frame time consistency.
        High variance = stuttery gameplay even if average FPS looks fine.
        Low variance = smooth, consistent frames.
        """
        if len(self.frame_times) < 2:
            return 0.0
        avg = sum(self.frame_times) / len(self.frame_times)
        variance = sum((t - avg) ** 2 for t in self.frame_times) / len(self.frame_times)
        return (variance ** 0.5) * 1000   # std deviation in ms

    @property
    def allocs_saved(self) -> int:
        """How many allocations were avoided by pooling and caching."""
        return self.pool_reuses + self.cache_hits

    @property
    def gc_pauses_avoided(self) -> int:
        """
        Estimated GC pauses avoided.
        In the baseline, one GC fires every GC_THRESHOLD allocations.
        With optimisation, we only count actual allocations toward GC pressure.
        """
        optimised_gc = self.actual_allocs // self.GC_THRESHOLD
        return max(0, self.baseline_gc_pauses - optimised_gc)

    @property
    def elapsed_seconds(self) -> float:
        return time.perf_counter() - self.start_time

    def snapshot(self) -> dict:
        return {
            "elapsed":           self.elapsed_seconds,
            "avg_frame_ms":      self.avg_frame_ms,
            "frame_variance_ms": self.frame_variance_ms,
            "baseline_allocs":   self.baseline_allocs,
            "baseline_gc":       self.baseline_gc_pauses,
            "pool_reuses":       self.pool_reuses,
            "cache_hits":        self.cache_hits,
            "actual_allocs":     self.actual_allocs,
            "allocs_saved":      self.allocs_saved,
            "gc_avoided":        self.gc_pauses_avoided,
        }


# ---------------------------------------------------------------------------
# StatsOverlay
# Draws the performance comparison panel onto a pygame surface.
# ---------------------------------------------------------------------------
class StatsOverlay:

    def __init__(self):
        self.font_lg = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 13)

    def draw(self, surface: pygame.Surface, stats: PerformanceStats,
             resource_kb: float, x: int = 0, y: int = 0):
        """Draw the full performance comparison panel at (x, y)."""
        snap = stats.snapshot()

        panel_w, panel_h = 420, 280
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 200))
        surface.blit(panel, (x, y))

        # Title
        surface.blit(self.font_lg.render("MEMORY MANAGEMENT STATS", True,
                                          (200, 200, 255)), (x + 10, y + 8))

        # Divider line
        pygame.draw.line(surface, (80, 80, 120),
                         (x + 10, y + 30), (x + panel_w - 10, y + 30), 1)

        # Column headers
        surface.blit(self.font_sm.render("WITHOUT optimisation", True, (255, 100, 100)),
                     (x + 10, y + 38))
        surface.blit(self.font_sm.render("WITH optimisation", True, (100, 220, 100)),
                     (x + 220, y + 38))

        # Row data
        rows = [
            ("Allocations",
             str(snap["baseline_allocs"]),
             str(snap["actual_allocs"])),
            ("GC pauses simulated",
             str(snap["baseline_gc"]),
             str(snap["baseline_gc"] - snap["gc_avoided"])),
            ("Allocs avoided",
             "N/A",
             str(snap["allocs_saved"])),
            ("GC pauses avoided",
             "N/A",
             str(snap["gc_avoided"])),
            ("Texture cache KB",
             "N/A",
             f"{resource_kb:.1f} KB"),
            ("Avg frame time",
             "N/A",
             f"{snap['avg_frame_ms']:.2f} ms"),
            ("Frame variance",
             "N/A",
             f"{snap['frame_variance_ms']:.3f} ms"),
        ]

        for i, (label, before, after) in enumerate(rows):
            row_y = y + 58 + i * 28
            lbl_color  = (180, 180, 180)
            bad_color  = (255, 100, 100)
            good_color = (100, 220, 100)
            neu_color  = (200, 200, 200)

            surface.blit(self.font_sm.render(label, True, lbl_color),
                         (x + 10, row_y))
            surface.blit(self.font_sm.render(before, True,
                         bad_color if before != "N/A" else neu_color),
                         (x + 210, row_y))
            surface.blit(self.font_sm.render(after, True,
                         good_color if after != "N/A" else neu_color),
                         (x + 330, row_y))

        # Footer hint
        surface.blit(self.font_sm.render(f"Runtime: {snap['elapsed']:.1f}s",
                                          True, (130, 130, 150)),
                     (x + 10, y + panel_h - 20))
