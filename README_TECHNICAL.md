# RVCE Campus Runner - Technical Documentation

A comprehensive educational game demonstrating Data Structures and Algorithms through campus navigation.

## Table of Contents
1. [How to Run](#how-to-run)
2. [Project Structure](#project-structure)
3. [Data Structures](#data-structures)
4. [Algorithms](#algorithms)
5. [Core Features](#core-features)
6. [Game Mechanics](#game-mechanics)
7. [Code Architecture](#code-architecture)
8. [Key Implementation Details](#key-implementation-details)

---

## How to Run

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/the-code-vortex/rvce-campus-runner.git
cd rvce-campus-runner

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

### Controls
| Key | Action |
|-----|--------|
| ↑↓←→ | Move player |
| B | Show BFS path |
| C | Clear path |
| H | Ask NPC for hint (-15 pts) |
| L | Ask Lab Assistant to clear construction (-5 pts) |
| G | Toggle grid display |
| P | Pause game |
| U | Undo last move |
| +/- | Zoom in/out |
| ESC | Exit fullscreen/Quit |

---

## Project Structure

```
rvce-campus-runner/
├── main.py              # Main game file (3200+ lines)
├── game_dynamics.py     # Dynamic game systems (NPCs, camera, fog, events)
├── game_screens.py      # UI screens (menu, how-to-play, high scores)
├── sound_effects.py     # Programmatic sound generation
├── requirements.txt     # Dependencies (pygame, numpy)
├── high_scores.json     # Persistent high score data
└── README.md            # Basic readme
```

---

## Data Structures

### 1. Graph (Adjacency List)
**File:** `main.py` - `RVCEGraph` class (lines 723-797)

**Implementation:**
```python
class RVCEGraph:
    def __init__(self):
        self.adj_list = {}  # Dictionary: node -> list of neighbors
        self.weights = {}   # Dictionary: (node1, node2) -> weight
```

**Why Used:**
- Represents the campus as a navigable graph
- Efficient O(1) neighbor lookup for pathfinding
- Supports weighted edges for different tile types

**Where Used:**
- BFS pathfinding traversal
- A* pathfinding (disabled but available)
- NPC movement planning

---

### 2. Queue (BFS Queue)
**File:** `main.py` - `BFSQueue` class (lines 698-722)

**Implementation:**
```python
class BFSQueue:
    def __init__(self):
        self.items = deque()  # Python's efficient double-ended queue
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        return self.items.popleft()  # O(1) operation
```

**Why Used:**
- FIFO (First-In-First-Out) order essential for BFS level-by-level exploration
- `deque` provides O(1) operations for both ends
- Guarantees shortest path in unweighted graphs

**Where Used:**
- `find_path_bfs()` - Main pathfinding function
- NPC movement pathfinding

---

### 3. Priority Queue (Min-Heap)
**File:** `main.py` - `PriorityQueue` class (lines 670-697)

**Implementation:**
```python
class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.entry_finder = {}
    
    def push(self, item, priority):
        heapq.heappush(self.heap, (priority, self.counter, item))
    
    def pop(self):
        return heapq.heappop(self.heap)[2]  # Returns item with lowest priority
```

**Why Used:**
- A* algorithm requires processing nodes by f-score (lowest first)
- Heap provides O(log n) push and O(log n) pop
- Entry finder enables efficient priority updates

**Where Used:**
- `find_path_astar()` - A* pathfinding (currently disabled)

---

### 4. Stack (Undo Stack)
**File:** `main.py` - `UndoStack` class (lines 798-824)

**Implementation:**
```python
class UndoStack:
    def __init__(self, max_size=50):
        self.stack = []
        self.max_size = max_size
    
    def push(self, state):
        self.stack.append(state)
        if len(self.stack) > self.max_size:
            self.stack.pop(0)  # Remove oldest if full
    
    def pop(self):
        return self.stack.pop() if self.stack else None
```

**Why Used:**
- LIFO (Last-In-First-Out) perfect for undo operations
- Limited size prevents memory issues
- Stores player position history

**Where Used:**
- Player movement (saves position before each move)
- U key undo functionality

---

### 5. 2D Grid Array
**File:** `main.py` - `GameMap` class (lines 631-669)

**Implementation:**
```python
class GameMap:
    def __init__(self, width, height):
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        # 0 = walkable, 1 = wall/blocked
```

**Why Used:**
- O(1) access to any grid cell
- Natural representation of 2D space
- Easy boundary checking

**Where Used:**
- Collision detection
- Pathfinding validity checks
- Building placement

---

### 6. Dictionary/Hash Map
**Used Throughout:**

| Variable | Purpose |
|----------|---------|
| `self.buildings` | Maps building name → (x, y) position |
| `self.building_icons` | Maps building name → pygame Surface |
| `self.tile_map` | 2D array of TileType enums |
| `TILE_PROPERTIES` | Maps TileType → properties dict |
| `parent` dict in BFS | Tracks path for reconstruction |

**Why Used:**
- O(1) average lookup time
- Flexible key-value associations
- Clean code organization

---

### 7. Enum Types
**File:** `game_dynamics.py` - Various enums

```python
class TileType(Enum):
    NORMAL = 0       # Regular walkable path
    WALL = 1         # Non-walkable
    ICE = 2          # Slide effect
    CONSTRUCTION = 8 # Temporarily blocked
    # ... more types

class NPCType(Enum):
    STUDENT = 1
    PROFESSOR = 3
    LAB_ASSISTANT = 4

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    # ... more states
```

**Why Used:**
- Type safety for state management
- Readable code vs magic numbers
- Easy state machine implementation

---

## Algorithms

### 1. Breadth-First Search (BFS)
**File:** `main.py` - `find_path_bfs()` (lines 1895-1930)

**How It Works:**
```
1. Start from player position
2. Add to queue, mark as visited
3. While queue not empty:
   a. Dequeue front node (current)
   b. If current == goal, reconstruct path
   c. For each unvisited neighbor:
      - Skip if CONSTRUCTION tile
      - Mark visited, record parent
      - Enqueue neighbor
4. Return path or empty list
```

**Complexity:**
- Time: O(V + E) where V = vertices, E = edges
- Space: O(V) for visited set and parent dict

**Why Used:**
- Guarantees shortest path in unweighted graphs
- Simple to understand and implement
- Explores level-by-level (distance-based)

**Visual Output:**
- Green path overlay on tiles
- Shows explored node count in console

---

### 2. A* Search (Disabled but Available)
**File:** `main.py` - `find_path_astar()` (lines 1932-1975)

**How It Works:**
```
1. Initialize open set (priority queue) with start
2. g_score[start] = 0, f_score[start] = heuristic(start, goal)
3. While open set not empty:
   a. Pop node with lowest f_score
   b. If current == goal, reconstruct path
   c. For each neighbor:
      - tentative_g = g_score[current] + edge_weight
      - If tentative_g < g_score[neighbor]:
        * Update g_score and f_score
        * Record parent
        * Add to open set
4. Return path or empty list
```

**Heuristic:** Manhattan distance
```python
def heuristic(self, a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
```

**Why Available:**
- More efficient than BFS for weighted graphs
- Can incorporate tile weights (ice = 0.5, grass = 2)
- Currently disabled per user request

---

### 3. Camera Follow Algorithm
**File:** `game_dynamics.py` - `Camera` class (lines 545-640)

**Implementation:**
```python
def update(self, target_x, target_y, dt):
    # Smooth exponential following
    self.x += (target_x - self.visible_width/2 - self.x) * self.follow_speed * dt
    self.y += (target_y - self.visible_height/2 - self.y) * self.follow_speed * dt
    
    # Smooth zoom interpolation
    self.zoom += (self.target_zoom - self.zoom) * self.follow_speed * dt
```

**Why Used:**
- Smooth player-following camera
- Prevents jarring view changes
- Supports zoom functionality

---

### 4. Fog of War Algorithm
**File:** `game_dynamics.py` - `FogOfWar` class (lines 643-700)

**How It Works:**
- 3-state grid: unexplored (0), explored (1), visible (2)
- Updates visibility radius around player each move
- Alpha blending for smooth fog edges

---

## Core Features

### 1. Task/Riddle System
**File:** `main.py` - `TaskManager` class, `RIDDLE_BANK`

- Random building assignment
- Difficulty-based riddles (easy/normal/hard)
- Tracks completion and scoring

### 2. Scoring System
| Action | Points |
|--------|--------|
| Visit building | +50 |
| No pathfinding used | +20 |
| Optimal path taken | +30 |
| Using hint | -15 |
| Lab Assistant help | -5 |

### 3. Runner Titles
| Score Range | Title |
|-------------|-------|
| 0-249 | Fresher |
| 250-599 | Sophomore |
| 600-799 | Senior |
| 800+ | Super Senior |

### 4. NPC System
**File:** `game_dynamics.py` - `NPC`, `NPCManager` classes

- **Types:** Student, Security, Professor, Lab Assistant
- **Behavior:** Patrol between buildings using pathfinding
- **Interaction:** Hints (Prof/Student), Construction clearing (Lab Asst)

### 5. Construction Obstacles
**File:** `main.py` - `_update_construction_events()`, `_spawn_construction_site()`

- Random spawning every 30-60 seconds
- Blocks 2-4 adjacent tiles
- Auto-clears after 45 seconds
- BFS automatically reroutes

### 6. Special Tiles
| Tile | Effect |
|------|--------|
| Ice | Slide extra cells |
| Portal | Teleport to paired portal |
| Trap | Time penalty |
| Booster | Speed burst |

---

## Code Architecture

### Main Game Loop
```python
def run(self):
    while self.running:
        dt = self.clock.tick(60) / 1000.0  # 60 FPS
        self.handle_events()
        self.update(dt)
        self.draw()
        pygame.display.flip()
```

### State Machine
```
MENU → DIFFICULTY_SELECT → NAME_ENTRY → PLAYING ↔ PAUSED
                                          ↓
                                    VICTORY / GAME_OVER
```

### File Responsibilities

| File | Responsibility |
|------|----------------|
| `main.py` | Core game logic, rendering, pathfinding, state management |
| `game_dynamics.py` | Reusable systems (NPCs, camera, fog, tiles, events) |
| `game_screens.py` | UI screens, buttons, high score management |
| `sound_effects.py` | Programmatic sound generation using numpy |

---

## Key Implementation Details

### 1. Programmatic Asset Generation
All game assets (icons, textures, sprites) are generated programmatically in code - no external image files needed. This ensures:
- Portability
- Exam safety (no asset dependencies)
- Easy customization

### 2. Dynamic Map Rendering
- Roads: Dark gray with lane markings (walkable)
- Grass: Green with texture dots (non-walkable)
- Buildings: Icons with shadow for depth
- Grid: Toggleable with G key

### 3. Full Screen Mode
Uses `pygame.FULLSCREEN` flag with dynamic display size detection.

### 4. High Score Persistence
Scores saved to `high_scores.json` with player name, score, and difficulty.

### 5. Sound System
Optional numpy-based sound generation for:
- Footsteps, victory jingles, alerts
- Works without external audio files

---

## Performance Considerations

1. **BFS Optimization:** Early exit on goal found
2. **Camera Culling:** Only render visible tiles
3. **Efficient Data Structures:** deque for O(1) queue operations
4. **60 FPS Target:** Frame-rate independent movement using delta time

---

## Dependencies

```
pygame>=2.0.0    # Game framework
numpy>=1.20.0    # Sound generation (optional)
```

---

## License

Educational project for RVCE campus exploration and DSA learning.

---

*Documentation generated for RVCE Campus Runner v1.0*
