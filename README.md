# Memory Management Prototype
**GDT-110 | Week 3 Assignment**
**Student:** Levi
**Language:** Python 3.12 + Pygame

---

## GitHub Repository

https://github.com/JoeJeep/fps-prototype

## Video Demo

https://www.loom.com/share/a27ed17b3ae14f2f99067ce01043202c

---

## Project Overview

This prototype expands on the Week 2 FPS prototype to demonstrate four memory management techniques covered in the Week 3 simulation report on Unity's memory system. All concepts are implemented in Python using Pygame as the runtime environment.

The four systems demonstrated are:

1. Resource loading and unloading via a ResourceManager that tracks reference counts
2. Texture caching that reuses already-loaded assets instead of reallocating them
3. Object pooling that pre-allocates bullets and reuses them throughout gameplay
4. Performance comparison showing allocations saved, GC pauses avoided, and memory footprint

---

## How to Run

### Requirements

- Python 3.10, 3.11, or 3.12 (Pygame does not support Python 3.14 yet)
- Pygame library

### Install Pygame

```
pip install pygame
```

or if you have multiple Python versions:

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
| WASD / Arrow keys | Move player |
| SPACE | Shoot toward nearest enemy |
| TAB | Cycle FPS mode (30 / 60 / 480) |
| L | Load all catalogue textures into cache |
| U | Unload all unused textures (simulates scene transition) |
| P | Toggle performance stats panel |
| R (game over) | Restart |
| ESC (game over) | Quit |

---

## What to Observe

### Resource loading and caching
Press L to load all textures. Watch the "Cached" counter and KB value go up in the top-left HUD. Press L again and notice the cache hit ratio bar fills further — textures already in memory are reused, not reallocated.

### Unloading
Press U to sweep unused textures out of memory. Watch the cached asset count drop and the event log at the bottom-left show which assets were removed.

### Object pooling
Shoot repeatedly with SPACE and watch "Bullets: X active / Y pooled" in the HUD. The active count rises and pooled drops, but no new objects are ever created — they come from the pre-allocated pool of 60.

### Performance comparison panel
The bottom-right panel (toggle with P) shows a side-by-side comparison of what memory usage would look like without optimisation versus with. Key rows to watch are allocations, GC pauses simulated, and allocations avoided.

---

## File Structure

```
fps_prototype/
├── main.py               Game loop, player, enemies, HUD, rendering
├── object_pool.py        Bullet and BulletPool classes (object pooling)
├── resource_manager.py   Asset loading, caching, reference counting, unloading
├── performance_stats.py  Performance tracking and comparison overlay
└── README.md             This file
```

---

## Key Concepts Demonstrated

| Concept | Where in code | Unity equivalent |
|---|---|---|
| Lazy loading | resource_manager.py load_texture() | Resources.Load() |
| Texture caching | resource_manager.py _cache dict | Asset cache / AssetBundle |
| Reference counting | SimulatedTexture.ref_count | Object reference tracking |
| Unload unused | resource_manager.py unload_unused() | Resources.UnloadUnusedAssets() |
| Object pooling | object_pool.py BulletPool | Custom pool / Unity Pool API |
| GC pressure sim | performance_stats.py record_baseline_alloc() | Mono GC behaviour |

---

## References

Unity Technologies. (2024a). Memory management overview. Unity Documentation.
https://docs.unity3d.com/Manual/performance-memory-overview.html

Unity Technologies. (2024b). AssetBundles overview. Unity Documentation.
https://docs.unity3d.com/Manual/AssetBundlesIntro.html

Pygame Community. (2024). Pygame documentation.
https://www.pygame.org/docs/
