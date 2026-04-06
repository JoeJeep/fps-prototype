# FPS Optimization Prototype
**GDT-110 | Topic 2 Assignment**
**Student:** Levi
**Engine/Language:** Python 3 + Pygame

---

## 📌 Project Overview

This prototype demonstrates **frame rate optimization** as a core gameplay system mechanic, directly tied to the Topic 1 research report on *Frame Rate Optimization and Player Immersion in Fast-Paced Action Games*.

The prototype lets you **feel** the difference between 30 FPS, 60 FPS, and uncapped frame rates in real time while playing a simple action game. It also visually demonstrates **object pooling** — one of the key architectural techniques covered in the research report — by showing how bullets are reused from a pre-allocated pool instead of being created and destroyed every frame.

---

## 🎮 Gameplay Features

| Feature | Description |
|---|---|
| **Live FPS Counter** | Real-time FPS display with color coding (green/orange/red) |
| **FPS Mode Toggle** | Switch between 30, 60, and uncapped FPS mid-game with TAB |
| **FPS History Graph** | Mini line graph in the top-right showing frame rate over time |
| **Object Pooling** | Bullets drawn from a pre-allocated pool of 60 — HUD shows active vs. waiting |
| **Enemy Spawning** | Enemies spawn from screen edges and chase the player |
| **Shooting** | Aim with mouse, shoot with SPACE |
| **Score System** | Earn 10 points per enemy eliminated |

---

## 🖥️ How to Run

### Step 1 — Install Python
If you don't have Python installed:
1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download **Python 3.10 or newer**
3. During install, **check the box that says "Add Python to PATH"**

### Step 2 — Install Pygame
Open a terminal (Command Prompt or PowerShell on Windows, Terminal on Mac):
```
pip install pygame
```

### Step 3 — Download / Clone the Project
**Option A — Download ZIP:**
1. Click the green **Code** button on GitHub
2. Click **Download ZIP**
3. Extract the folder anywhere on your computer

**Option B — Clone with Git:**
```
git clone https://github.com/YOUR_USERNAME/fps-prototype.git
```

### Step 4 — Open in VS Code
1. Open **VS Code**
2. Click **File → Open Folder**
3. Select the `fps_prototype` folder you just extracted or cloned
4. You should see `main.py` and `object_pool.py` in the Explorer panel on the left

### Step 5 — Run the Game
**Option A — From VS Code terminal:**
1. Press **Ctrl + `** (backtick) to open the terminal inside VS Code
2. Type:
```
python main.py
```
3. Press Enter — the game window will open

**Option B — From your system terminal:**
1. Navigate to the folder:
```
cd path/to/fps_prototype
```
2. Run:
```
python main.py
```

---

## 🕹️ Controls

| Key | Action |
|---|---|
| **W A S D** or **Arrow Keys** | Move player |
| **SPACE** | Shoot toward nearest enemy |
| **TAB** | Cycle FPS mode (30 → 60 → Uncapped → 30) |
| **Close Window** | Quit |

---

## 📊 What to Observe

1. **Start at 60 FPS** (default) — movement feels smooth, enemies are manageable
2. **Press TAB to switch to 30 FPS** — notice the choppier movement and slower bullet response
3. **Press TAB again for Uncapped** — watch the FPS graph spike; on fast machines this can exceed 500+ FPS
4. **Watch the pool HUD** — as you shoot, "Active" bullets increase and "Pooled" bullets decrease. When bullets go off-screen, they return to the pool — no new objects are ever created mid-game

---

## 🗂️ File Structure

```
fps_prototype/
├── main.py          ← Main game loop, player, enemies, HUD, rendering
├── object_pool.py   ← Bullet and BulletPool classes (object pooling demo)
└── README.md        ← This file
```

---

## 🔗 GitHub Repository

[https://github.com/YOUR_USERNAME/fps-prototype](https://github.com/YOUR_USERNAME/fps-prototype)

*(Replace YOUR_USERNAME with your GitHub username after uploading)*

---

## 📹 Video Demo

[Insert your Loom / YouTube / Vimeo link here after recording]

---

## 📚 Concepts Demonstrated

- **Frame Rate Capping** — `clock.tick(fps)` enforces a frame budget, matching how Unreal, Unity, and Godot manage their render loops
- **Object Pooling** — Pre-allocated `BulletPool` avoids runtime memory allocation and garbage collection spikes (directly references the GC stutter issue discussed in the research report)
- **FPS Monitoring** — Live sampling mirrors the profiling tools in Unity's Frame Debugger and Unreal's Stat commands
- **Game/System Separation** — `object_pool.py` is a separate module from `main.py`, mirroring the architectural separation discussed across all five engines in the report

---

## 📖 References

Epic Games. (2024). *Rendering and graphics in Unreal Engine.* https://dev.epicgames.com/documentation/en-us/unreal-engine/rendering-and-graphics-in-unreal-engine

Unity Technologies. (2024). *Scriptable Render Pipeline.* https://docs.unity3d.com/Manual/ScriptableRenderPipeline.html

Pygame Community. (2024). *Pygame documentation.* https://www.pygame.org/docs/
