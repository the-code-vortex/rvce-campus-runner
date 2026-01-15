import pygame
import sys
import heapq
from collections import deque, defaultdict
from enum import Enum
import math
import random
import os

# Import game screens
from game_screens import (
    MainMenuScreen, HowToPlayScreen, HighScoresScreen,
    DifficultySelectScreen, NameEntryScreen, HighScoreManager, COLORS
)

# Import game dynamics
from game_dynamics import (
    TileType, TILE_PROPERTIES, MapEvent, EventManager,
    ConstructionEvent, RainEvent, FireDrillEvent,
    NPC, NPCType, NPCState, NPCManager,
    Camera, FogOfWar, TileEffectHandler, MiniMap
)

# Import sound effects (optional - requires numpy)
try:
    from sound_effects import SoundManager
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    print("Note: Sound effects disabled (numpy not installed)")

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
                
    def is_walkable(self, x, y, tile_map=None, has_key=False):
        """Check if tile is walkable, optionally using tile_map for dynamic tiles"""
        if 0 <= x < self.width and 0 <= y < self.height:
            # Check base grid
            if self.grid[y][x] == 1:
                return False
            # Check dynamic tile map if provided
            if tile_map is not None:
                tile_type = tile_map[y][x]
                if tile_type in TILE_PROPERTIES:
                    props = TILE_PROPERTIES[tile_type]
                    if not props.get('walkable', True):
                        # Special case: locked gate with key
                        if tile_type == TileType.LOCKED_GATE and has_key:
                            return True
                        return False
            return True
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
        if v not in self.adj_list[u]:
            self.adj_list[u].append(v)
        if u not in self.adj_list[v]:
            self.adj_list[v].append(u)
        self.weights[(u, v)] = weight
        self.weights[(v, u)] = weight
        
    def clear(self):
        """Clear the graph for rebuilding"""
        self.adj_list = defaultdict(list)
        self.weights = {}
        
    def build_from_rvce_grid(self, game_map, tile_map=None):
        """Build graph from walkable paths in RVCE campus with tile-based weights"""
        self.clear()
        for y in range(game_map.height):
            for x in range(game_map.width):
                if game_map.is_walkable(x, y, tile_map):
                    current = (x, y)
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < game_map.width and 
                            0 <= ny < game_map.height and 
                            game_map.is_walkable(nx, ny, tile_map)):
                            # Get weight from tile type
                            weight = 1
                            if tile_map is not None:
                                tile_type = tile_map[ny][nx]
                                if tile_type in TILE_PROPERTIES:
                                    weight = TILE_PROPERTIES[tile_type].get('weight', 1)
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
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4
    HOW_TO_PLAY = 5
    HIGH_SCORES = 6
    DIFFICULTY_SELECT = 7
    NAME_ENTRY = 8

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
        
        # Difficulty settings (default: normal)
        self.difficulty = 'normal'
        self.difficulty_settings = {
            'easy': {'time': 420, 'tasks': 5, 'name': 'Easy'},
            'normal': {'time': 300, 'tasks': 7, 'name': 'Normal'},
            'hard': {'time': 180, 'tasks': 7, 'name': 'Hard'},
        }
        
        # High score manager
        scores_path = os.path.join(os.path.dirname(__file__), "high_scores.json")
        self.high_score_manager = HighScoreManager(scores_path)
        
        # Initialize menu screens
        self.main_menu = MainMenuScreen(self.screen_width, self.screen_height)
        self.how_to_play_screen = HowToPlayScreen(self.screen_width, self.screen_height)
        self.high_scores_screen = HighScoresScreen(self.screen_width, self.screen_height, 
                                                    self.high_score_manager)
        self.difficulty_screen = DifficultySelectScreen(self.screen_width, self.screen_height)
        self.name_entry_screen = None  # Created when needed
        
        # Start in menu state
        self.state = GameState.MENU
        
        # Dynamic game systems (initialized on game start)
        self.camera = None
        self.fog_of_war = None
        self.tile_effect_handler = None
        self.event_manager = None
        self.npc_manager = None
        self.mini_map = None
        self.tile_map = None  # 2D array of TileTypes
        
        # UI message display
        self.ui_message = None
        self.ui_message_timer = 0
        
        # Player visual effect states
        self.player_slowed = False
        self.player_boosted = False
        self.player_on_ice = False
        self.player_effect_timer = 0
        self.move_cooldown = 0  # Prevents movement when slowed
        
        # NPC interaction
        self.nearby_npc = None
        self.npc_dialogue_active = False
        
        # Sound manager
        self.sound_manager = None
        if SOUND_AVAILABLE:
            try:
                self.sound_manager = SoundManager()
            except Exception as e:
                print(f"Sound init failed: {e}")
        
        # Generate all assets
        self.load_assets()
        
        # Game is not initialized yet - will be done when starting
        self.game_initialized = False
        
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
        
        # Game state - use difficulty settings
        self.state = GameState.PLAYING
        self.player_pos = (2, 15)
        self.score = 0
        
        # Step tracking for efficiency scoring
        self.task_steps = 0  # Actual steps player has taken
        self.expected_path_length = 0  # BFS optimal path length
        self.task_start_pos = self.player_pos  # Where player was when task started
        
        self.time_remaining = self.difficulty_settings[self.difficulty]['time']
        self.max_time = self.time_remaining  # Store for time bonus calculation
        self.last_time = pygame.time.get_ticks()
        
        self.current_path = []
        self.path_algorithm = "BFS"
        self.algorithm_stats = {"BFS": 0, "A*": 0}
        
        # Clear particles
        self.particles = []
        
        # UI message
        self.ui_message = None
        self.ui_message_timer = 0
        
        # Mark game as initialized
        self.game_initialized = True
        
        # Setup map and buildings first
        self.setup_rvce_campus()
        
        # Initialize tile map (2D array of TileTypes)
        self.tile_map = [[TileType.NORMAL for _ in range(self.game_map.width)] 
                         for _ in range(self.game_map.height)]
        # Mark walls in tile map
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                if self.game_map.grid[y][x] == 1:
                    self.tile_map[y][x] = TileType.WALL
        
        # Initialize tile effect handler BEFORE setup_special_tiles (needed for portals)
        self.tile_effect_handler = TileEffectHandler()
                    
        # Setup special tiles
        self.setup_special_tiles()
        
        # Build navigation graph with tile weights
        self.nav_graph.build_from_rvce_grid(self.game_map, self.tile_map)
        
        # Initialize camera system
        self.camera = Camera(self.screen_width, self.screen_height)
        # Snap camera immediately to player position
        player_world_x = self.player_pos[0] * self.game_map.cell_size + self.game_map.cell_size / 2
        player_world_y = self.player_pos[1] * self.game_map.cell_size + self.game_map.cell_size / 2
        self.camera.snap_to((player_world_x, player_world_y))
        
        # Initialize fog of war
        self.fog_of_war = FogOfWar(self.game_map.width, self.game_map.height)
        self.fog_of_war.update(self.player_pos)
        
        # Initialize event manager
        self.event_manager = EventManager()
        self.event_manager.set_available_positions(self.game_map, self.tile_map)
        
        # Initialize NPC manager
        self.npc_manager = NPCManager()
        self.npc_manager.spawn_npcs(self.game_map, self.buildings)
        
        # Initialize mini-map (position in top-right dashboard area)
        self.mini_map = MiniMap(self.screen_width - 180, 50, 150)
        
        # Setup tasks
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
        # Note: Graph is built in reset_game after tile_map is set up
        
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
    
    def setup_special_tiles(self):
        """Setup special tile types for dynamic gameplay"""
        # Add ice tiles (near library area)
        ice_positions = [(9, 13), (10, 13), (12, 13)]
        for x, y in ice_positions:
            if self.game_map.is_walkable(x, y):
                self.tile_map[y][x] = TileType.ICE
                
        # Add grass tiles (garden areas)
        grass_positions = [(5, 5), (6, 5), (5, 7), (6, 7), (15, 7), (15, 9)]
        for x, y in grass_positions:
            if self.game_map.is_walkable(x, y):
                self.tile_map[y][x] = TileType.GRASS
        
        # Helper function to check if all buildings are reachable from player start
        def all_buildings_reachable():
            """BFS to verify all buildings are reachable from player start"""
            start = (2, 15)  # Main Gate / Player start
            visited = set()
            queue = deque([start])
            visited.add(start)
            
            while queue:
                x, y = queue.popleft()
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in visited:
                        if 0 <= nx < self.game_map.width and 0 <= ny < self.game_map.height:
                            tile = self.tile_map[ny][nx]
                            # Check if walkable (portals ARE walkable)
                            if tile != TileType.WALL and tile != TileType.CONSTRUCTION:
                                visited.add((nx, ny))
                                queue.append((nx, ny))
            
            # Check all building positions are reachable
            for name, pos in self.buildings.items():
                if pos not in visited:
                    return False, name
            return True, None
        
        # Try portal placement - only if all buildings remain reachable
        # Portals should be on intersection tiles, not bottleneck paths
        potential_portal_pairs = [
            ((7, 13), (13, 9)),    # Library area to CSE area
            ((5, 9), (15, 11)),    # Mid-left to mid-right
            ((3, 11), (17, 5)),    # Left side to right side
        ]
        
        portal_placed = False
        for portal_a, portal_b in potential_portal_pairs:
            # Check both positions are walkable NORMAL tiles (not buildings)
            if (self.game_map.is_walkable(*portal_a) and 
                self.game_map.is_walkable(*portal_b) and
                portal_a not in self.buildings.values() and
                portal_b not in self.buildings.values()):
                
                # Temporarily place portals
                old_a = self.tile_map[portal_a[1]][portal_a[0]]
                old_b = self.tile_map[portal_b[1]][portal_b[0]]
                self.tile_map[portal_a[1]][portal_a[0]] = TileType.PORTAL_A
                self.tile_map[portal_b[1]][portal_b[0]] = TileType.PORTAL_B
                
                # Verify all buildings still reachable
                reachable, blocked = all_buildings_reachable()
                
                if reachable:
                    # Keep portals
                    self.tile_effect_handler.set_portals(portal_a, portal_b)
                    portal_placed = True
                    break
                else:
                    # Revert portals - they block access to a building
                    self.tile_map[portal_a[1]][portal_a[0]] = old_a
                    self.tile_map[portal_b[1]][portal_b[0]] = old_b
                    print(f"Skipped portal pair {portal_a}-{portal_b}: would block {blocked}")
        
        if not portal_placed:
            print("No valid portal positions found - skipping portals")
            
        # Add trap tiles (verify they don't block paths)
        trap_positions = [(9, 9), (5, 11)]
        for x, y in trap_positions:
            if self.game_map.is_walkable(x, y) and (x, y) not in self.buildings.values():
                self.tile_map[y][x] = TileType.TRAP
                
        # Add booster tiles
        booster_positions = [(7, 7), (13, 13)]
        for x, y in booster_positions:
            if self.game_map.is_walkable(x, y) and (x, y) not in self.buildings.values():
                self.tile_map[y][x] = TileType.BOOSTER
                
        # Add water tiles
        water_positions = [(9, 5), (10, 5), (11, 5)]
        for x, y in water_positions:
            if self.game_map.is_walkable(x, y) and (x, y) not in self.buildings.values():
                self.tile_map[y][x] = TileType.WATER
                
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
        
        # Limit tasks based on difficulty
        max_tasks = self.difficulty_settings[self.difficulty]['tasks']
        task_list = list(tasks.items())[:max_tasks]
        
        for task_id, task_data in task_list:
            self.task_manager.add_task(task_id, task_data)
        
        first_task = self.task_manager.get_next_task()
        if first_task:
            self.task_manager.assign_task(first_task)
            # Calculate expected path for first task
            current = self.task_manager.current_task
            if current:
                target = self.buildings.get(current['building'])
                if target:
                    expected_path = self.find_path_bfs(self.player_pos, target)
                    self.expected_path_length = len(expected_path) if expected_path else 0
                    self.task_start_pos = self.player_pos
                    print(f"First task: {current['name']} (optimal: {self.expected_path_length} steps)")
    
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
                
                # Calculate efficiency bonus/penalty
                base_points = current_task['points']
                efficiency_bonus = 0
                efficiency_message = ""
                
                if self.expected_path_length > 0 and self.task_steps > 0:
                    # Calculate efficiency ratio
                    efficiency = self.expected_path_length / self.task_steps
                    
                    if efficiency > 1.2:  # Beat expected path by 20%+
                        # Excellent - teleportation used effectively!
                        efficiency_bonus = int(base_points * 0.5 * (efficiency - 1))
                        efficiency_message = f" +{efficiency_bonus} EFFICIENCY BONUS (portals!)"
                        if self.sound_manager:
                            self.sound_manager.play('victory')
                    elif efficiency > 1.0:  # Beat expected path slightly
                        efficiency_bonus = int(base_points * 0.25)
                        efficiency_message = f" +{efficiency_bonus} efficiency bonus"
                    elif efficiency > 0.8:  # Close to optimal
                        efficiency_message = " (efficient path)"
                    elif efficiency > 0.5:  # Took extra steps
                        efficiency_bonus = -int(base_points * 0.1)
                        efficiency_message = f" {efficiency_bonus} (longer route)"
                    else:  # Very inefficient
                        efficiency_bonus = -int(base_points * 0.2)
                        efficiency_message = f" {efficiency_bonus} (took many detours)"
                
                total_points = base_points + efficiency_bonus
                self.score += total_points
                
                print(f"✓ Task Completed: {current_task['name']} (+{base_points} base{efficiency_message})")
                print(f"   Path: {self.task_steps} steps vs {self.expected_path_length} expected (BFS optimal)")
                
                if self.sound_manager and efficiency_bonus <= 0:
                    self.sound_manager.play('task_complete')
                
                self.task_manager.complete_task(current_task['id'])
                self.current_path = []
                
                # Reset step counter for next task
                self.task_steps = 0
                
                next_task = self.task_manager.get_next_task()
                if next_task:
                    self.task_manager.assign_task(next_task)
                    # Calculate expected path for new task
                    current = self.task_manager.current_task
                    if current:
                        new_target = self.buildings.get(current['building'])
                        if new_target:
                            expected_path = self.find_path_bfs(self.player_pos, new_target)
                            self.expected_path_length = len(expected_path) if expected_path else 0
                            self.task_start_pos = self.player_pos
                        print(f"New task assigned: {current['name']} (optimal: {self.expected_path_length} steps)")
                else:
                    # Victory! Add time bonus
                    time_bonus = self.time_remaining * 2
                    self.score += time_bonus
                    print(f"All tasks completed! Victory! (+{time_bonus} time bonus)")
                    
                    # Check for high score
                    if self.high_score_manager.is_high_score(self.score):
                        rank = self.high_score_manager.get_rank(self.score)
                        self.name_entry_screen = NameEntryScreen(
                            self.screen_width, self.screen_height, self.score, rank
                        )
                        self.state = GameState.NAME_ENTRY
                    else:
                        self.state = GameState.VICTORY
    
    def handle_input(self):
        dt = self.clock.get_time() / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle different game states
            if self.state == GameState.MENU:
                result = self.main_menu.handle_event(event)
                if result == 'start':
                    self.reset_game()
                elif result == 'difficulty':
                    self.state = GameState.DIFFICULTY_SELECT
                elif result == 'how_to_play':
                    self.state = GameState.HOW_TO_PLAY
                elif result == 'high_scores':
                    self.state = GameState.HIGH_SCORES
                elif result == 'exit':
                    return False
                    
            elif self.state == GameState.HOW_TO_PLAY:
                result = self.how_to_play_screen.handle_event(event)
                if result == 'back':
                    self.state = GameState.MENU
                    
            elif self.state == GameState.HIGH_SCORES:
                result = self.high_scores_screen.handle_event(event)
                if result == 'back':
                    self.state = GameState.MENU
                    
            elif self.state == GameState.DIFFICULTY_SELECT:
                result = self.difficulty_screen.handle_event(event)
                if result:
                    action, value = result
                    if action == 'select':
                        self.difficulty = value
                        self.reset_game()
                    elif action == 'back':
                        self.state = GameState.MENU
                        
            elif self.state == GameState.NAME_ENTRY:
                if self.name_entry_screen:
                    result = self.name_entry_screen.handle_event(event)
                    if result:
                        action, value = result
                        if action == 'submit':
                            self.high_score_manager.add_score(
                                value, self.score, 
                                self.difficulty_settings[self.difficulty]['name']
                            )
                            self.state = GameState.MENU
                        elif action == 'skip':
                            self.state = GameState.MENU
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in [GameState.PLAYING, GameState.PAUSED, 
                                     GameState.VICTORY, GameState.GAME_OVER]:
                        self.state = GameState.MENU
                        self.game_initialized = False
                    else:
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
                        
                        direction = (new_x - x, new_y - y)
                        has_key = self.tile_effect_handler.can_unlock_gate() if self.tile_effect_handler else False
                        
                        # Check for movement slowdown (grass, water, rain)
                        if self.move_cooldown > 0:
                            continue  # Still in cooldown, skip movement
                        
                        if self.game_map.is_walkable(new_x, new_y, self.tile_map, has_key):
                            self.player_pos = (new_x, new_y)
                            self.player_frame += 1
                            
                            # Increment step counter for efficiency tracking
                            self.task_steps += 1
                            
                            # Play step sound
                            if self.sound_manager:
                                self.sound_manager.play('step')
                            
                            # Process tile effect
                            if self.tile_map and self.tile_effect_handler:
                                tile_type = self.tile_map[new_y][new_x]
                                new_pos, time_penalty, message = self.tile_effect_handler.process_tile(
                                    self.player_pos, tile_type, direction, self.game_map
                                )
                                
                                # Set player visual states and apply effects
                                self.player_slowed = False
                                self.player_boosted = False
                                self.player_on_ice = False
                                
                                if tile_type == TileType.GRASS:
                                    self.player_slowed = True
                                    self.move_cooldown = 0.15  # Slow down movement
                                elif tile_type == TileType.WATER:
                                    self.player_slowed = True
                                    self.move_cooldown = 0.3  # Much slower
                                elif tile_type == TileType.ICE:
                                    self.player_on_ice = True
                                    if self.sound_manager:
                                        self.sound_manager.play('ice_slide')
                                elif tile_type == TileType.BOOSTER:
                                    self.player_boosted = True
                                    if self.sound_manager:
                                        self.sound_manager.play('booster')
                                
                                # Check for rain slowdown
                                if self.event_manager and self.event_manager.get_rain_intensity() > 1:
                                    self.player_slowed = True
                                    self.move_cooldown = max(self.move_cooldown, 0.1)
                                
                                # Apply teleport
                                if new_pos != self.player_pos:
                                    self.player_pos = new_pos
                                    if self.sound_manager:
                                        self.sound_manager.play('teleport')
                                    
                                # Apply time penalty
                                if time_penalty > 0:
                                    self.time_remaining -= time_penalty
                                    if self.sound_manager:
                                        self.sound_manager.play('trap')
                                    
                                # Show message
                                if message:
                                    self.ui_message = message
                                    self.ui_message_timer = 2.0
                            
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
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
                        self.game_initialized = False
                    # E key to interact with NPCs
                    elif event.key == pygame.K_e:
                        if self.nearby_npc and not self.nearby_npc.has_interacted:
                            self.ui_message = self.nearby_npc.dialogue
                            self.ui_message_timer = 3.0
                            self.nearby_npc.has_interacted = True
                            if self.sound_manager:
                                self.sound_manager.play('npc_talk')
                            # Give bonus for talking to professor
                            if self.nearby_npc.npc_type == NPCType.PROFESSOR:
                                self.score += 10
                                self.ui_message += " (+10 pts!)"
                    # Zoom controls
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        if self.camera:
                            self.camera.zoom_in()
                    elif event.key == pygame.K_MINUS:
                        if self.camera:
                            self.camera.zoom_out()
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_p:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        return True
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
                        self.game_initialized = False
                        
                elif self.state == GameState.VICTORY or self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        return True
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
                        self.game_initialized = False
        
        return True
    
    def undo_move(self):
        previous_state = self.undo_stack.pop()
        if previous_state:
            self.player_pos = previous_state['position']
            self.score = previous_state['score']
    
    def update(self):
        dt = self.clock.get_time() / 1000.0
        
        # Update menu screens if in menu state
        if self.state == GameState.MENU:
            self.main_menu.update(dt)
            return
        elif self.state == GameState.HOW_TO_PLAY:
            self.how_to_play_screen.update(dt)
            return
        elif self.state == GameState.HIGH_SCORES:
            self.high_scores_screen.update(dt)
            return
        elif self.state == GameState.DIFFICULTY_SELECT:
            self.difficulty_screen.update(dt)
            return
        elif self.state == GameState.NAME_ENTRY:
            if self.name_entry_screen:
                self.name_entry_screen.update(dt)
            return
        
        if self.state != GameState.PLAYING:
            return
            
        # Update timer
        current_time = pygame.time.get_ticks()
        if current_time - self.last_time > 1000:
            self.time_remaining -= 1
            self.last_time = current_time
            
            if self.time_remaining <= 0:
                # Check for high score before game over
                if self.high_score_manager.is_high_score(self.score):
                    rank = self.high_score_manager.get_rank(self.score)
                    self.name_entry_screen = NameEntryScreen(
                        self.screen_width, self.screen_height, self.score, rank
                    )
                    self.state = GameState.NAME_ENTRY
                else:
                    self.state = GameState.GAME_OVER
        
        # Update animations
        self.animation_time = current_time / 1000.0
        self.pulse_offset = math.sin(self.animation_time * 3) * 3
        self.path_animation = (self.path_animation + 1) % 60
        
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Update UI message timer
        if self.ui_message_timer > 0:
            self.ui_message_timer -= dt
            if self.ui_message_timer <= 0:
                self.ui_message = None
        
        # Update camera
        if self.camera:
            player_world_x = self.player_pos[0] * self.game_map.cell_size + self.game_map.cell_size / 2
            player_world_y = self.player_pos[1] * self.game_map.cell_size + self.game_map.cell_size / 2
            self.camera.update(dt, (player_world_x, player_world_y))
            self.camera.clamp_to_map(self.game_map.width, self.game_map.height, self.game_map.cell_size)
        
        # Update fog of war
        if self.fog_of_war:
            self.fog_of_war.update(self.player_pos)
        
        # Update tile effects
        if self.tile_effect_handler:
            self.tile_effect_handler.update(dt)
            
            # Process ice sliding
            if self.tile_effect_handler.slide_remaining > 0:
                new_pos = self.tile_effect_handler.process_slide(self.player_pos, self.game_map, self.tile_map)
                if new_pos != self.player_pos:
                    self.player_pos = new_pos
                    self.check_task_completion()
        
        # Update map events
        if self.event_manager:
            def rebuild_graph():
                self.nav_graph.build_from_rvce_grid(self.game_map, self.tile_map)
            self.event_manager.update(dt, self.game_map, self.tile_map, rebuild_graph)
        
        # Update move cooldown (for slowdown effects)
        if self.move_cooldown > 0:
            self.move_cooldown -= dt
            
        # Update player effect timer
        self.player_effect_timer += dt
        
        # Update NPCs
        if self.npc_manager:
            self.npc_manager.update(dt, self.player_pos, self.game_map, self.find_path_astar)
            
            # Check for nearby NPC (for E key interaction)
            self.nearby_npc = self.npc_manager.check_interaction(self.player_pos)
            if self.nearby_npc and not self.nearby_npc.has_interacted:
                # Show prompt to press E
                if self.ui_message != "Press E to talk":
                    self.ui_message = "Press E to talk"
                    self.ui_message_timer = 0.5
            elif self.ui_message == "Press E to talk":
                self.ui_message = None
    
    def draw_gradient_background(self):
        for y in range(self.screen_height):
            progress = y / self.screen_height
            r = int(10 + progress * 15)
            g = int(15 + progress * 20)
            b = int(30 + progress * 25)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
    
    def draw(self):
        # Handle menu screen drawing
        if self.state == GameState.MENU:
            self.main_menu.draw(self.screen)
            pygame.display.flip()
            return
        elif self.state == GameState.HOW_TO_PLAY:
            self.how_to_play_screen.draw(self.screen)
            pygame.display.flip()
            return
        elif self.state == GameState.HIGH_SCORES:
            self.high_scores_screen.draw(self.screen)
            pygame.display.flip()
            return
        elif self.state == GameState.DIFFICULTY_SELECT:
            self.difficulty_screen.draw(self.screen)
            pygame.display.flip()
            return
        elif self.state == GameState.NAME_ENTRY:
            if self.name_entry_screen:
                self.name_entry_screen.draw(self.screen)
            pygame.display.flip()
            return
        
        # Check if game is initialized before drawing game content
        if not self.game_initialized:
            self.draw_gradient_background()
            pygame.display.flip()
            return
        
        # Background
        self.draw_gradient_background()
        
        # Use camera-based rendering if available
        if self.camera:
            # Camera-based map rendering
            cell_size = int(self.game_map.cell_size * self.camera.zoom)
            
            for y in range(self.game_map.height):
                for x in range(self.game_map.width):
                    # Check visibility with camera
                    world_x = x * self.game_map.cell_size
                    world_y = y * self.game_map.cell_size
                    
                    if not self.camera.is_visible(world_x / self.game_map.cell_size, 
                                                   world_y / self.game_map.cell_size, margin=2):
                        continue
                    
                    screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
                    rect = pygame.Rect(screen_x, screen_y, cell_size, cell_size)
                    
                    # Check fog of war
                    fog_alpha = 0
                    if self.fog_of_war:
                        fog_alpha = self.fog_of_war.get_alpha(x, y)
                        if fog_alpha == 255:
                            # Completely hidden
                            pygame.draw.rect(self.screen, (15, 20, 30), rect)
                            continue
                    
                    # Get tile type
                    tile_type = self.tile_map[y][x] if self.tile_map else TileType.NORMAL
                    
                    # Draw tile based on type
                    if tile_type == TileType.WALL:
                        texture = pygame.transform.scale(self.brick_texture, (cell_size, cell_size))
                        self.screen.blit(texture, rect.topleft)
                    elif tile_type in TILE_PROPERTIES:
                        props = TILE_PROPERTIES[tile_type]
                        pygame.draw.rect(self.screen, props['color'], rect)
                        # Add tile indicators
                        if tile_type == TileType.ICE:
                            pygame.draw.line(self.screen, (200, 240, 255), 
                                           (rect.x + 5, rect.y + 10), (rect.x + cell_size - 5, rect.y + 10), 2)
                        elif tile_type == TileType.PORTAL_A or tile_type == TileType.PORTAL_B:
                            pygame.draw.circle(self.screen, (255, 255, 255), rect.center, cell_size // 4, 2)
                        elif tile_type == TileType.TRAP:
                            pygame.draw.line(self.screen, (255, 255, 100), 
                                           (rect.x + 5, rect.y + 5), (rect.x + cell_size - 5, rect.y + cell_size - 5), 2)
                            pygame.draw.line(self.screen, (255, 255, 100), 
                                           (rect.x + cell_size - 5, rect.y + 5), (rect.x + 5, rect.y + cell_size - 5), 2)
                        elif tile_type == TileType.BOOSTER:
                            pygame.draw.polygon(self.screen, (255, 255, 200), [
                                (rect.centerx, rect.y + 5),
                                (rect.x + 5, rect.y + cell_size - 5),
                                (rect.x + cell_size - 5, rect.y + cell_size - 5)
                            ])
                    else:
                        texture = pygame.transform.scale(self.path_texture, (cell_size, cell_size))
                        self.screen.blit(texture, rect.topleft)
                    
                    pygame.draw.rect(self.screen, (20, 25, 35), rect, 1)
                    
                    # Apply fog overlay for explored but not visible tiles
                    if fog_alpha > 0:
                        fog_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                        fog_surface.fill((0, 0, 0, fog_alpha))
                        self.screen.blit(fog_surface, rect.topleft)
            
            # Draw animated path
            if len(self.current_path) > 0:
                path_color = (50, 255, 100) if self.path_algorithm == "BFS" else (100, 150, 255)
                
                for i, pos in enumerate(self.current_path):
                    px, py = pos
                    world_x = px * self.game_map.cell_size
                    world_y = py * self.game_map.cell_size
                    screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
                    rect = pygame.Rect(screen_x, screen_y, cell_size, cell_size)
                    
                    anim_offset = (self.path_animation - i * 3) % 60
                    alpha = int(100 + 50 * math.sin(anim_offset / 10))
                    
                    path_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                    path_surface.fill((*path_color, alpha))
                    self.screen.blit(path_surface, rect.topleft)
                    pygame.draw.rect(self.screen, path_color, rect, 2)
            
            # Draw buildings
            for name, pos in self.buildings.items():
                bx, by = pos
                
                # Check fog visibility
                if self.fog_of_war and not self.fog_of_war.is_explored(bx, by):
                    continue
                
                world_x = bx * self.game_map.cell_size
                world_y = by * self.game_map.cell_size
                screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
                rect = pygame.Rect(screen_x, screen_y, cell_size, cell_size)
                
                is_target = (self.task_manager.current_task and 
                            self.task_manager.current_task['building'] == name)
                
                if is_target:
                    pulse_size = int(self.pulse_offset * self.camera.zoom)
                    glow_rect = rect.inflate(12 + pulse_size, 12 + pulse_size)
                    glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                    glow_surface.fill((255, 200, 0, 120))
                    self.screen.blit(glow_surface, (glow_rect.x, glow_rect.y))
                    pygame.draw.rect(self.screen, (255, 220, 50), rect, border_radius=4)
                else:
                    pygame.draw.rect(self.screen, (80, 70, 120), rect, border_radius=4)
                
                if name in self.building_icons:
                    icon = self.building_icons[name]
                    icon_size = cell_size - 8
                    icon_scaled = pygame.transform.scale(icon, (icon_size, icon_size))
                    self.screen.blit(icon_scaled, (rect.x + 4, rect.y + 4))
            
            # Draw NPCs
            if self.npc_manager:
                npc_font = pygame.font.SysFont('Segoe UI', max(10, cell_size // 4), bold=True)
                for npc in self.npc_manager.npcs:
                    # Check fog visibility
                    if self.fog_of_war and not self.fog_of_war.is_visible(*npc.pos):
                        continue
                        
                    world_x = npc.pos[0] * self.game_map.cell_size
                    world_y = npc.pos[1] * self.game_map.cell_size
                    screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
                    
                    npc_rect = pygame.Rect(screen_x, screen_y, cell_size, cell_size)
                    
                    # Draw NPC body (colored rectangle with rounded corners)
                    npc_color = npc.get_color()
                    body_rect = npc_rect.inflate(-cell_size // 4, -cell_size // 4)
                    pygame.draw.rect(self.screen, npc_color, body_rect, border_radius=cell_size // 6)
                    pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 2, border_radius=cell_size // 6)
                    
                    # Draw head (small circle on top)
                    head_radius = max(4, cell_size // 6)
                    head_pos = (npc_rect.centerx, body_rect.top - head_radius + 2)
                    pygame.draw.circle(self.screen, (255, 220, 180), head_pos, head_radius)
                    pygame.draw.circle(self.screen, npc_color, head_pos, head_radius, 2)
                    
                    # Draw label below NPC
                    label = npc.get_label()
                    label_surface = npc_font.render(label, True, (255, 255, 255))
                    label_rect = label_surface.get_rect(midtop=(npc_rect.centerx, npc_rect.bottom - 2))
                    
                    # Label background
                    bg_rect = label_rect.inflate(6, 2)
                    pygame.draw.rect(self.screen, (30, 30, 40, 200), bg_rect, border_radius=3)
                    self.screen.blit(label_surface, label_rect)
                    
                    # Draw state indicator (exclamation for chase)
                    if npc.state == NPCState.CHASE:
                        alert_surface = npc_font.render("!", True, (255, 50, 50))
                        self.screen.blit(alert_surface, (npc_rect.centerx - 3, npc_rect.top - 15))
            
            # Draw player
            px, py = self.player_pos
            world_x = px * self.game_map.cell_size
            world_y = py * self.game_map.cell_size
            screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
            player_rect = pygame.Rect(screen_x, screen_y, cell_size, cell_size)
            
            # Draw player effect background (before sprite)
            if self.player_slowed:
                # Blue/green slow overlay
                slow_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                pulse = int(abs(math.sin(self.player_effect_timer * 4)) * 60)
                slow_surface.fill((50, 100, 200, 80 + pulse))
                self.screen.blit(slow_surface, player_rect.topleft)
                
            elif self.player_boosted:
                # Yellow/orange speed glow
                glow_size = int(8 + abs(math.sin(self.player_effect_timer * 8)) * 4)
                glow_rect = player_rect.inflate(glow_size, glow_size)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                glow_surface.fill((255, 200, 50, 100))
                self.screen.blit(glow_surface, glow_rect.topleft)
                
            elif self.player_on_ice:
                # Ice crystal trail effect
                for i in range(3):
                    offset_x = random.randint(-5, 5)
                    offset_y = random.randint(0, 8)
                    pygame.draw.circle(self.screen, (200, 230, 255, 150), 
                                     (player_rect.centerx + offset_x, player_rect.bottom + offset_y), 3)
            
            # Draw player sprite
            sprite_index = (self.player_frame // 5) % len(self.player_sprites)
            player_sprite = pygame.transform.scale(self.player_sprites[sprite_index], (cell_size, cell_size))
            self.screen.blit(player_sprite, player_rect.topleft)
            
            # Draw rain effect overlay on player during rain
            if self.event_manager and self.event_manager.get_rain_intensity() > 1:
                # Rain drops around player
                for _ in range(5):
                    rx = player_rect.x + random.randint(0, cell_size)
                    ry = player_rect.y + random.randint(0, cell_size)
                    pygame.draw.line(self.screen, (150, 180, 255), 
                                   (rx, ry), (rx - 2, ry + 6), 1)
            
            # Draw particles
            for particle in self.particles:
                particle.draw(self.screen)
            
            # Draw mini-map
            if self.mini_map:
                target_pos = None
                if self.task_manager.current_task:
                    target_pos = self.buildings.get(self.task_manager.current_task['building'])
                npcs = self.npc_manager.npcs if self.npc_manager else []
                self.mini_map.draw(self.screen, self.game_map, self.player_pos, 
                                  target_pos, npcs, self.fog_of_war)
            
            # Draw UI message
            if self.ui_message:
                msg_font = pygame.font.SysFont('Segoe UI', 24, bold=True)
                msg_surface = msg_font.render(self.ui_message, True, (255, 255, 100))
                msg_rect = msg_surface.get_rect(center=(self.screen_width // 3, 50))
                
                # Background
                bg_rect = msg_rect.inflate(20, 10)
                pygame.draw.rect(self.screen, (30, 35, 50), bg_rect, border_radius=8)
                pygame.draw.rect(self.screen, (100, 150, 255), bg_rect, 2, border_radius=8)
                self.screen.blit(msg_surface, msg_rect)
            
            # Draw event warnings
            if self.event_manager:
                if self.event_manager.is_fire_drill_active():
                    warning_font = pygame.font.SysFont('Segoe UI', 20, bold=True)
                    warning = warning_font.render("🚨 FIRE DRILL IN PROGRESS!", True, (255, 100, 100))
                    self.screen.blit(warning, (self.screen_width // 3 - 100, 80))
                    
                rain_intensity = self.event_manager.get_rain_intensity()
                if rain_intensity > 1:
                    rain_font = pygame.font.SysFont('Segoe UI', 18)
                    rain = rain_font.render("🌧 Rain - Movement Slowed", True, (150, 180, 255))
                    self.screen.blit(rain, (self.screen_width // 3 - 80, 80))
        
        else:
            # Fallback to original drawing (no camera)
            map_width = self.game_map.width * self.game_map.cell_size
            map_height = self.game_map.height * self.game_map.cell_size
            map_offset_x = 50
            map_offset_y = (self.screen_height - map_height) // 2
            
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
                        texture = pygame.transform.scale(self.brick_texture, (self.game_map.cell_size, self.game_map.cell_size))
                        self.screen.blit(texture, rect.topleft)
                    else:
                        texture = pygame.transform.scale(self.path_texture, (self.game_map.cell_size, self.game_map.cell_size))
                        self.screen.blit(texture, rect.topleft)
                    
                    pygame.draw.rect(self.screen, (20, 25, 35), rect, 1)
            
            # Draw player (fallback)
            x, y = self.player_pos
            player_rect = pygame.Rect(
                x * self.game_map.cell_size + map_offset_x,
                y * self.game_map.cell_size + map_offset_y,
                self.game_map.cell_size,
                self.game_map.cell_size
            )
            sprite_index = (self.player_frame // 5) % len(self.player_sprites)
            player_sprite = pygame.transform.scale(self.player_sprites[sprite_index], 
                                                   (self.game_map.cell_size, self.game_map.cell_size))
            self.screen.blit(player_sprite, player_rect.topleft)
        
        # Draw dashboard
        map_width = self.game_map.width * self.game_map.cell_size
        map_offset_x = 50
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
            "↑↓←→ Move", "E - Talk", "B - BFS", "A - A*",
            "C - Clear", "P - Pause", "R - Restart", 
            "+/- Zoom", "M - Menu"
        ]
        
        for control in controls:
            control_text = self.small_font.render(control, True, (180, 180, 200))
            self.screen.blit(control_text, (x_offset, y_offset))
            y_offset += 22
        
        # Game state overlays
        if self.state == GameState.PAUSED:
            self.draw_overlay("⏸ PAUSED", "Press P to continue | M - Menu", (255, 220, 100))
        elif self.state == GameState.VICTORY:
            self.draw_overlay("🏆 VICTORY!", f"Score: {self.score} | R - Restart | M - Menu", (100, 255, 150))
        elif self.state == GameState.GAME_OVER:
            self.draw_overlay("⏰ TIME'S UP!", f"Score: {self.score} | R - Retry | M - Menu", (255, 100, 100))
    
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