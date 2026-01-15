"""
Game Dynamics Module for RVCE Campus Runner
Contains dynamic map events, tile interactions, NPCs, and camera system
"""
import pygame
import math
import random
from collections import deque
from enum import Enum

# ==================== TILE TYPES ====================
class TileType(Enum):
    """Different tile types with unique effects"""
    NORMAL = 0       # Regular walkable path
    WALL = 1         # Non-walkable
    ICE = 2          # Slide extra cells
    GRASS = 3        # Slow movement
    PORTAL_A = 4     # Teleport to Portal B
    PORTAL_B = 5     # Teleport to Portal A
    TRAP = 6         # Lose time
    BOOSTER = 7      # Speed burst
    CONSTRUCTION = 8 # Temporarily blocked
    WATER = 9        # Very slow, requires detour
    LOCKED_GATE = 10 # Needs key
    KEY = 11         # Pickup key item


# Tile properties
TILE_PROPERTIES = {
    TileType.NORMAL: {'walkable': True, 'weight': 1, 'color': (60, 65, 80)},
    TileType.WALL: {'walkable': False, 'weight': float('inf'), 'color': (120, 80, 100)},
    TileType.ICE: {'walkable': True, 'weight': 0.5, 'color': (150, 220, 255), 'slide': 2},
    TileType.GRASS: {'walkable': True, 'weight': 2, 'color': (80, 150, 80)},
    TileType.PORTAL_A: {'walkable': True, 'weight': 1, 'color': (200, 100, 255)},
    TileType.PORTAL_B: {'walkable': True, 'weight': 1, 'color': (255, 100, 200)},
    TileType.TRAP: {'walkable': True, 'weight': 1, 'color': (255, 80, 80), 'time_penalty': 5},
    TileType.BOOSTER: {'walkable': True, 'weight': 0.3, 'color': (255, 220, 50)},
    TileType.CONSTRUCTION: {'walkable': False, 'weight': float('inf'), 'color': (255, 150, 50)},
    TileType.WATER: {'walkable': True, 'weight': 4, 'color': (50, 100, 200)},
    TileType.LOCKED_GATE: {'walkable': False, 'weight': float('inf'), 'color': (150, 100, 50)},
    TileType.KEY: {'walkable': True, 'weight': 1, 'color': (255, 215, 0)},
}


# ==================== MAP EVENTS ====================
class MapEventType(Enum):
    """Types of dynamic map events"""
    CONSTRUCTION = 1    # Blocks paths temporarily
    RAIN = 2            # Slows movement on outdoor tiles
    FIRE_DRILL = 3      # Forces evacuation routes
    LOCKED_GATE = 4     # Blocks until key found
    PORTAL_SPAWN = 5    # Creates portal pair


class MapEvent:
    """Base class for dynamic map events"""
    
    def __init__(self, event_type, duration, positions=None):
        self.event_type = event_type
        self.duration = duration  # In seconds
        self.time_remaining = duration
        self.positions = positions or []
        self.active = False
        self.original_tiles = {}  # Store original tile values
        
    def apply(self, game_map, tile_map):
        """Apply the event to the map"""
        self.active = True
        # Store original tiles
        for pos in self.positions:
            x, y = pos
            if 0 <= x < game_map.width and 0 <= y < game_map.height:
                self.original_tiles[pos] = tile_map[y][x]
        
    def revert(self, game_map, tile_map):
        """Revert the event changes"""
        self.active = False
        for pos, original_tile in self.original_tiles.items():
            x, y = pos
            if 0 <= x < game_map.width and 0 <= y < game_map.height:
                tile_map[y][x] = original_tile
                
    def update(self, dt):
        """Update event timer, returns True if still active"""
        if self.active:
            self.time_remaining -= dt
            return self.time_remaining > 0
        return False


