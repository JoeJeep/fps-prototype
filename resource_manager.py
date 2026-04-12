"""
resource_manager.py
GDT-110 | Week 3 | Memory Management Prototype

Demonstrates dynamic resource loading, unloading, and texture caching.

Key concepts shown here:
  - Lazy loading: assets are only loaded when first requested, not all at startup
  - Texture cache: once a texture is loaded it is reused instead of reloaded
  - Reference counting: tracks how many systems are using each asset
  - Unloading: assets with zero references are eligible for removal
  - Mipmapping simulation: textures are stored at reduced sizes to save memory
"""

import pygame
import time


# ---------------------------------------------------------------------------
# SimulatedTexture
# Represents a texture asset in memory. In a real engine this would hold
# GPU-side pixel data. Here we store a pygame Surface as a stand-in.
# ---------------------------------------------------------------------------
class SimulatedTexture:
    # Compression levels simulate mipmapping / texture compression.
    # FULL   = full resolution, highest memory cost
    # HALF   = half resolution, 25% of the memory cost of FULL
    # MIPMAP = quarter resolution, 6.25% of the memory cost of FULL
    FULL    = 1.0
    HALF    = 0.5
    MIPMAP  = 0.25

    def __init__(self, name: str, width: int, height: int,
                 color: tuple, compression: float = FULL):
        self.name        = name
        self.width       = int(width  * compression)
        self.height      = int(height * compression)
        self.color       = color
        self.compression = compression
        self.ref_count   = 0          # how many systems are using this texture
        self.load_time   = time.perf_counter()

        # Create the actual pygame surface (simulates GPU allocation)
        self.surface = pygame.Surface((max(1, self.width), max(1, self.height)))
        self.surface.fill(color)

        # Memory cost in bytes: width * height * 4 bytes per pixel (RGBA)
        self.memory_bytes = self.width * self.height * 4

    def acquire(self):
        """Increment the reference count — a system is now using this texture."""
        self.ref_count += 1

    def release(self):
        """Decrement the reference count — a system is done with this texture."""
        self.ref_count = max(0, self.ref_count - 1)

    @property
    def is_unused(self):
        return self.ref_count == 0


# ---------------------------------------------------------------------------
# ResourceManager
# Central system that owns all loaded assets.
#
# How it works:
#   1. load_texture(name) checks the cache first. If the texture is already
#      loaded it returns the existing one and increments its ref count.
#      This is the texture reuse / caching behaviour.
#   2. If not cached, it creates a new SimulatedTexture and stores it.
#   3. unload_texture(name) decrements the ref count. If it hits zero the
#      texture is removed from the cache entirely (memory freed).
#   4. unload_unused() sweeps the entire cache and removes anything with
#      ref_count == 0, simulating Unity's Resources.UnloadUnusedAssets().
# ---------------------------------------------------------------------------
class ResourceManager:

    # Predefined asset catalogue — simulates a real asset database.
    # Each entry defines: name, width, height, color
    ASSET_CATALOGUE = {
        "player_texture":   (64,  64,  (80,  180, 255)),
        "enemy_texture":    (48,  48,  (220, 60,  60 )),
        "bullet_texture":   (16,  16,  (255, 220, 50 )),
        "background_tile":  (128, 128, (25,  25,  45 )),
        "powerup_texture":  (32,  32,  (80,  220, 100)),
        "explosion_texture":(96,  96,  (255, 140, 0  )),
        "ui_panel":         (300, 160, (0,   0,   0  )),
    }

    def __init__(self):
        # The cache: maps asset name -> SimulatedTexture
        self._cache: dict[str, SimulatedTexture] = {}

        # Tracks total number of load and cache-hit events for the stats HUD
        self.total_loads      = 0    # actual allocations
        self.total_cache_hits = 0    # reuses (no allocation needed)
        self.total_unloads    = 0    # deallocations

        # Log of recent events shown in the performance panel
        self.event_log: list[str] = []

    # ── Public API ──────────────────────────────────────────────────────────

    def load_texture(self, name: str,
                     compression: float = SimulatedTexture.FULL) -> SimulatedTexture:
        """
        Load a texture by name.
        If it is already in the cache, return the cached version (cache hit).
        If not, allocate a new SimulatedTexture (cache miss / new allocation).
        """
        if name in self._cache:
            # CACHE HIT: texture already in memory, just add a reference
            tex = self._cache[name]
            tex.acquire()
            self.total_cache_hits += 1
            self._log(f"CACHE HIT  : {name}")
            return tex

        # CACHE MISS: texture not loaded yet, allocate it now (lazy loading)
        if name not in self.ASSET_CATALOGUE:
            raise ValueError(f"Unknown asset: {name}")

        w, h, color = self.ASSET_CATALOGUE[name]
        tex = SimulatedTexture(name, w, h, color, compression)
        tex.acquire()
        self._cache[name] = tex
        self.total_loads += 1
        self._log(f"LOADED     : {name} ({tex.memory_bytes // 1024} KB)")
        return tex

    def unload_texture(self, name: str):
        """
        Release one reference to a texture.
        If the ref count drops to zero, remove it from the cache entirely.
        This simulates calling Destroy() or unloading an AssetBundle in Unity.
        """
        if name not in self._cache:
            return
        tex = self._cache[name]
        tex.release()
        if tex.is_unused:
            del self._cache[name]
            self.total_unloads += 1
            self._log(f"UNLOADED   : {name}")

    def unload_unused(self):
        """
        Remove all textures with zero references in one sweep.
        This mirrors Unity's Resources.UnloadUnusedAssets() call.
        """
        to_remove = [name for name, tex in self._cache.items() if tex.is_unused]
        for name in to_remove:
            del self._cache[name]
            self.total_unloads += 1
            self._log(f"SWEPT      : {name}")
        if to_remove:
            self._log(f"--- sweep removed {len(to_remove)} asset(s) ---")

    def preload_scene(self, asset_names: list[str],
                      compression: float = SimulatedTexture.FULL):
        """
        Load a batch of assets upfront before gameplay begins.
        Simulates scene loading — all necessary assets allocated at once.
        """
        self._log("=== SCENE PRELOAD START ===")
        for name in asset_names:
            self.load_texture(name, compression)
        self._log("=== SCENE PRELOAD END ===")

    # ── Stats helpers ───────────────────────────────────────────────────────

    @property
    def cached_assets(self) -> int:
        return len(self._cache)

    @property
    def total_memory_bytes(self) -> int:
        return sum(t.memory_bytes for t in self._cache.values())

    @property
    def total_memory_kb(self) -> float:
        return self.total_memory_bytes / 1024

    def stats_snapshot(self) -> dict:
        return {
            "cached":      self.cached_assets,
            "memory_kb":   self.total_memory_kb,
            "loads":       self.total_loads,
            "cache_hits":  self.total_cache_hits,
            "unloads":     self.total_unloads,
            "assets":      {n: t.memory_bytes for n, t in self._cache.items()},
        }

    # ── Internal ────────────────────────────────────────────────────────────

    def _log(self, message: str):
        timestamp = time.perf_counter()
        entry = f"[{timestamp:.2f}s] {message}"
        self.event_log.append(entry)
        if len(self.event_log) > 20:
            self.event_log.pop(0)
