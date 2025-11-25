import pygame
import sys
import heapq
from collections import deque, defaultdict
from enum import Enum
import math
import random

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
                    # Connect to adjacent walkable cells
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

class RVCECampusRunner:
    def __init__(self):
        pygame.init()
        self.screen_width = 1000
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("RVCE Campus Runner - A* vs BFS Pathfinding")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 14)
        self.large_font = pygame.font.SysFont('Arial', 18)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Initialize data structures
        self.game_map = RVCEGameMap(20, 18)
        self.nav_graph = RVCEGraph()
        self.undo_stack = UndoStack()
        self.task_manager = TaskManager()
        self.bfs_queue = BFSQueue()
        self.priority_queue = PriorityQueue()
        
        # Game state
        self.state = GameState.PLAYING
        self.player_pos = (2, 15)  # Start near Main Gate
        self.score = 0
        self.time_remaining = 300  # 5 minutes
        self.last_time = pygame.time.get_ticks()
        
        self.current_path = []
        self.path_algorithm = "BFS"
        self.algorithm_stats = {"BFS": 0, "A*": 0}
        
        self.setup_rvce_campus()
        self.setup_academic_tasks()
        
    def setup_rvce_campus(self):
        # RVCE Campus Layout (0=path, 1=buildings, 2=items, 3=special)
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
        
        # RVCE Building Locations
        self.buildings = {
            "Main Gate": (2, 15),
            "Admin Block": (4, 3),
            "DTL Innovation Hub": (7, 2),
            "Mechanical Dept": (12, 2),
            "BT Quadrangle": (8, 5),
            "AI-ML & MCA Dept": (15, 4),
            "BT & EIE Dept": (17, 6),
            "IEM Dept": (5, 7),
            "EEE Dept": (10, 8),
            "CSE Dept": (15, 9),
            "ECE Dept": (8, 11),
            "Library": (12, 12),
            "Food Court (MINGOS)": (5, 13),
            "Boys Hostel": (17, 14),
            "Incubation Center": (14, 16)
        }
        
    def setup_academic_tasks(self):
        # Academic Tasks with Riddles
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
        
        # Assign first task
        first_task = self.task_manager.get_next_task()
        if first_task:
            self.task_manager.assign_task(first_task)
    
    def heuristic(self, a, b):
        """Manhattan distance heuristic for A* algorithm"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def find_path_bfs(self, start, goal):
        """BFS Algorithm - Finds shortest path (unweighted)"""
        visited = set()
        parent = {}
        nodes_explored = 0
        
        self.bfs_queue.enqueue(start)
        visited.add(start)
        
        while not self.bfs_queue.is_empty():
            current = self.bfs_queue.dequeue()
            nodes_explored += 1
            
            if current == goal:
                # Reconstruct path
                path = []
                while current in parent:
                    path.append(current)
                    current = parent[current]
                self.algorithm_stats["BFS"] = nodes_explored
                return path[::-1]
            
            for neighbor in self.nav_graph.adj_list[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    self.bfs_queue.enqueue(neighbor)
        
        self.algorithm_stats["BFS"] = nodes_explored
        return []
    
    def find_path_astar(self, start, goal):
        """A* Algorithm - Finds shortest path with heuristic"""
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
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                self.algorithm_stats["A*"] = nodes_explored
                return path[::-1]
            
            for neighbor in self.nav_graph.adj_list[current]:
                tentative_g_score = g_score[current] + 1  # All edges weight 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)
                    open_set.push(neighbor, f_score[neighbor])
        
        self.algorithm_stats["A*"] = nodes_explored
        return []
    
    def check_task_completion(self):
        if not self.task_manager.current_task:
            return
            
        current_task = self.task_manager.current_task
        target_building = current_task['building']
        
        if target_building in self.buildings:
            target_pos = self.buildings[target_building]
            if self.player_pos == target_pos:
                # Task completed!
                self.score += current_task['points']
                self.task_manager.complete_task(current_task['id'])
                
                # Assign next task
                next_task = self.task_manager.get_next_task()
                if next_task:
                    self.task_manager.assign_task(next_task)
                else:
                    # All tasks completed!
                    self.state = GameState.VICTORY
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.PLAYING:
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
                    elif event.key == pygame.K_u:
                        self.undo_move()
                    elif event.key == pygame.K_b:  # BFS
                        if self.task_manager.current_task:
                            target = self.buildings[self.task_manager.current_task['building']]
                            self.current_path = self.find_path_bfs(self.player_pos, target)
                            self.path_algorithm = "BFS"
                            print(f"BFS Path Found! Nodes explored: {self.algorithm_stats['BFS']}")
                    elif event.key == pygame.K_a:  # A*
                        if self.task_manager.current_task:
                            target = self.buildings[self.task_manager.current_task['building']]
                            self.current_path = self.find_path_astar(self.player_pos, target)
                            self.path_algorithm = "A*"
                            print(f"A* Path Found! Nodes explored: {self.algorithm_stats['A*']}")
                    elif event.key == pygame.K_c:
                        self.current_path = []
                    elif event.key == pygame.K_p:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_n:  # Next task
                        next_task = self.task_manager.get_next_task()
                        if next_task:
                            self.task_manager.assign_task(next_task)
                    
                    if self.game_map.is_walkable(new_x, new_y):
                        self.player_pos = (new_x, new_y)
                        self.check_task_completion()
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_p:
                        self.state = GameState.PLAYING
                elif self.state == GameState.VICTORY:
                    if event.key == pygame.K_r:
                        self.__init__()  # Restart game
        
        return True
    
    def undo_move(self):
        previous_state = self.undo_stack.pop()
        if previous_state:
            self.player_pos = previous_state['position']
            self.score = previous_state['score']
    
    def update(self):
        if self.state != GameState.PLAYING:
            return
            
        # Update timer
        current_time = pygame.time.get_ticks()
        if current_time - self.last_time > 1000:  # 1 second
            self.time_remaining -= 1
            self.last_time = current_time
            
            if self.time_remaining <= 0:
                self.state = GameState.GAME_OVER
    
    def draw(self):
        self.screen.fill((25, 25, 50))
        
        # Draw campus map
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                rect = pygame.Rect(
                    x * self.game_map.cell_size + 10,
                    y * self.game_map.cell_size + 10,
                    self.game_map.cell_size - 2,
                    self.game_map.cell_size - 2
                )
                
                cell_value = self.game_map.get_cell_value(x, y)
                if cell_value == 1:
                    pygame.draw.rect(self.screen, (80, 80, 140), rect)
                else:
                    pygame.draw.rect(self.screen, (50, 50, 90), rect)
                
                pygame.draw.rect(self.screen, (30, 30, 60), rect, 1)
        
        # Draw buildings
        for name, pos in self.buildings.items():
            x, y = pos
            rect = pygame.Rect(
                x * self.game_map.cell_size + 10,
                y * self.game_map.cell_size + 10,
                self.game_map.cell_size - 2,
                self.game_map.cell_size - 2
            )
            pygame.draw.rect(self.screen, (120, 80, 160), rect)
            
            # Draw building label
            if self.game_map.cell_size > 30:
                label = self.font.render(name[:3], True, (255, 255, 255))
                self.screen.blit(label, (rect.x + 2, rect.y + 2))
        
        # Draw path with different colors for different algorithms
        path_color = (0, 200, 0) if self.path_algorithm == "BFS" else (0, 100, 255)
        for pos in self.current_path:
            x, y = pos
            rect = pygame.Rect(
                x * self.game_map.cell_size + 10,
                y * self.game_map.cell_size + 10,
                self.game_map.cell_size - 2,
                self.game_map.cell_size - 2
            )
            pygame.draw.rect(self.screen, path_color, rect, 3)
        
        # Draw player
        x, y = self.player_pos
        player_rect = pygame.Rect(
            x * self.game_map.cell_size + 10,
            y * self.game_map.cell_size + 10,
            self.game_map.cell_size - 2,
            self.game_map.cell_size - 2
        )
        pygame.draw.rect(self.screen, (255, 50, 50), player_rect)
        
        self.draw_dashboard()
        pygame.display.flip()
    
    def draw_dashboard(self):
        # Main dashboard area
        dashboard_rect = pygame.Rect(720, 10, 270, 680)
        pygame.draw.rect(self.screen, (40, 40, 80), dashboard_rect)
        pygame.draw.rect(self.screen, (70, 70, 120), dashboard_rect, 2)
        
        y_offset = 20
        
        # Title
        title = self.title_font.render("RVCE CAMPUS RUNNER", True, (255, 255, 0))
        self.screen.blit(title, (730, y_offset))
        y_offset += 40
        
        # Score and Time
        score_text = self.large_font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (730, y_offset))
        y_offset += 30
        
        time_color = (255, 255, 255) if self.time_remaining > 60 else (255, 100, 100)
        time_text = self.large_font.render(f"TIME: {self.time_remaining}s", True, time_color)
        self.screen.blit(time_text, (730, y_offset))
        y_offset += 40
        
        # Algorithm Info
        algo_title = self.large_font.render("PATHFINDING ALGORITHMS:", True, (255, 200, 100))
        self.screen.blit(algo_title, (730, y_offset))
        y_offset += 30
        
        bfs_color = (0, 255, 0) if self.path_algorithm == "BFS" else (150, 150, 150)
        astar_color = (100, 150, 255) if self.path_algorithm == "A*" else (150, 150, 150)
        
        bfs_text = self.font.render("BFS (B key) - Green Path", True, bfs_color)
        self.screen.blit(bfs_text, (730, y_offset))
        y_offset += 20
        
        astar_text = self.font.render("A* (A key) - Blue Path", True, astar_color)
        self.screen.blit(astar_text, (730, y_offset))
        y_offset += 20
        
        if self.current_path:
            algo_text = self.font.render(f"Active: {self.path_algorithm}", True, (255, 255, 255))
            self.screen.blit(algo_text, (730, y_offset))
            y_offset += 20
            
            nodes_text = self.font.render(f"Nodes explored: {self.algorithm_stats[self.path_algorithm]}", True, (200, 200, 255))
            self.screen.blit(nodes_text, (730, y_offset))
            y_offset += 20
        
        y_offset += 20
        
        # Current Task
        task_title = self.large_font.render("CURRENT MISSION:", True, (255, 200, 100))
        self.screen.blit(task_title, (730, y_offset))
        y_offset += 30
        
        if self.task_manager.current_task:
            task = self.task_manager.current_task
            task_name = self.font.render(f"Task: {task['name']}", True, (200, 255, 200))
            self.screen.blit(task_name, (730, y_offset))
            y_offset += 25
            
            # Riddle
            riddle_lines = task['riddle'].split('\n')
            for line in riddle_lines:
                riddle_text = self.font.render(line, True, (255, 255, 200))
                self.screen.blit(riddle_text, (730, y_offset))
                y_offset += 20
            
            y_offset += 10
            
            building_text = self.font.render(f"Building: {task['building']}", True, (200, 200, 255))
            self.screen.blit(building_text, (730, y_offset))
            y_offset += 25
            
            points_text = self.font.render(f"Points: {task['points']}", True, (255, 200, 100))
            self.screen.blit(points_text, (730, y_offset))
            y_offset += 25
            
            hint_text = self.font.render(f"Hint: {task['hint']}", True, (200, 200, 200))
            self.screen.blit(hint_text, (730, y_offset))
            y_offset += 40
        else:
            no_task = self.font.render("No active task", True, (200, 200, 200))
            self.screen.blit(no_task, (730, y_offset))
            y_offset += 40
        
        # Completed Tasks
        completed_title = self.large_font.render("COMPLETED TASKS:", True, (100, 255, 100))
        self.screen.blit(completed_title, (730, y_offset))
        y_offset += 30
        
        completed_count = len(self.task_manager.completed_tasks)
        total_tasks = len(self.task_manager.tasks)
        progress_text = self.font.render(f"Progress: {completed_count}/{total_tasks}", True, (200, 255, 200))
        self.screen.blit(progress_text, (730, y_offset))
        y_offset += 25
        
        for task_id in self.task_manager.completed_tasks:
            task = self.task_manager.tasks[task_id]
            completed_task = self.font.render(f"✓ {task['name']}", True, (100, 255, 100))
            self.screen.blit(completed_task, (730, y_offset))
            y_offset += 20
        
        y_offset += 20
        
        # Controls
        controls_title = self.large_font.render("CONTROLS:", True, (255, 200, 100))
        self.screen.blit(controls_title, (730, y_offset))
        y_offset += 30
        
        controls = [
            "Arrow Keys - Move",
            "B - BFS Path (Green)",
            "A - A* Path (Blue)", 
            "U - Undo move",
            "C - Clear path",
            "P - Pause",
            "N - Next task",
            "R - Restart"
        ]
        
        for control in controls:
            control_text = self.font.render(control, True, (200, 200, 255))
            self.screen.blit(control_text, (730, y_offset))
            y_offset += 20
        
        # Game state messages
        if self.state == GameState.PAUSED:
            self.draw_centered_message("PAUSED", (255, 255, 0))
        elif self.state == GameState.VICTORY:
            self.draw_centered_message("ACADEMIC VICTORY! All tasks completed!", (0, 255, 0))
            restart = self.font.render("Press R to play again", True, (255, 255, 255))
            self.screen.blit(restart, (self.screen_width//2 - 80, self.screen_height//2 + 30))
        elif self.state == GameState.GAME_OVER:
            self.draw_centered_message("TIME'S UP! Game Over", (255, 50, 50))
            restart = self.font.render("Press R to try again", True, (255, 255, 255))
            self.screen.blit(restart, (self.screen_width//2 - 80, self.screen_height//2 + 30))
    
    def draw_centered_message(self, message, color):
        message_text = self.title_font.render(message, True, color)
        text_rect = message_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
        self.screen.blit(message_text, text_rect)
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(10)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = RVCECampusRunner()
    game.run()