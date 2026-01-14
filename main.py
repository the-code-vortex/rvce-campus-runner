import pygame
import sys
import heapq
from collections import deque, defaultdict
from enum import Enum
import math
import random

# ==================== ASSET GENERATOR ====================
class AssetGenerator:
    """Programmatically generate all game assets - exam-safe, no external files needed"""
    
    @staticmethod
    def create_building_icon(icon_type, size=64):
        """Generate building icons using shapes and colors"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if icon_type == "admin":
            # Document/clipboard icon
            pygame.draw.rect(surface, (255, 255, 255), (15, 10, 34, 44), border_radius=3)
            pygame.draw.rect(surface, (100, 150, 255), (15, 10, 34, 44), 2, border_radius=3)
            for i in range(3):
                pygame.draw.line(surface, (100, 150, 255), (20, 20 + i*8), (44, 20 + i*8), 2)
                
        elif icon_type == "library":
            # Book icon
            pygame.draw.rect(surface, (200, 100, 50), (18, 15, 28, 34), border_radius=2)
            pygame.draw.rect(surface, (150, 70, 30), (18, 15, 28, 34), 2, border_radius=2)
            pygame.draw.line(surface, (255, 200, 150), (32, 15), (32, 49), 2)
            for i in range(4):
                pygame.draw.line(surface, (150, 70, 30), (20, 20 + i*7), (44, 20 + i*7), 1)
                
        elif icon_type == "food":
            # Fork and knife icon
            pygame.draw.rect(surface, (200, 200, 200), (22, 15, 3, 30))  # Fork handle
            pygame.draw.rect(surface, (200, 200, 200), (39, 15, 3, 30))  # Knife handle
            for i in range(3):
                pygame.draw.rect(surface, (200, 200, 200), (20 + i*3, 10, 2, 8))  # Fork prongs
            pygame.draw.polygon(surface, (220, 220, 220), [(39, 10), (42, 10), (40.5, 15)])  # Knife tip
            
        elif icon_type == "hostel":
            # Bed icon
            pygame.draw.rect(surface, (150, 100, 200), (12, 25, 40, 20), border_radius=3)
            pygame.draw.circle(surface, (180, 130, 220), (20, 20), 6)  # Pillow
            pygame.draw.rect(surface, (120, 80, 160), (10, 45, 4, 10))  # Leg
            pygame.draw.rect(surface, (120, 80, 160), (50, 45, 4, 10))  # Leg
            
        elif icon_type == "lab":
            # Beaker/flask icon
            pygame.draw.polygon(surface, (100, 200, 255), [(28, 15), (36, 15), (40, 45), (24, 45)])
            pygame.draw.rect(surface, (80, 160, 200), (24, 35, 16, 10))  # Liquid
            pygame.draw.circle(surface, (100, 200, 255), (32, 12), 3)  # Stopper
            
        elif icon_type == "innovation":
            # Lightbulb icon
            pygame.draw.circle(surface, (255, 220, 100), (32, 25), 12)
            pygame.draw.rect(surface, (200, 200, 200), (28, 37, 8, 12), border_radius=2)
            pygame.draw.line(surface, (255, 240, 150), (26, 25), (38, 25), 2)
            
        elif icon_type == "computer":
            # Computer/monitor icon
            pygame.draw.rect(surface, (100, 100, 100), (16, 15, 32, 24), border_radius=2)
            pygame.draw.rect(surface, (150, 200, 255), (18, 17, 28, 20))  # Screen
            pygame.draw.rect(surface, (80, 80, 80), (28, 39, 8, 8))  # Stand
            
        elif icon_type == "default":
            # Generic building icon
            pygame.draw.rect(surface, (150, 150, 200), (16, 20, 32, 28), border_radius=3)
            pygame.draw.rect(surface, (100, 150, 255), (22, 26, 8, 8))  # Window
            pygame.draw.rect(surface, (100, 150, 255), (34, 26, 8, 8))  # Window
            pygame.draw.rect(surface, (80, 80, 120), (28, 38, 8, 10))  # Door
            
        return surface
    
    @staticmethod
    def create_player_sprite(frame=0, size=32):
        """Generate animated player sprite"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Body (circle)
        bounce = math.sin(frame * 0.3) * 2 if frame > 0 else 0
        center_y = size // 2 - int(bounce)
        
        # Shadow
        shadow = pygame.Surface((size, size // 4), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80), (4, 0, size - 8, size // 4))
        surface.blit(shadow, (0, size - size // 4))
        
        # Body
        pygame.draw.circle(surface, (255, 100, 100), (size // 2, center_y), size // 3)
        pygame.draw.circle(surface, (255, 150, 150), (size // 2, center_y), size // 3, 2)
        
        # Eyes
        eye_offset = 2 if frame % 2 == 0 else 0
        pygame.draw.circle(surface, (50, 50, 50), (size // 2 - 4, center_y - 2), 2)
        pygame.draw.circle(surface, (50, 50, 50), (size // 2 + 4, center_y - 2), 2)
        
        return surface
    
    @staticmethod
    def create_texture(texture_type, size=32):
        """Generate tileable textures"""
        surface = pygame.Surface((size, size))
        
        if texture_type == "brick":
            # Brick pattern
            surface.fill((120, 80, 100))
            for y in range(0, size, 8):
                offset = 16 if (y // 8) % 2 == 0 else 0
                for x in range(-16 + offset, size, 16):
                    pygame.draw.rect(surface, (100, 60, 80), (x, y, 14, 6))
                    
        elif texture_type == "path":
            # Stone/concrete path
            surface.fill((60, 65, 80))
            for _ in range(20):
                x, y = random.randint(0, size-1), random.randint(0, size-1)
                c = random.randint(50, 70)
                pygame.draw.circle(surface, (c, c+5, c+10), (x, y), 1)
                
        return surface
    
    @staticmethod
    def create_particle(color, size=4):
        """Create particle for effects"""
        surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (size, size), size)
        return surface

# Data Structure 1: 2D Array for RVCE campus grid
class RVCEGameMap:
    def __init__(self, width, height):
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height
        self.cell_size = 35
        
    def load_rvce_map(self, map_data):
        for y, row in enumerate(map_data):
            for x, cell in enumerate(row):
                self.grid[y][x] = cell
                
    def is_walkable(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] != 1
        return False
    
    def get_cell_value(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return 1

# Data Structure 2: Graph for navigation
class RVCEGraph:
    def __init__(self):
        self.adj_list = defaultdict(list)
        self.weights = {}
        
    def add_edge(self, u, v, weight=1):
        self.adj_list[u].append(v)
        self.adj_list[v].append(u)
        self.weights[(u, v)] = weight
        self.weights[(v, u)] = weight
        
    def build_from_rvce_grid(self, game_map):
        """Build graph from walkable paths in RVCE campus"""
        for y in range(game_map.height):
            for x in range(game_map.width):
                if game_map.is_walkable(x, y):
                    current = (x, y)
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < game_map.width and 
                            0 <= ny < game_map.height and 
                            game_map.is_walkable(nx, ny)):
                            weight = 1
                            self.add_edge(current, (nx, ny), weight)

# Data Structure 3: Queue for BFS
class BFSQueue:
    def __init__(self):
        self.queue = deque()
        
    def enqueue(self, item):
        self.queue.append(item)
        
    def dequeue(self):
        return self.queue.popleft() if self.queue else None
        
    def is_empty(self):
        return len(self.queue) == 0

# Data Structure 4: Priority Queue for A*
class PriorityQueue:
    def __init__(self):
        self.heap = []
        
    def push(self, item, priority):
        heapq.heappush(self.heap, (priority, item))
        
    def pop(self):
        if self.heap:
            priority, item = heapq.heappop(self.heap)
            return item
        return None
        
    def is_empty(self):
        return len(self.heap) == 0

# Data Structure 5: Stack for undo functionality
class UndoStack:
    def __init__(self, max_size=50):
        self.stack = []
        self.max_size = max_size
        
    def push(self, state):
        if len(self.stack) >= self.max_size:
            self.stack.pop(0)
        self.stack.append(state)
        
    def pop(self):
        return self.stack.pop() if self.stack else None
        
    def is_empty(self):
        return len(self.stack) == 0

# Data Structure 6: Hash Map for tasks and buildings
class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.completed_tasks = set()
        self.current_task = None
        self.task_queue = deque()
        
    def add_task(self, task_id, task_data):
        self.tasks[task_id] = task_data
        
    def assign_task(self, task_id):
        if task_id in self.tasks and task_id not in self.completed_tasks:
            self.current_task = self.tasks[task_id]
            return True
        return False
    
    def complete_task(self, task_id):
        if task_id == self.current_task['id']:
            self.completed_tasks.add(task_id)
            self.current_task = None
            return True
        return False
    
    def get_next_task(self):
        """Get a random uncompleted task"""
        available_tasks = [task_id for task_id in self.tasks 
                          if task_id not in self.completed_tasks]
        if available_tasks:
            return random.choice(available_tasks)
        return None

# Game State Enum
class GameState(Enum):
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4

# Particle system for visual effects
class Particle:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.life = 1.0
        self.size = random.randint(2, 5)
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 200 * dt  # Gravity
        self.life -= dt * 2
        return self.life > 0
    
    def draw(self, screen):
        alpha = int(self.life * 255)
        color = (*self.color[:3], alpha)
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class RVCECampusRunner:
    def __init__(self):
        pygame.init()
        # Fullscreen mode
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        pygame.display.set_caption("RVCE Campus Runner - Pathfinding Adventure")
        self.clock = pygame.time.Clock()
        
        # Professional fonts
        self.font = pygame.font.SysFont('Segoe UI', 16)
        self.large_font = pygame.font.SysFont('Segoe UI', 22, bold=True)
        self.title_font = pygame.font.SysFont('Segoe UI', 32, bold=True)
        self.small_font = pygame.font.SysFont('Segoe UI', 14)
        self.huge_font = pygame.font.SysFont('Segoe UI', 48, bold=True)
        
        # Animation variables
        self.animation_time = 0
        self.pulse_offset = 0
        self.player_frame = 0
        self.path_animation = 0
        
        # Particle system
        self.particles = []
        
        # Generate all assets
        self.load_assets()
        
        self.reset_game()
        
    def load_assets(self):
        """Generate all visual assets programmatically"""
        print("Generating game assets...")
        
        # Building icons
        self.building_icons = {
            "Admin Block": AssetGenerator.create_building_icon("admin"),
            "Library": AssetGenerator.create_building_icon("library"),
            "Food Court (MINGOS)": AssetGenerator.create_building_icon("food"),
            "Boys Hostel": AssetGenerator.create_building_icon("hostel"),
            "DTL Innovation Hub": AssetGenerator.create_building_icon("innovation"),
            "AI-ML & MCA Dept": AssetGenerator.create_building_icon("lab"),
            "Mechanical Dept": AssetGenerator.create_building_icon("computer"),
            "BT Quadrangle": AssetGenerator.create_building_icon("lab"),
            "BT & EIE Dept": AssetGenerator.create_building_icon("computer"),
            "IEM Dept": AssetGenerator.create_building_icon("computer"),
            "EEE Dept": AssetGenerator.create_building_icon("computer"),
            "CSE Dept": AssetGenerator.create_building_icon("computer"),
            "ECE Dept": AssetGenerator.create_building_icon("computer"),
            "Main Gate": AssetGenerator.create_building_icon("default"),
            "Incubation Center": AssetGenerator.create_building_icon("innovation"),
        }
        
        # Player sprites (animation frames)
        self.player_sprites = [
            AssetGenerator.create_player_sprite(i) for i in range(4)
        ]
        
        # Textures
        self.brick_texture = AssetGenerator.create_texture("brick")
        self.path_texture = AssetGenerator.create_texture("path")
        
        print("✓ Assets generated successfully!")
        
    def reset_game(self):
        """Properly reset the game state"""
        # Initialize data structures
        self.game_map = RVCEGameMap(20, 18)
        self.nav_graph = RVCEGraph()
        self.undo_stack = UndoStack()
        self.task_manager = TaskManager()
        
        # Calculate cell size
        map_area_width = self.screen_width - 500
        map_area_height = self.screen_height - 100
        self.game_map.cell_size = min(map_area_width // 20, map_area_height // 18)
        
        # Game state
        self.state = GameState.PLAYING
        self.player_pos = (2, 15)
        self.score = 0
        self.time_remaining = 300
        self.last_time = pygame.time.get_ticks()
        
        self.current_path = []
        self.path_algorithm = "BFS"
        self.algorithm_stats = {"BFS": 0, "A*": 0}
        
        # Clear particles
        self.particles = []
        
        self.setup_rvce_campus()
        self.setup_academic_tasks()
        
    def setup_rvce_campus(self):
        map_data = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,1,1,1,0,0,0,1,1,1,0,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,0,1,0,1,0,1,0,1,1,0,1],
            [1,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1],
            [1,0,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1],
            [1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1],
            [1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,1],
            [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,1],
            [1,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
            [1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,1],
            [1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1],
            [1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1],
            [1,1,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        
        self.game_map.load_rvce_map(map_data)
        self.nav_graph.build_from_rvce_grid(self.game_map)
        
        # Building locations - ON WALKABLE PATHS
        self.buildings = {
            "Main Gate": (2, 15),
            "Admin Block": (3, 3),
            "DTL Innovation Hub": (6, 3),
            "Mechanical Dept": (11, 3),
            "BT Quadrangle": (7, 5),
            "AI-ML & MCA Dept": (14, 5),
            "BT & EIE Dept": (16, 7),
            "IEM Dept": (4, 7),
            "EEE Dept": (9, 7),
            "CSE Dept": (14, 9),
            "ECE Dept": (7, 11),
            "Library": (11, 13),
            "Food Court (MINGOS)": (4, 13),
            "Boys Hostel": (16, 15),
            "Incubation Center": (13, 15)
        }
        
    def setup_academic_tasks(self):
        tasks = {
            "task1": {
                "id": "task1",
                "name": "First Day Orientation",
                "building": "Admin Block",
                "riddle": "Where new beginnings start, paperwork and IDs you'll get.\nFind the building where all students first met!",
                "points": 50,
                "hint": "Head to the administrative heart of RVCE"
            },
            "task2": {
                "id": "task2", 
                "name": "Collect Syllabus",
                "building": "BT Quadrangle",
                "riddle": "For Biotech dreams, where formulas unfold,\nGet your syllabus, future stories to be told!",
                "points": 75,
                "hint": "Find the building for Biotechnology studies"
            },
            "task3": {
                "id": "task3",
                "name": "AI Lab Session", 
                "building": "AI-ML & MCA Dept",
                "riddle": "Where machines learn and algorithms play,\nAttend your first AI lab session today!",
                "points": 100,
                "hint": "Look for the department of Artificial Intelligence"
            },
            "task4": {
                "id": "task4",
                "name": "Library Research",
                "building": "Library", 
                "riddle": "Silent knowledge, books galore,\nResearch for projects, always learn more!",
                "points": 80,
                "hint": "Find the building with the most books"
            },
            "task5": {
                "id": "task5",
                "name": "Lunch Break",
                "building": "Food Court (MINGOS)", 
                "riddle": "Hungry from studies, need some fuel,\nFind the place that's really cool!",
                "points": 60,
                "hint": "Time for food at the popular eating spot"
            },
            "task6": {
                "id": "task6",
                "name": "Innovation Workshop",
                "building": "DTL Innovation Hub",
                "riddle": "Where ideas spark and startups grow,\nAttend a workshop, your skills to show!",
                "points": 90,
                "hint": "Visit the innovation and entrepreneurship center"
            },
            "task7": {
                "id": "task7",
                "name": "Hostel Check-in", 
                "building": "Boys Hostel",
                "riddle": "Day is ending, sun's going down,\nFind your room in campus town!",
                "points": 70,
                "hint": "Head to your accommodation for the night"
            }
        }
        
        for task_id, task_data in tasks.items():
            self.task_manager.add_task(task_id, task_data)
        
        first_task = self.task_manager.get_next_task()
        if first_task:
            self.task_manager.assign_task(first_task)
    
    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def find_path_bfs(self, start, goal):
        """BFS Algorithm"""
        visited = set()
        parent = {}
        nodes_explored = 0
        
        bfs_queue = BFSQueue()
        bfs_queue.enqueue(start)
        visited.add(start)
        
        while not bfs_queue.is_empty():
            current = bfs_queue.dequeue()
            nodes_explored += 1
            
            if current == goal:
                path = []
                while current in parent:
                    path.append(current)
                    current = parent[current]
                path.append(start)
                self.algorithm_stats["BFS"] = nodes_explored
                return path[::-1]
            
            for neighbor in self.nav_graph.adj_list[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    bfs_queue.enqueue(neighbor)
        
        self.algorithm_stats["BFS"] = nodes_explored
        return []
    
    def find_path_astar(self, start, goal):
        """A* Algorithm"""
        open_set = PriorityQueue()
        open_set.push(start, 0)
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        nodes_explored = 0
        
        while not open_set.is_empty():
            current = open_set.pop()
            nodes_explored += 1
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                self.algorithm_stats["A*"] = nodes_explored
                return path[::-1]
            
            for neighbor in self.nav_graph.adj_list[current]:
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)
                    open_set.push(neighbor, f_score[neighbor])
        
        self.algorithm_stats["A*"] = nodes_explored
        return []
    
    def spawn_celebration_particles(self, x, y):
        """Spawn particles for task completion"""
        colors = [(255, 215, 0), (255, 255, 100), (255, 200, 50)]
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 100
            color = random.choice(colors)
            self.particles.append(Particle(x, y, color, (vx, vy)))
    
    def check_task_completion(self):
        if not self.task_manager.current_task:
            return
            
        current_task = self.task_manager.current_task
        target_building = current_task['building']
        
        if target_building in self.buildings:
            target_pos = self.buildings[target_building]
            
            if self.player_pos == target_pos:
                # Task completed - spawn celebration!
                map_offset_x = 50
                map_offset_y = (self.screen_height - self.game_map.height * self.game_map.cell_size) // 2
                px = target_pos[0] * self.game_map.cell_size + map_offset_x + self.game_map.cell_size // 2
                py = target_pos[1] * self.game_map.cell_size + map_offset_y + self.game_map.cell_size // 2
                self.spawn_celebration_particles(px, py)
                
                print(f"✓ Task Completed: {current_task['name']} (+{current_task['points']} points)")
                self.score += current_task['points']
                self.task_manager.complete_task(current_task['id'])
                self.current_path = []
                
                next_task = self.task_manager.get_next_task()
                if next_task:
                    self.task_manager.assign_task(next_task)
                    print(f"New task assigned: {self.task_manager.current_task['name']}")
                else:
                    print("All tasks completed! Victory!")
                    self.state = GameState.VICTORY
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                if self.state == GameState.PLAYING:
                    # Handle movement keys
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        self.undo_stack.push({
                            'position': self.player_pos,
                            'score': self.score
                        })
                        
                        x, y = self.player_pos
                        new_x, new_y = x, y
                        
                        if event.key == pygame.K_UP:
                            new_y -= 1
                        elif event.key == pygame.K_DOWN:
                            new_y += 1
                        elif event.key == pygame.K_LEFT:
                            new_x -= 1
                        elif event.key == pygame.K_RIGHT:
                            new_x += 1
                        
                        if self.game_map.is_walkable(new_x, new_y):
                            self.player_pos = (new_x, new_y)
                            self.player_frame += 1
                            self.check_task_completion()
                    
                    # Handle other commands
                    elif event.key == pygame.K_u:
                        self.undo_move()
                    elif event.key == pygame.K_b:
                        if self.task_manager.current_task:
                            target = self.buildings[self.task_manager.current_task['building']]
                            self.current_path = self.find_path_bfs(self.player_pos, target)
                            self.path_algorithm = "BFS"
                            print(f"✓ BFS Path: {len(self.current_path)} cells, {self.algorithm_stats['BFS']} nodes explored")
                    elif event.key == pygame.K_a:
                        if self.task_manager.current_task:
                            target = self.buildings[self.task_manager.current_task['building']]
                            self.current_path = self.find_path_astar(self.player_pos, target)
                            self.path_algorithm = "A*"
                            print(f"✓ A* Path: {len(self.current_path)} cells, {self.algorithm_stats['A*']} nodes explored")
                    elif event.key == pygame.K_c:
                        self.current_path = []
                    elif event.key == pygame.K_p:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_n:
                        next_task = self.task_manager.get_next_task()
                        if next_task:
                            self.task_manager.assign_task(next_task)
                            self.current_path = []
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        return True
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_p:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        return True
                elif self.state == GameState.VICTORY or self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        return True
        
        return True
    
    def undo_move(self):
        previous_state = self.undo_stack.pop()
        if previous_state:
            self.player_pos = previous_state['position']
            self.score = previous_state['score']
    
    def update(self):
        dt = self.clock.get_time() / 1000.0
        
        if self.state != GameState.PLAYING:
            return
            
        # Update timer
        current_time = pygame.time.get_ticks()
        if current_time - self.last_time > 1000:
            self.time_remaining -= 1
            self.last_time = current_time
            
            if self.time_remaining <= 0:
                self.state = GameState.GAME_OVER
        
        # Update animations
        self.animation_time = current_time / 1000.0
        self.pulse_offset = math.sin(self.animation_time * 3) * 3
        self.path_animation = (self.path_animation + 1) % 60
        
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw_gradient_background(self):
        for y in range(self.screen_height):
            progress = y / self.screen_height
            r = int(10 + progress * 15)
            g = int(15 + progress * 20)
            b = int(30 + progress * 25)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
    
    def draw(self):
        # Background
        self.draw_gradient_background()
        
        # Calculate map offset
        map_width = self.game_map.width * self.game_map.cell_size
        map_height = self.game_map.height * self.game_map.cell_size
        map_offset_x = 50
        map_offset_y = (self.screen_height - map_height) // 2
        
        # Draw map shadow
        shadow_rect = pygame.Rect(map_offset_x + 5, map_offset_y + 5, map_width, map_height)
        shadow_surface = pygame.Surface((map_width, map_height))
        shadow_surface.set_alpha(100)
        shadow_surface.fill((0, 0, 0))
        self.screen.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))
        
        # Draw campus map with textures
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                rect = pygame.Rect(
                    x * self.game_map.cell_size + map_offset_x,
                    y * self.game_map.cell_size + map_offset_y,
                    self.game_map.cell_size,
                    self.game_map.cell_size
                )
                
                cell_value = self.game_map.get_cell_value(x, y)
                if cell_value == 1:
                    # Buildings with brick texture
                    texture = pygame.transform.scale(self.brick_texture, (self.game_map.cell_size, self.game_map.cell_size))
                    self.screen.blit(texture, rect.topleft)
                else:
                    # Paths with stone texture
                    texture = pygame.transform.scale(self.path_texture, (self.game_map.cell_size, self.game_map.cell_size))
                    self.screen.blit(texture, rect.topleft)
                
                pygame.draw.rect(self.screen, (20, 25, 35), rect, 1)
        
        # Draw animated path
        if len(self.current_path) > 0:
            path_color = (50, 255, 100) if self.path_algorithm == "BFS" else (100, 150, 255)
            
            for i, pos in enumerate(self.current_path):
                x, y = pos
                rect = pygame.Rect(
                    x * self.game_map.cell_size + map_offset_x,
                    y * self.game_map.cell_size + map_offset_y,
                    self.game_map.cell_size,
                    self.game_map.cell_size
                )
                
                # Animated glow
                anim_offset = (self.path_animation - i * 3) % 60
                alpha = int(100 + 50 * math.sin(anim_offset / 10))
                
                path_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                path_surface.fill((*path_color, alpha))
                self.screen.blit(path_surface, rect.topleft)
                
                # Border
                pygame.draw.rect(self.screen, path_color, rect, 2)
        
        # Draw buildings with icons
        for name, pos in self.buildings.items():
            x, y = pos
            rect = pygame.Rect(
                x * self.game_map.cell_size + map_offset_x,
                y * self.game_map.cell_size + map_offset_y,
                self.game_map.cell_size,
                self.game_map.cell_size
            )
            
            is_target = (self.task_manager.current_task and 
                        self.task_manager.current_task['building'] == name)
            
            if is_target:
                # Pulsing glow
                pulse_size = int(self.pulse_offset)
                glow_rect = rect.inflate(12 + pulse_size, 12 + pulse_size)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                glow_surface.fill((255, 200, 0, 120))
                self.screen.blit(glow_surface, (glow_rect.x, glow_rect.y))
                
                # Yellow background
                pygame.draw.rect(self.screen, (255, 220, 50), rect, border_radius=4)
            else:
                # Subtle background
                pygame.draw.rect(self.screen, (80, 70, 120), rect, border_radius=4)
            
            # Draw icon
            if name in self.building_icons:
                icon = self.building_icons[name]
                icon_scaled = pygame.transform.scale(icon, (self.game_map.cell_size - 8, self.game_map.cell_size - 8))
                self.screen.blit(icon_scaled, (rect.x + 4, rect.y + 4))
        
        # Draw player with animation
        x, y = self.player_pos
        player_rect = pygame.Rect(
            x * self.game_map.cell_size + map_offset_x,
            y * self.game_map.cell_size + map_offset_y,
            self.game_map.cell_size,
            self.game_map.cell_size
        )
        
        # Get animated sprite
        sprite_index = (self.player_frame // 5) % len(self.player_sprites)
        player_sprite = pygame.transform.scale(self.player_sprites[sprite_index], 
                                               (self.game_map.cell_size, self.game_map.cell_size))
        self.screen.blit(player_sprite, player_rect.topleft)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        self.draw_dashboard(map_offset_x, map_width)
        pygame.display.flip()
    
    def draw_dashboard(self, map_offset_x, map_width):
        # Dashboard positioning
        dashboard_x = map_offset_x + map_width + 30
        dashboard_width = self.screen_width - dashboard_x - 30
        dashboard_rect = pygame.Rect(dashboard_x, 30, dashboard_width, self.screen_height - 60)
        
        # Dashboard background
        dashboard_surface = pygame.Surface((dashboard_width, self.screen_height - 60))
        for y in range(self.screen_height - 60):
            progress = y / (self.screen_height - 60)
            r = int(25 + progress * 10)
            g = int(30 + progress * 10)
            b = int(50 + progress * 15)
            pygame.draw.line(dashboard_surface, (r, g, b), (0, y), (dashboard_width, y))
        self.screen.blit(dashboard_surface, (dashboard_x, 30))
        
        pygame.draw.rect(self.screen, (70, 80, 120), dashboard_rect, 3, border_radius=15)
        
        x_offset = dashboard_x + 20
        y_offset = 50
        
        # Title
        title = self.huge_font.render("RVCE", True, (100, 200, 255))
        self.screen.blit(title, (x_offset, y_offset))
        y_offset += 55
        
        subtitle = self.large_font.render("Campus Runner", True, (200, 220, 255))
        self.screen.blit(subtitle, (x_offset, y_offset))
        y_offset += 50
        
        # Score card
        self.draw_card(x_offset - 10, y_offset - 5, dashboard_width - 20, 40, (40, 50, 70))
        score_text = self.large_font.render(f"⭐ SCORE: {self.score}", True, (255, 220, 100))
        self.screen.blit(score_text, (x_offset, y_offset))
        y_offset += 50
        
        # Time card with progress
        time_color = (100, 255, 150) if self.time_remaining > 60 else (255, 100, 100)
        time_text = self.large_font.render(f"⏱ TIME: {self.time_remaining}s", True, time_color)
        self.screen.blit(time_text, (x_offset, y_offset))
        y_offset += 35
        
        # Time progress bar
        bar_width = dashboard_width - 40
        bar_height = 15
        progress = max(0, self.time_remaining / 300)
        self.draw_progress_bar(x_offset, y_offset, bar_width, bar_height, progress, time_color)
        y_offset += 40
        
        # Separator
        pygame.draw.line(self.screen, (60, 70, 100), (x_offset, y_offset), 
                        (x_offset + dashboard_width - 40, y_offset), 2)
        y_offset += 25
        
        # Algorithm section
        algo_title = self.large_font.render("🔍 PATHFINDING", True, (150, 200, 255))
        self.screen.blit(algo_title, (x_offset, y_offset))
        y_offset += 35
        
        bfs_color = (100, 255, 150) if self.path_algorithm == "BFS" else (100, 100, 100)
        astar_color = (150, 180, 255) if self.path_algorithm == "A*" else (100, 100, 100)
        
        bfs_text = self.font.render("● BFS (B) - Green", True, bfs_color)
        self.screen.blit(bfs_text, (x_offset, y_offset))
        y_offset += 25
        
        astar_text = self.font.render("● A* (A) - Blue", True, astar_color)
        self.screen.blit(astar_text, (x_offset, y_offset))
        y_offset += 25
        
        if self.current_path:
            self.draw_card(x_offset - 5, y_offset - 3, dashboard_width - 30, 45, (40, 60, 40))
            active_text = self.font.render(f"✓ {self.path_algorithm} ACTIVE", True, (150, 255, 150))
            self.screen.blit(active_text, (x_offset, y_offset))
            y_offset += 22
            
            stats_text = self.small_font.render(
                f"{len(self.current_path)} cells | {self.algorithm_stats[self.path_algorithm]} nodes", 
                True, (180, 220, 180))
            self.screen.blit(stats_text, (x_offset, y_offset))
            y_offset += 28
        else:
            no_path = self.small_font.render("Press B or A to show path", True, (120, 120, 120))
            self.screen.blit(no_path, (x_offset, y_offset))
            y_offset += 25
        
        y_offset += 15
        
        # Current Mission
        pygame.draw.line(self.screen, (60, 70, 100), (x_offset, y_offset), 
                        (x_offset + dashboard_width - 40, y_offset), 2)
        y_offset += 25
        
        mission_title = self.large_font.render("🎯 MISSION", True, (255, 200, 100))
        self.screen.blit(mission_title, (x_offset, y_offset))
        y_offset += 35
        
        if self.task_manager.current_task:
            task = self.task_manager.current_task
            
            self.draw_card(x_offset - 10, y_offset - 5, dashboard_width - 20, 30, (50, 60, 80))
            task_name = self.font.render(task['name'], True, (150, 255, 150))
            self.screen.blit(task_name, (x_offset, y_offset))
            y_offset += 40
            
            # Riddle
            riddle_lines = task['riddle'].split('\n')
            for line in riddle_lines:
                riddle_text = self.small_font.render(line, True, (255, 255, 180))
                self.screen.blit(riddle_text, (x_offset, y_offset))
                y_offset += 20
            
            y_offset += 10
            
            building_text = self.font.render(f"📍 {task['building']}", True, (150, 180, 255))
            self.screen.blit(building_text, (x_offset, y_offset))
            y_offset += 25
            
            points_text = self.font.render(f"💎 {task['points']} points", True, (255, 200, 100))
            self.screen.blit(points_text, (x_offset, y_offset))
            y_offset += 35
        
        # Progress
        pygame.draw.line(self.screen, (60, 70, 100), (x_offset, y_offset), 
                        (x_offset + dashboard_width - 40, y_offset), 2)
        y_offset += 25
        
        completed_count = len(self.task_manager.completed_tasks)
        total_tasks = len(self.task_manager.tasks)
        progress_title = self.large_font.render(f"✓ {completed_count}/{total_tasks} TASKS", True, (150, 255, 150))
        self.screen.blit(progress_title, (x_offset, y_offset))
        y_offset += 35
        
        # Task progress bar
        task_progress = completed_count / total_tasks if total_tasks > 0 else 0
        self.draw_progress_bar(x_offset, y_offset, bar_width, bar_height, task_progress, (100, 255, 150))
        y_offset += 30
        
        # Controls
        pygame.draw.line(self.screen, (60, 70, 100), (x_offset, y_offset), 
                        (x_offset + dashboard_width - 40, y_offset), 2)
        y_offset += 25
        
        controls_title = self.large_font.render("⌨ CONTROLS", True, (200, 180, 255))
        self.screen.blit(controls_title, (x_offset, y_offset))
        y_offset += 30
        
        controls = [
            "↑↓←→ Move", "B - BFS", "A - A*",
            "C - Clear", "P - Pause", "R - Restart", "ESC - Exit"
        ]
        
        for control in controls:
            control_text = self.small_font.render(control, True, (180, 180, 200))
            self.screen.blit(control_text, (x_offset, y_offset))
            y_offset += 22
        
        # Game state overlays
        if self.state == GameState.PAUSED:
            self.draw_overlay("⏸ PAUSED", "Press P to continue", (255, 220, 100))
        elif self.state == GameState.VICTORY:
            self.draw_overlay("🏆 VICTORY!", f"Score: {self.score} | Press R", (100, 255, 150))
        elif self.state == GameState.GAME_OVER:
            self.draw_overlay("⏰ TIME'S UP!", "Press R to retry", (255, 100, 100))
    
    def draw_card(self, x, y, width, height, color):
        """Draw a card background"""
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color, card_rect, border_radius=5)
        pygame.draw.rect(self.screen, (color[0]+30, color[1]+30, color[2]+30), card_rect, 2, border_radius=5)
    
    def draw_progress_bar(self, x, y, width, height, progress, color):
        """Draw an animated progress bar"""
        bar_bg = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (30, 35, 45), bar_bg, border_radius=8)
        
        bar_fill = pygame.Rect(x, y, int(width * progress), height)
        pygame.draw.rect(self.screen, color, bar_fill, border_radius=8)
        pygame.draw.rect(self.screen, (60, 70, 90), bar_bg, 2, border_radius=8)
    
    def draw_overlay(self, title, subtitle, color):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((10, 15, 25))
        self.screen.blit(overlay, (0, 0))
        
        title_text = self.huge_font.render(title, True, color)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40))
        
        shadow = self.huge_font.render(title, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(self.screen_width // 2 + 3, self.screen_height // 2 - 37))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.large_font.render(subtitle, True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 30))
        self.screen.blit(subtitle_text, subtitle_rect)
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS for smooth animations
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = RVCECampusRunner()
    game.run()