class ConstructionEvent(MapEvent):
    """Construction zone that blocks paths"""
    
    def __init__(self, positions, duration=30):
        super().__init__(MapEventType.CONSTRUCTION, duration, positions)
        
    def apply(self, game_map, tile_map):
        super().apply(game_map, tile_map)
        for pos in self.positions:
            x, y = pos
            if 0 <= x < game_map.width and 0 <= y < game_map.height:
                tile_map[y][x] = TileType.CONSTRUCTION


class RainEvent(MapEvent):
    """Rain that slows movement on outdoor tiles"""
    
    def __init__(self, duration=20):
        super().__init__(MapEventType.RAIN, duration, [])
        self.rain_intensity = 1.0
        self.rain_drops = []
        
    def apply(self, game_map, tile_map):
        self.active = True
        # Rain affects movement speed globally
        self.rain_intensity = 2.0  # Double movement cost
        # Generate rain drops for visual effect
        self.rain_drops = []
        
    def revert(self, game_map, tile_map):
        self.active = False
        self.rain_intensity = 1.0
        self.rain_drops = []
        
    def update(self, dt):
        if self.active:
            self.time_remaining -= dt
            # Update rain drops
            return self.time_remaining > 0
        return False


class FireDrillEvent(MapEvent):
    """Fire drill that forces specific evacuation routes"""
    
    def __init__(self, blocked_positions, duration=25):
        super().__init__(MapEventType.FIRE_DRILL, duration, blocked_positions)
        self.alarm_flash = 0
        
    def apply(self, game_map, tile_map):
        super().apply(game_map, tile_map)
        # Block certain areas, force specific routes
        for pos in self.positions:
            x, y = pos
            if 0 <= x < game_map.width and 0 <= y < game_map.height:
                tile_map[y][x] = TileType.CONSTRUCTION
                
    def update(self, dt):
        if self.active:
            self.time_remaining -= dt
            self.alarm_flash = (self.alarm_flash + dt * 5) % 2
            return self.time_remaining > 0
        return False


# ==================== EVENT MANAGER ====================
class EventManager:
    """Manages dynamic map events with an event queue"""
    
    def __init__(self):
        self.event_queue = deque()  # Upcoming events
        self.active_events = []     # Currently active events
        self.event_timer = 0
        self.next_event_time = 15   # First event after 15 seconds
        self.event_interval = 20    # New event every 20 seconds
        self.available_positions = []
        
    def set_available_positions(self, game_map, tile_map):
        """Find positions where events can spawn"""
        self.available_positions = []
        for y in range(game_map.height):
            for x in range(game_map.width):
                if tile_map[y][x] == TileType.NORMAL:
                    self.available_positions.append((x, y))
                    
    def generate_random_event(self, game_map):
        """Generate a random event"""
        if not self.available_positions:
            return None
            
        event_type = random.choice([
            MapEventType.CONSTRUCTION,
            MapEventType.RAIN,
            MapEventType.FIRE_DRILL,
        ])
        
        if event_type == MapEventType.CONSTRUCTION:
            # Pick 2-4 adjacent positions for construction
            center = random.choice(self.available_positions)
            positions = [center]
            cx, cy = center
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                if random.random() > 0.5:
                    pos = (cx + dx, cy + dy)
                    if pos in self.available_positions:
                        positions.append(pos)
            return ConstructionEvent(positions[:4], duration=random.randint(15, 30))
            
        elif event_type == MapEventType.RAIN:
            return RainEvent(duration=random.randint(15, 25))
            
        elif event_type == MapEventType.FIRE_DRILL:
            # Block some paths
            positions = random.sample(self.available_positions, 
                                     min(5, len(self.available_positions)))
            return FireDrillEvent(positions, duration=random.randint(20, 30))
            
        return None
        
    def schedule_event(self, event):
        """Add event to queue"""
        self.event_queue.append(event)
        
    def update(self, dt, game_map, tile_map, graph_rebuild_callback):
        """Update all events and spawn new ones"""
        # Track if graph needs rebuild
        graph_changed = False
        
        # Update event timer
        self.event_timer += dt
        
        # Spawn new events periodically
        if self.event_timer >= self.next_event_time:
            event = self.generate_random_event(game_map)
            if event:
                self.schedule_event(event)
            self.next_event_time = self.event_timer + self.event_interval
            
        # Activate queued events
        while self.event_queue:
            event = self.event_queue.popleft()
            event.apply(game_map, tile_map)
            self.active_events.append(event)
            graph_changed = True
            
        # Update active events
        still_active = []
        for event in self.active_events:
            if event.update(dt):
                still_active.append(event)
            else:
                event.revert(game_map, tile_map)
                graph_changed = True
        self.active_events = still_active
        
        # Rebuild graph if needed
        if graph_changed and graph_rebuild_callback:
            graph_rebuild_callback()
            
        return graph_changed
        
    def get_rain_intensity(self):
        """Get current rain effect multiplier"""
        for event in self.active_events:
            if isinstance(event, RainEvent):
                return event.rain_intensity
        return 1.0
        
    def is_fire_drill_active(self):
        """Check if fire drill is happening"""
        return any(isinstance(e, FireDrillEvent) for e in self.active_events)


# ==================== NPC SYSTEM ====================
class NPCState(Enum):
    """NPC behavior states (Finite State Machine)"""
    IDLE = 0
    PATROL = 1
    CHASE = 2
    RETURN = 3
    INTERACT = 4


class NPCType(Enum):
    """Types of NPCs"""
    STUDENT = 1
    SECURITY = 2
    PROFESSOR = 3


class NPC:
    """Non-Player Character with AI behavior"""
    
    def __init__(self, npc_type, start_pos, patrol_points=None):
        self.npc_type = npc_type
        self.pos = start_pos
        self.start_pos = start_pos
        self.target_pos = None
        self.current_path = []
        self.path_index = 0
        
        # Patrol system
        self.patrol_points = patrol_points or [start_pos]
        self.patrol_index = 0
        
        # State machine
        self.state = NPCState.PATROL if patrol_points else NPCState.IDLE
        self.state_timer = 0
        self.detection_range = 4 if npc_type == NPCType.SECURITY else 3
        self.chase_speed = 1.5 if npc_type == NPCType.SECURITY else 1.0
        
        # Animation
        self.frame = 0
        self.direction = (0, 1)  # Facing direction
        
        # Interaction
        self.dialogue = self._get_dialogue()
        self.has_interacted = False
        
        # Movement timing
        self.move_timer = 0
        self.move_delay = 0.3  # Seconds between moves
        
    def _get_dialogue(self):
        """Get NPC dialogue based on type"""
        dialogues = {
            NPCType.STUDENT: [
                "Hey! Need help finding a building?",
                "The library is a great place to study!",
                "Have you tried the food court yet?",
            ],
            NPCType.SECURITY: [
                "Keep moving, no loitering!",
                "ID card please... just kidding!",
                "Stay on the designated paths.",
            ],
            NPCType.PROFESSOR: [
                "Remember, A* is more efficient than BFS!",
                "Algorithms are the heart of computer science.",
                "Don't forget about graph theory!",
            ],
        }
        return random.choice(dialogues.get(self.npc_type, ["..."]))
        
    def get_color(self):
        """Get NPC color based on type"""
        colors = {
            NPCType.STUDENT: (100, 200, 100),    # Green
            NPCType.SECURITY: (100, 100, 255),   # Blue
            NPCType.PROFESSOR: (200, 150, 100),  # Brown
        }
        return colors.get(self.npc_type, (150, 150, 150))
    
    def get_label(self):
        """Get NPC label for display"""
        labels = {
            NPCType.STUDENT: "Student",
            NPCType.SECURITY: "Guard",
            NPCType.PROFESSOR: "Prof",
        }
        return labels.get(self.npc_type, "NPC")
    
    def get_icon(self):
        """Get NPC icon emoji"""
        icons = {
            NPCType.STUDENT: "👨‍🎓",
            NPCType.SECURITY: "👮",
            NPCType.PROFESSOR: "👨‍🏫",
        }
        return icons.get(self.npc_type, "👤")
        
    def update(self, dt, player_pos, game_map, find_path_func):
        """Update NPC behavior using FSM"""
        self.frame += 1
        self.state_timer += dt
        self.move_timer += dt
        
        # Calculate distance to player
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # State transitions
        if self.state == NPCState.IDLE:
            # Randomly start patrolling
            if self.state_timer > 3:
                self.state = NPCState.PATROL
                self.state_timer = 0
                
        elif self.state == NPCState.PATROL:
            # Check for player detection (security guards chase)
            if self.npc_type == NPCType.SECURITY and distance < self.detection_range:
                self.state = NPCState.CHASE
                self.state_timer = 0
            else:
                # Move along patrol route
                if self.move_timer >= self.move_delay:
                    self._patrol_move(game_map, find_path_func)
                    self.move_timer = 0
                    
        elif self.state == NPCState.CHASE:
            # Chase player
            if distance > self.detection_range * 2:
                # Lost player, return to patrol
                self.state = NPCState.RETURN
                self.state_timer = 0
            elif distance < 1.5:
                # Caught up to player
                self.state = NPCState.INTERACT
                self.state_timer = 0
            else:
                # Continue chasing
                if self.move_timer >= self.move_delay / self.chase_speed:
                    self._chase_move(player_pos, game_map, find_path_func)
                    self.move_timer = 0
                    
        elif self.state == NPCState.RETURN:
            # Return to patrol start
            if self.pos == self.start_pos:
                self.state = NPCState.PATROL
                self.state_timer = 0
            else:
                if self.move_timer >= self.move_delay:
                    self._return_move(game_map, find_path_func)
                    self.move_timer = 0
                    
        elif self.state == NPCState.INTERACT:
            # Brief interaction then return to patrol
            if self.state_timer > 2:
                self.state = NPCState.PATROL
                self.state_timer = 0
                self.has_interacted = True
                
    def _patrol_move(self, game_map, find_path_func):
        """Move to next patrol point"""
        if not self.patrol_points:
            return
            
        target = self.patrol_points[self.patrol_index]
        
        if self.pos == target:
            # Reached patrol point, go to next
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
            target = self.patrol_points[self.patrol_index]
            
        # Find path to target
        if not self.current_path or self.current_path[-1] != target:
            self.current_path = find_path_func(self.pos, target)
            self.path_index = 0
            
        # Move along path
        if self.current_path and self.path_index < len(self.current_path):
            next_pos = self.current_path[self.path_index]
            if game_map.is_walkable(next_pos[0], next_pos[1]):
                self.direction = (next_pos[0] - self.pos[0], next_pos[1] - self.pos[1])
                self.pos = next_pos
                self.path_index += 1
                
    def _chase_move(self, player_pos, game_map, find_path_func):
        """Chase the player using A*"""
        self.current_path = find_path_func(self.pos, player_pos)
        
        if self.current_path and len(self.current_path) > 1:
            next_pos = self.current_path[1]  # Skip current position
            if game_map.is_walkable(next_pos[0], next_pos[1]):
                self.direction = (next_pos[0] - self.pos[0], next_pos[1] - self.pos[1])
                self.pos = next_pos
                
    def _return_move(self, game_map, find_path_func):
        """Return to start position"""
        if self.pos == self.start_pos:
            return
            
        self.current_path = find_path_func(self.pos, self.start_pos)
        
        if self.current_path and len(self.current_path) > 1:
            next_pos = self.current_path[1]
            if game_map.is_walkable(next_pos[0], next_pos[1]):
                self.direction = (next_pos[0] - self.pos[0], next_pos[1] - self.pos[1])
                self.pos = next_pos


class NPCManager:
    """Manages all NPCs in the game"""
    
    def __init__(self):
        self.npcs = []
        
    def spawn_npcs(self, game_map, buildings):
        """Spawn NPCs around the campus"""
        self.npcs = []
        
        # Spawn students near buildings
        building_positions = list(buildings.values())
        for i in range(3):
            if i < len(building_positions):
                start = building_positions[i]
                # Create patrol route between nearby buildings
                patrol = [start]
                if i + 1 < len(building_positions):
                    patrol.append(building_positions[i + 1])
                self.npcs.append(NPC(NPCType.STUDENT, start, patrol))
                
        # Spawn security guard
        if len(building_positions) > 2:
            security_start = building_positions[len(building_positions) // 2]
            security_patrol = [building_positions[0], building_positions[-1]]
            self.npcs.append(NPC(NPCType.SECURITY, security_start, security_patrol))
            
        # Spawn professor
        if len(building_positions) > 4:
            prof_start = building_positions[3]
            self.npcs.append(NPC(NPCType.PROFESSOR, prof_start, [prof_start]))
            
    def update(self, dt, player_pos, game_map, find_path_func):
        """Update all NPCs"""
        for npc in self.npcs:
            npc.update(dt, player_pos, game_map, find_path_func)
            
    def check_interaction(self, player_pos):
        """Check if player is near any NPC for interaction"""
        for npc in self.npcs:
            dx = player_pos[0] - npc.pos[0]
            dy = player_pos[1] - npc.pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 1.5:
                return npc
        return None
        
    def get_blocking_npc(self, pos):
        """Check if an NPC is blocking a position"""
        for npc in self.npcs:
            if npc.pos == pos:
                return npc
        return None


# ==================== CAMERA SYSTEM ====================
class Camera:
    """Camera that follows player with smooth movement and zoom"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Camera position (top-left corner in world coords)
        self.x = 0
        self.y = 0
        
        # Target position for smooth following
        self.target_x = 0
        self.target_y = 0
        
        # Zoom level (1.0 = normal, 2.0 = zoomed in 2x)
        self.zoom = 1.5
        self.target_zoom = 1.5
        self.min_zoom = 0.8
        self.max_zoom = 2.5
        
        # Smooth following speed
        self.follow_speed = 5.0
        
        # Viewport dimensions in world units
        self.visible_width = 0
        self.visible_height = 0
        self.update_viewport()
        
    def update_viewport(self):
        """Calculate visible area based on zoom"""
        self.visible_width = self.screen_width / self.zoom
        self.visible_height = self.screen_height / self.zoom
        
    def set_target(self, world_x, world_y):
        """Set camera target to center on position"""
        self.target_x = world_x - self.visible_width / 2
        self.target_y = world_y - self.visible_height / 2
        
    def update(self, dt, player_world_pos):
        """Update camera position with smooth following"""
        # Center on player
        target_x = player_world_pos[0] - self.visible_width / 2
        target_y = player_world_pos[1] - self.visible_height / 2
        
        # Use faster interpolation for responsive following
        lerp_speed = min(1.0, self.follow_speed * dt)
        self.x += (target_x - self.x) * lerp_speed
        self.y += (target_y - self.y) * lerp_speed
        
        # Zoom interpolation
        self.zoom += (self.target_zoom - self.zoom) * lerp_speed
        self.update_viewport()
    
    def snap_to(self, player_world_pos):
        """Instantly center camera on position (no smoothing)"""
        self.x = player_world_pos[0] - self.visible_width / 2
        self.y = player_world_pos[1] - self.visible_height / 2
        self.update_viewport()
        
    def zoom_in(self):
        """Zoom in"""
        self.target_zoom = min(self.max_zoom, self.target_zoom + 0.2)
        
    def zoom_out(self):
        """Zoom out"""
        self.target_zoom = max(self.min_zoom, self.target_zoom - 0.2)
        
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (world_x - self.x) * self.zoom
        screen_y = (world_y - self.y) * self.zoom
        return (int(screen_x), int(screen_y))
        
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        world_x = screen_x / self.zoom + self.x
        world_y = screen_y / self.zoom + self.y
        return (world_x, world_y)
        
    def is_visible(self, world_x, world_y, margin=1):
        """Check if a world position is visible on screen"""
        return (self.x - margin <= world_x <= self.x + self.visible_width + margin and
                self.y - margin <= world_y <= self.y + self.visible_height + margin)
        
    def clamp_to_map(self, map_width, map_height, cell_size):
        """Keep camera within map bounds"""
        max_x = map_width * cell_size - self.visible_width
        max_y = map_height * cell_size - self.visible_height
        
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))


# ==================== FOG OF WAR ====================
class FogOfWar:
    """Fog of war system - unexplored tiles are hidden"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # 0 = unexplored, 1 = explored but not visible, 2 = currently visible
        self.visibility = [[0 for _ in range(width)] for _ in range(height)]
        self.view_range = 5  # How far player can see
        
    def update(self, player_pos):
        """Update visibility based on player position"""
        px, py = player_pos
        
        # Dim previously visible tiles to explored
        for y in range(self.height):
            for x in range(self.width):
                if self.visibility[y][x] == 2:
                    self.visibility[y][x] = 1
                    
        # Reveal tiles around player
        for dy in range(-self.view_range, self.view_range + 1):
            for dx in range(-self.view_range, self.view_range + 1):
                nx, ny = px + dx, py + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance <= self.view_range:
                        self.visibility[ny][nx] = 2
                        
    def get_visibility(self, x, y):
        """Get visibility state of a tile"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.visibility[y][x]
        return 0
        
    def is_explored(self, x, y):
        """Check if tile has been explored"""
        return self.get_visibility(x, y) > 0
        
    def is_visible(self, x, y):
        """Check if tile is currently visible"""
        return self.get_visibility(x, y) == 2
        
    def get_alpha(self, x, y):
        """Get alpha value for rendering fog"""
        vis = self.get_visibility(x, y)
        if vis == 0:
            return 255  # Full fog
        elif vis == 1:
            return 150  # Partial fog (explored)
        else:
            return 0    # No fog (visible)


# ==================== TILE EFFECT HANDLER ====================
class TileEffectHandler:
    """Handles tile-based effects on player"""
    
    def __init__(self):
        self.portal_a_pos = None
        self.portal_b_pos = None
        self.booster_active = False
        self.booster_timer = 0
        self.slide_direction = None
        self.slide_remaining = 0
        self.has_key = False
        self.triggered_traps = set()
        
    def set_portals(self, pos_a, pos_b):
        """Set portal positions"""
        self.portal_a_pos = pos_a
        self.portal_b_pos = pos_b
        
    def process_tile(self, player_pos, tile_type, direction, game_map):
        """Process tile effect and return new position, time penalty, and message"""
        new_pos = player_pos
        time_penalty = 0
        message = None
        
        if tile_type == TileType.ICE:
            # Start sliding
            props = TILE_PROPERTIES[TileType.ICE]
            self.slide_direction = direction
            self.slide_remaining = props.get('slide', 2)
            message = "❄️ ICE!"
            
        elif tile_type == TileType.TRAP:
            trap_key = player_pos
            if trap_key not in self.triggered_traps:
                props = TILE_PROPERTIES[TileType.TRAP]
                time_penalty = props.get('time_penalty', 5)
                self.triggered_traps.add(trap_key)
                message = f"⚠️ TRAP! -{time_penalty}s"
                
        elif tile_type == TileType.BOOSTER:
            self.booster_active = True
            self.booster_timer = 3.0  # 3 seconds of speed boost
            message = "⚡ SPEED BOOST!"
            
        elif tile_type == TileType.PORTAL_A and self.portal_b_pos:
            new_pos = self.portal_b_pos
            message = "🌀 TELEPORT!"
            
        elif tile_type == TileType.PORTAL_B and self.portal_a_pos:
            new_pos = self.portal_a_pos
            message = "🌀 TELEPORT!"
            
        elif tile_type == TileType.KEY:
            self.has_key = True
            message = "🔑 KEY ACQUIRED!"
            
        elif tile_type == TileType.GRASS:
            message = "🌿 Grass slows you..."
            
        return new_pos, time_penalty, message
        
    def process_slide(self, player_pos, game_map, tile_map):
        """Process ice sliding effect"""
        if self.slide_remaining > 0 and self.slide_direction:
            dx, dy = self.slide_direction
            new_x = player_pos[0] + dx
            new_y = player_pos[1] + dy
            
            if game_map.is_walkable(new_x, new_y):
                self.slide_remaining -= 1
                return (new_x, new_y)
            else:
                # Hit wall, stop sliding
                self.slide_remaining = 0
                self.slide_direction = None
                
        return player_pos
        
    def update(self, dt):
        """Update effect timers"""
        if self.booster_active:
            self.booster_timer -= dt
            if self.booster_timer <= 0:
                self.booster_active = False
                
    def get_move_speed_multiplier(self):
        """Get current movement speed multiplier"""
        if self.booster_active:
            return 2.0  # Double speed
        return 1.0
        
    def can_unlock_gate(self):
        """Check if player can unlock gates"""
        return self.has_key


# ==================== MINI-MAP ====================
class MiniMap:
    """Mini-map showing player position and objectives"""
    
    def __init__(self, x, y, size=150):
        self.x = x
        self.y = y
        self.size = size
        self.border = 3
        
    def draw(self, screen, game_map, player_pos, target_pos, npcs, fog):
        """Draw the mini-map"""
        # Background
        pygame.draw.rect(screen, (20, 25, 35), 
                        (self.x, self.y, self.size, self.size))
        pygame.draw.rect(screen, (60, 70, 100), 
                        (self.x, self.y, self.size, self.size), self.border)
        
        # Calculate scale
        scale_x = (self.size - self.border * 2) / game_map.width
        scale_y = (self.size - self.border * 2) / game_map.height
        scale = min(scale_x, scale_y)
        
        offset_x = self.x + self.border + (self.size - self.border * 2 - game_map.width * scale) / 2
        offset_y = self.y + self.border + (self.size - self.border * 2 - game_map.height * scale) / 2
        
        # Draw map tiles
        for y in range(game_map.height):
            for x in range(game_map.width):
                # Check fog
                if fog and not fog.is_explored(x, y):
                    continue
                    
                px = int(offset_x + x * scale)
                py = int(offset_y + y * scale)
                
                if game_map.get_cell_value(x, y) == 1:
                    color = (80, 60, 70)
                else:
                    color = (50, 55, 65)
                    
                pygame.draw.rect(screen, color, (px, py, max(2, int(scale)), max(2, int(scale))))
                
        # Draw target
        if target_pos:
            tx = int(offset_x + target_pos[0] * scale)
            ty = int(offset_y + target_pos[1] * scale)
            pygame.draw.circle(screen, (255, 220, 50), (tx, ty), 4)
            
        # Draw NPCs
        for npc in npcs:
            nx = int(offset_x + npc.pos[0] * scale)
            ny = int(offset_y + npc.pos[1] * scale)
            pygame.draw.circle(screen, npc.get_color(), (nx, ny), 2)
            
        # Draw player
        ppx = int(offset_x + player_pos[0] * scale)
        ppy = int(offset_y + player_pos[1] * scale)
        pygame.draw.circle(screen, (255, 100, 100), (ppx, ppy), 4)
        
        # Label
        font = pygame.font.SysFont('Segoe UI', 10)
        label = font.render("MAP", True, (150, 160, 180))
        screen.blit(label, (self.x + 5, self.y + 5))
