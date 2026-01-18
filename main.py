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
        
        elif icon_type == "stage":
            pygame.draw.polygon(surface, (255, 180, 80),
            [(10, 45), (32, 15), (54, 45)])
            pygame.draw.rect(surface, (120, 80, 50), (12, 45, 40, 8))

        elif icon_type == "civil":
            pygame.draw.rect(surface, (180, 180, 180), (14, 18, 36, 30))
            pygame.draw.line(surface, (90, 90, 90), (14, 30), (50, 30), 2)

        elif icon_type == "mechanical":
            pygame.draw.circle(surface, (160, 160, 160), (32, 32), 14, 3)
            pygame.draw.circle(surface, (100, 100, 100), (32, 32), 5)

        elif icon_type == "biotech":
            pygame.draw.circle(surface, (100, 200, 120), (32, 28), 10)
            pygame.draw.line(surface, (80, 160, 100), (32, 38), (32, 52), 3)

        elif icon_type == "ai":
            pygame.draw.rect(surface, (100, 200, 255), (16, 18, 32, 24))
            pygame.draw.circle(surface, (255, 255, 255), (32, 30), 3)

        elif icon_type == "electronics":
            pygame.draw.line(surface, (255, 255, 100), (12, 32), (52, 32), 3)

        elif icon_type == "management":
            pygame.draw.rect(surface, (200, 180, 100), (18, 20, 28, 24))

        elif icon_type == "maintenance":
            pygame.draw.rect(surface, (150, 150, 150), (18, 18, 28, 28))
            pygame.draw.line(surface, (90, 90, 90), (18, 32), (46, 32), 3)

        elif icon_type == "power":
            pygame.draw.polygon(surface, (255, 220, 0),
                [(30, 10), (36, 30), (28, 30), (34, 50)])

        elif icon_type == "code":
            pygame.draw.line(surface, (150, 255, 150), (20, 20), (30, 32), 3)
            pygame.draw.line(surface, (150, 255, 150), (30, 32), (20, 44), 3)

        elif icon_type == "signal":
            pygame.draw.arc(surface, (200, 200, 255), (12, 12, 40, 40), 0, 3.14, 3)

        elif icon_type == "chemistry":
            pygame.draw.polygon(surface, (200, 100, 100),
                [(28, 14), (36, 14), (42, 44), (22, 44)])

        elif icon_type == "vip":
            pygame.draw.circle(surface, (255, 215, 0), (32, 32), 14, 3)

        elif icon_type == "aerospace":
            pygame.draw.polygon(surface, (180, 180, 255),
                [(32, 10), (38, 50), (32, 44), (26, 50)])

            
        elif icon_type == "default":
            # Generic building icon
            pygame.draw.rect(surface, (150, 150, 200), (16, 20, 32, 28), border_radius=3)
            pygame.draw.rect(surface, (100, 150, 255), (22, 26, 8, 8))  # Window
            pygame.draw.rect(surface, (100, 150, 255), (34, 26, 8, 8))  # Window
            pygame.draw.rect(surface, (80, 80, 120), (28, 38, 8, 10))  # Door
            
        return surface
    
    @staticmethod
    def create_player_sprite(frame=0, size=32):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        bob = math.sin(frame * 0.4) * 2
        cx, cy = size // 2, size // 2 - int(bob)

        # Shadow
        pygame.draw.ellipse(surface, (0, 0, 0, 60),
            (6, size - 8, size - 12, 6))

        # Body
        pygame.draw.circle(surface, (80, 160, 255), (cx, cy), 10)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 10, 2)

        # Eyes
        pygame.draw.circle(surface, (0, 0, 0), (cx - 3, cy - 2), 2)
        pygame.draw.circle(surface, (0, 0, 0), (cx + 3, cy - 2), 2)

        # Feet animation
        step = frame % 2
        pygame.draw.line(surface, (50, 50, 50),
            (cx - 4, cy + 10), (cx - 6, cy + 14 + step), 2)
        pygame.draw.line(surface, (50, 50, 50),
            (cx + 4, cy + 10), (cx + 6, cy + 14 - step), 2)

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


class BuildingIconGenerator:
    """
    Generates custom building icons with geometric shapes and labels.
    Each building has a unique icon matching its semantic purpose.
    """
    
    # Category colors
    COLORS = {
        'admin': (70, 130, 180),      # Steel blue
        'academic': (100, 149, 237),   # Cornflower blue
        'hostel': (147, 112, 219),     # Medium purple
        'food': (255, 165, 0),         # Orange
        'sports': (50, 205, 50),       # Lime green
        'services': (220, 20, 60),     # Crimson
        'innovation': (255, 215, 0),   # Gold
        'science': (0, 206, 209),      # Dark turquoise
        'entry': (34, 139, 34),        # Forest green
    }
    
    @staticmethod
    def _create_base_surface(size=64):
        """Create a base transparent surface"""
        return pygame.Surface((size, size), pygame.SRCALPHA)
    
    @staticmethod
    def _add_label(surface, label, size=64):
        """Add building name label with black background"""
        font = pygame.font.SysFont('Segoe UI', 9, bold=True)
        text = font.render(label, True, (255, 255, 255))
        text_rect = text.get_rect(centerx=size//2, bottom=size-2)
        
        # Black background for label
        bg_rect = text_rect.inflate(4, 2)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect)
        surface.blit(text, text_rect)
        return surface
    
    @classmethod
    def main_entrance(cls, size=64):
        """Gate / archway / pillars"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['entry']
        cx, cy = size//2, size//2 - 8
        
        # Two pillars
        pygame.draw.rect(s, color, (cx-20, cy-10, 8, 30))
        pygame.draw.rect(s, color, (cx+12, cy-10, 8, 30))
        
        # Arch on top
        pygame.draw.arc(s, color, (cx-20, cy-20, 40, 30), 3.14, 0, 4)
        
        # Gate bars
        for i in range(-12, 13, 6):
            pygame.draw.line(s, (200, 200, 200), (cx+i, cy), (cx+i, cy+15), 1)
        
        return cls._add_label(s, "GATE", size)
    
    @classmethod
    def kotak_mahindra_bank(cls, size=64):
        """Bank building with currency symbol"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['services']
        cx, cy = size//2, size//2 - 8
        
        # Building shape
        pygame.draw.rect(s, color, (cx-18, cy-8, 36, 28), border_radius=3)
        
        # Pillars
        for i in [-12, 0, 12]:
            pygame.draw.rect(s, (255, 255, 255), (cx+i-2, cy-5, 4, 22))
        
        # Roof
        pygame.draw.polygon(s, (180, 20, 50), [(cx-20, cy-8), (cx, cy-18), (cx+20, cy-8)])
        
        # Rupee symbol
        font = pygame.font.SysFont('Segoe UI', 14, bold=True)
        rupee = font.render("₹", True, (255, 215, 0))
        s.blit(rupee, (cx-5, cy+2))
        
        return cls._add_label(s, "BANK", size)
    
    @classmethod
    def health_centre(cls, size=64):
        """Medical cross"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['services']
        cx, cy = size//2, size//2 - 8
        
        # White background circle
        pygame.draw.circle(s, (255, 255, 255), (cx, cy), 18)
        
        # Red cross
        pygame.draw.rect(s, color, (cx-4, cy-14, 8, 28))
        pygame.draw.rect(s, color, (cx-14, cy-4, 28, 8))
        
        return cls._add_label(s, "HEALTH", size)
    
    @classmethod
    def admin_block(cls, size=64):
        """Clipboard / office building"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['admin']
        cx, cy = size//2, size//2 - 8
        
        # Building
        pygame.draw.rect(s, color, (cx-16, cy-12, 32, 32), border_radius=2)
        
        # Windows grid
        for row in range(3):
            for col in range(3):
                pygame.draw.rect(s, (200, 220, 255), (cx-12+col*10, cy-8+row*8, 6, 5))
        
        # Door
        pygame.draw.rect(s, (50, 80, 120), (cx-4, cy+12, 8, 8))
        
        return cls._add_label(s, "ADMIN", size)
    
    @classmethod
    def iem_auditorium(cls, size=64):
        """Stage with curtain"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['admin']
        cx, cy = size//2, size//2 - 8
        
        # Stage base
        pygame.draw.rect(s, (100, 80, 60), (cx-20, cy+8, 40, 10))
        
        # Curtains
        pygame.draw.polygon(s, (180, 50, 50), [(cx-20, cy-15), (cx-20, cy+8), (cx-8, cy+8), (cx-14, cy-15)])
        pygame.draw.polygon(s, (180, 50, 50), [(cx+20, cy-15), (cx+20, cy+8), (cx+8, cy+8), (cx+14, cy-15)])
        
        # Stage light
        pygame.draw.circle(s, (255, 255, 200), (cx, cy-10), 6)
        
        return cls._add_label(s, "IEM AUD", size)
    
    @classmethod
    def library(cls, size=64):
        """Books / bookshelf"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['admin']
        cx, cy = size//2, size//2 - 8
        
        # Bookshelf
        pygame.draw.rect(s, (139, 90, 43), (cx-18, cy-12, 36, 30))
        
        # Books - different colors
        book_colors = [(200, 50, 50), (50, 150, 50), (50, 50, 200), (200, 200, 50), (200, 100, 150)]
        for i, bc in enumerate(book_colors):
            pygame.draw.rect(s, bc, (cx-14+i*6, cy-10, 5, 24))
        
        return cls._add_label(s, "LIBRARY", size)
    
    @classmethod
    def temple(cls, size=64):
        """Shrine with dome and bell"""
        s = cls._create_base_surface(size)
        color = (255, 165, 0)  # Orange/saffron
        cx, cy = size//2, size//2 - 8
        
        # Base
        pygame.draw.rect(s, (200, 200, 200), (cx-16, cy+5, 32, 12))
        
        # Dome
        pygame.draw.arc(s, color, (cx-14, cy-15, 28, 25), 3.14, 0, 3)
        pygame.draw.rect(s, color, (cx-14, cy-3, 28, 8))
        
        # Spire
        pygame.draw.polygon(s, color, [(cx, cy-20), (cx-4, cy-12), (cx+4, cy-12)])
        
        # Bell
        pygame.draw.circle(s, (218, 165, 32), (cx, cy+2), 4)
        
        return cls._add_label(s, "TEMPLE", size)
    
    @classmethod
    def mechanical_dept(cls, size=64):
        """Gear / cogwheel"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['academic']
        cx, cy = size//2, size//2 - 8
        
        # Main gear
        pygame.draw.circle(s, color, (cx, cy), 16, 4)
        pygame.draw.circle(s, color, (cx, cy), 6)
        
        # Gear teeth
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1, y1 = cx + 14 * math.cos(rad), cy + 14 * math.sin(rad)
            x2, y2 = cx + 20 * math.cos(rad), cy + 20 * math.sin(rad)
            pygame.draw.line(s, color, (x1, y1), (x2, y2), 4)
        
        return cls._add_label(s, "MECH", size)
    
    @classmethod
    def civil_dept(cls, size=64):
        """Bridge / column"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['academic']
        cx, cy = size//2, size//2 - 8
        
        # Bridge arch
        pygame.draw.arc(s, color, (cx-20, cy-5, 40, 20), 3.14, 0, 4)
        
        # Road deck
        pygame.draw.rect(s, (100, 100, 100), (cx-22, cy+5, 44, 6))
        
        # Pillars
        pygame.draw.rect(s, color, (cx-18, cy+5, 6, 12))
        pygame.draw.rect(s, color, (cx+12, cy+5, 6, 12))
        
        return cls._add_label(s, "CIVIL", size)
    
    @classmethod
    def chem_engg_physics_dept(cls, size=64):
        """Beaker + atom"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['science']
        cx, cy = size//2, size//2 - 8
        
        # Beaker
        pygame.draw.polygon(s, (200, 230, 255), [(cx-8, cy-12), (cx+8, cy-12), (cx+12, cy+12), (cx-12, cy+12)])
        pygame.draw.rect(s, color, (cx-12, cy+4, 24, 8))  # Liquid
        
        # Atom orbits (small)
        pygame.draw.ellipse(s, (255, 100, 100), (cx+6, cy-8, 16, 10), 1)
        pygame.draw.circle(s, (255, 100, 100), (cx+14, cy-3), 3)
        
        return cls._add_label(s, "CHEM-PHY", size)
    
    @classmethod
    def eee_dept(cls, size=64):
        """Lightning bolt"""
        s = cls._create_base_surface(size)
        color = (255, 255, 0)  # Yellow
        cx, cy = size//2, size//2 - 8
        
        # Lightning bolt
        points = [
            (cx+5, cy-18), (cx-5, cy-2), (cx+2, cy-2),
            (cx-8, cy+18), (cx+2, cy+2), (cx-5, cy+2)
        ]
        pygame.draw.polygon(s, color, points)
        pygame.draw.polygon(s, (255, 200, 0), points, 2)
        
        return cls._add_label(s, "EEE", size)
    
    @classmethod
    def ece_dept(cls, size=64):
        """Circuit / waveform"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['academic']
        cx, cy = size//2, size//2 - 8
        
        # Waveform
        points = []
        for i in range(40):
            x = cx - 18 + i
            y = cy + int(8 * math.sin(i * 0.4))
            points.append((x, y))
        pygame.draw.lines(s, (0, 255, 0), False, points, 2)
        
        # IC chip
        pygame.draw.rect(s, (50, 50, 50), (cx-10, cy+8, 20, 10))
        for i in range(4):
            pygame.draw.line(s, (200, 200, 200), (cx-8+i*5, cy+8), (cx-8+i*5, cy+4), 1)
        
        return cls._add_label(s, "ECE", size)
    
    @classmethod
    def cse_dept(cls, size=64):
        """Computer monitor / code brackets"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['academic']
        cx, cy = size//2, size//2 - 8
        
        # Monitor
        pygame.draw.rect(s, (60, 60, 60), (cx-16, cy-12, 32, 22), border_radius=2)
        pygame.draw.rect(s, (30, 30, 50), (cx-14, cy-10, 28, 18))
        
        # Code brackets < / >
        font = pygame.font.SysFont('Consolas', 12, bold=True)
        code = font.render("</>", True, (0, 255, 0))
        s.blit(code, (cx-10, cy-8))
        
        # Stand
        pygame.draw.rect(s, (80, 80, 80), (cx-4, cy+10, 8, 6))
        
        return cls._add_label(s, "CSE", size)
    
    @classmethod
    def telecom_dept(cls, size=64):
        """Signal tower with radio waves"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['academic']
        cx, cy = size//2, size//2 - 8
        
        # Tower
        pygame.draw.polygon(s, (150, 150, 150), [(cx, cy-15), (cx-10, cy+15), (cx+10, cy+15)])
        pygame.draw.line(s, (100, 100, 100), (cx-7, cy), (cx+7, cy), 2)
        pygame.draw.line(s, (100, 100, 100), (cx-5, cy+8), (cx+5, cy+8), 2)
        
        # Radio waves
        for i in range(3):
            pygame.draw.arc(s, (100, 200, 255), (cx-8-i*6, cy-15-i*4, 16+i*12, 12+i*4), 0.5, 2.6, 2)
        
        return cls._add_label(s, "TELECOM", size)
    
    @classmethod
    def mathematics_dept(cls, size=64):
        """Pi symbol / geometric pattern"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['academic']
        cx, cy = size//2, size//2 - 8
        
        # Pi symbol
        font = pygame.font.SysFont('Segoe UI', 28, bold=True)
        pi = font.render("π", True, color)
        pi_rect = pi.get_rect(center=(cx, cy-2))
        s.blit(pi, pi_rect)
        
        # Small geometric shapes
        pygame.draw.polygon(s, (255, 200, 100), [(cx-18, cy+10), (cx-10, cy+2), (cx-2, cy+10)], 2)
        pygame.draw.circle(s, (100, 200, 255), (cx+12, cy+6), 6, 2)
        
        return cls._add_label(s, "MATH", size)
    
    @classmethod
    def biotech_quadrangle(cls, size=64):
        """DNA helix"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['science']
        cx, cy = size//2, size//2 - 8
        
        # DNA helix strands
        for i in range(20):
            y = cy - 15 + i * 1.5
            x_offset = 8 * math.sin(i * 0.5)
            pygame.draw.circle(s, (0, 200, 100), (int(cx + x_offset), int(y)), 3)
            pygame.draw.circle(s, (100, 150, 255), (int(cx - x_offset), int(y)), 3)
            if i % 3 == 0:
                pygame.draw.line(s, (200, 200, 200), (int(cx + x_offset), int(y)), (int(cx - x_offset), int(y)), 1)
        
        return cls._add_label(s, "BIOTECH", size)
    
    @classmethod
    def green_house(cls, size=64):
        """Plant under glass"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['science']
        cx, cy = size//2, size//2 - 8
        
        # Glass dome
        pygame.draw.arc(s, (200, 255, 200), (cx-18, cy-12, 36, 30), 3.14, 0, 2)
        pygame.draw.line(s, (200, 255, 200), (cx-18, cy+3), (cx+18, cy+3), 2)
        
        # Plant
        pygame.draw.line(s, (100, 200, 100), (cx, cy+3), (cx, cy-5), 3)  # Stem
        pygame.draw.ellipse(s, (50, 180, 50), (cx-8, cy-12, 8, 10))  # Leaf
        pygame.draw.ellipse(s, (50, 180, 50), (cx, cy-12, 8, 10))    # Leaf
        pygame.draw.ellipse(s, (50, 200, 50), (cx-4, cy-16, 8, 8))   # Top leaf
        
        # Pot
        pygame.draw.polygon(s, (180, 100, 50), [(cx-6, cy+3), (cx+6, cy+3), (cx+4, cy+10), (cx-4, cy+10)])
        
        return cls._add_label(s, "GREEN", size)
    
    @classmethod
    def design_thinking_huddle(cls, size=64):
        """Light bulb with brainstorming nodes"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['innovation']
        cx, cy = size//2, size//2 - 8
        
        # Light bulb
        pygame.draw.circle(s, color, (cx, cy-4), 12)
        pygame.draw.rect(s, (200, 200, 200), (cx-5, cy+8, 10, 8), border_radius=2)
        
        # Rays
        for angle in range(0, 360, 45):
            if angle != 180:  # Skip bottom
                rad = math.radians(angle)
                x1, y1 = cx + 14 * math.cos(rad), cy - 4 + 14 * math.sin(rad)
                x2, y2 = cx + 20 * math.cos(rad), cy - 4 + 20 * math.sin(rad)
                pygame.draw.line(s, color, (x1, y1), (x2, y2), 2)
        
        return cls._add_label(s, "DTH", size)
    
    @classmethod
    def kriyakalpa(cls, size=64):
        """Innovation hub - tools + bulb"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['innovation']
        cx, cy = size//2, size//2 - 8
        
        # Gear
        pygame.draw.circle(s, (150, 150, 150), (cx-8, cy+4), 10, 2)
        pygame.draw.circle(s, (150, 150, 150), (cx-8, cy+4), 4)
        
        # Bulb
        pygame.draw.circle(s, color, (cx+8, cy-4), 8)
        pygame.draw.rect(s, (200, 200, 200), (cx+5, cy+4, 6, 5), border_radius=1)
        
        # Sparkles
        pygame.draw.line(s, (255, 255, 255), (cx+8, cy-14), (cx+8, cy-18), 2)
        pygame.draw.line(s, (255, 255, 255), (cx+16, cy-8), (cx+20, cy-8), 2)
        
        return cls._add_label(s, "KRIYA", size)
    
    @classmethod
    def ise_aerospace_dept(cls, size=64):
        """Rocket / satellite"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['science']
        cx, cy = size//2, size//2 - 8
        
        # Rocket body
        pygame.draw.ellipse(s, (200, 200, 220), (cx-6, cy-18, 12, 30))
        
        # Nose cone
        pygame.draw.polygon(s, (255, 100, 100), [(cx, cy-22), (cx-5, cy-14), (cx+5, cy-14)])
        
        # Fins
        pygame.draw.polygon(s, (255, 100, 100), [(cx-6, cy+6), (cx-12, cy+14), (cx-4, cy+10)])
        pygame.draw.polygon(s, (255, 100, 100), [(cx+6, cy+6), (cx+12, cy+14), (cx+4, cy+10)])
        
        # Window
        pygame.draw.circle(s, (100, 200, 255), (cx, cy-6), 4)
        
        # Flame
        pygame.draw.polygon(s, (255, 200, 0), [(cx-4, cy+12), (cx, cy+20), (cx+4, cy+12)])
        
        return cls._add_label(s, "ISE-AERO", size)
    
    @classmethod
    def thode_aur_canteen(cls, size=64):
        """Plate with spoon"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['food']
        cx, cy = size//2, size//2 - 8
        
        # Plate
        pygame.draw.ellipse(s, (240, 240, 240), (cx-16, cy-6, 32, 18))
        pygame.draw.ellipse(s, (220, 220, 220), (cx-12, cy-2, 24, 12))
        
        # Food items
        pygame.draw.circle(s, (200, 150, 100), (cx-4, cy+2), 5)
        pygame.draw.circle(s, (100, 180, 100), (cx+6, cy+2), 4)
        
        # Spoon
        pygame.draw.ellipse(s, (180, 180, 180), (cx+14, cy-8, 6, 10))
        pygame.draw.rect(s, (180, 180, 180), (cx+15, cy, 3, 12))
        
        return cls._add_label(s, "THODE", size)
    
    @classmethod
    def mingos_canteen(cls, size=64):
        """Coffee cup"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['food']
        cx, cy = size//2, size//2 - 8
        
        # Cup
        pygame.draw.rect(s, (255, 255, 255), (cx-10, cy-6, 20, 22), border_radius=3)
        pygame.draw.arc(s, (200, 200, 200), (cx+8, cy, 12, 14), -1.5, 1.5, 3)
        
        # Coffee fill
        pygame.draw.rect(s, (139, 90, 43), (cx-8, cy-2, 16, 16), border_radius=2)
        
        # Steam
        for i in range(3):
            pygame.draw.arc(s, (200, 200, 200), (cx-6+i*6, cy-16, 8, 10), 0.5, 2.6, 2)
        
        return cls._add_label(s, "MINGOS", size)
    
    @classmethod
    def canteen(cls, size=64):
        """General canteen - plate + utensils"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['food']
        cx, cy = size//2, size//2 - 8
        
        # Plate
        pygame.draw.ellipse(s, color, (cx-14, cy-4, 28, 16))
        pygame.draw.ellipse(s, (255, 200, 150), (cx-10, cy, 20, 10))
        
        # Fork
        pygame.draw.rect(s, (200, 200, 200), (cx-18, cy-10, 2, 16))
        for i in range(3):
            pygame.draw.rect(s, (200, 200, 200), (cx-20+i*2, cy-14, 2, 6))
        
        # Knife
        pygame.draw.rect(s, (200, 200, 200), (cx+16, cy-10, 2, 16))
        pygame.draw.polygon(s, (200, 200, 200), [(cx+16, cy-14), (cx+18, cy-14), (cx+17, cy-10)])
        
        return cls._add_label(s, "CANTEEN", size)
    
    @classmethod
    def football_cricket_ground(cls, size=64):
        """Ball / field outline"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['sports']
        cx, cy = size//2, size//2 - 8
        
        # Field
        pygame.draw.ellipse(s, (80, 160, 80), (cx-20, cy-10, 40, 24))
        pygame.draw.ellipse(s, (100, 180, 100), (cx-20, cy-10, 40, 24), 2)
        
        # Cricket stumps
        for i in range(-4, 5, 4):
            pygame.draw.rect(s, (200, 180, 150), (cx+i-1, cy-8, 2, 12))
        
        # Football
        pygame.draw.circle(s, (255, 255, 255), (cx-10, cy+4), 6)
        pygame.draw.circle(s, (50, 50, 50), (cx-10, cy+4), 6, 1)
        
        return cls._add_label(s, "SPORTS", size)
    
    @classmethod
    def pe_sports_dept(cls, size=64):
        """Dumbbell"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['sports']
        cx, cy = size//2, size//2 - 8
        
        # Dumbbell bar
        pygame.draw.rect(s, (150, 150, 150), (cx-18, cy-2, 36, 4))
        
        # Weights
        pygame.draw.rect(s, (80, 80, 80), (cx-20, cy-10, 8, 20), border_radius=2)
        pygame.draw.rect(s, (80, 80, 80), (cx+12, cy-10, 8, 20), border_radius=2)
        pygame.draw.rect(s, (60, 60, 60), (cx-24, cy-8, 6, 16), border_radius=2)
        pygame.draw.rect(s, (60, 60, 60), (cx+18, cy-8, 6, 16), border_radius=2)
        
        return cls._add_label(s, "PE SPORTS", size)
    
    @classmethod
    def krishna_hostel(cls, size=64):
        """Bed / dorm building"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['hostel']
        cx, cy = size//2, size//2 - 8
        
        # Building
        pygame.draw.rect(s, color, (cx-16, cy-10, 32, 28), border_radius=2)
        
        # Windows (arranged like rooms)
        for row in range(2):
            for col in range(3):
                pygame.draw.rect(s, (255, 255, 200), (cx-12+col*10, cy-6+row*12, 6, 8))
        
        # Door
        pygame.draw.rect(s, (100, 70, 150), (cx-3, cy+10, 6, 8))
        
        return cls._add_label(s, "KRISHNA", size)
    
    @classmethod
    def cauvery_boys_hostel(cls, size=64):
        """Bunk beds / residence block"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['hostel']
        cx, cy = size//2, size//2 - 8
        
        # Building - slightly different style
        pygame.draw.rect(s, color, (cx-18, cy-12, 36, 30), border_radius=2)
        
        # Bunk bed icon in center
        pygame.draw.rect(s, (200, 180, 220), (cx-8, cy-8, 16, 4))   # Top bunk
        pygame.draw.rect(s, (200, 180, 220), (cx-8, cy+4, 16, 4))   # Bottom bunk
        pygame.draw.rect(s, (150, 130, 180), (cx-10, cy-8, 2, 16))  # Left post
        pygame.draw.rect(s, (150, 130, 180), (cx+8, cy-8, 2, 16))   # Right post
        
        return cls._add_label(s, "CAUVERY", size)
    
    @classmethod
    def rv_university(cls, size=64):
        """Graduation cap / university building"""
        s = cls._create_base_surface(size)
        color = cls.COLORS['admin']
        cx, cy = size//2, size//2 - 8
        
        # Building with columns
        pygame.draw.rect(s, (200, 200, 200), (cx-16, cy-4, 32, 22))
        
        # Columns
        for i in [-10, 0, 10]:
            pygame.draw.rect(s, (180, 180, 180), (cx+i-2, cy-2, 4, 18))
        
        # Roof/pediment
        pygame.draw.polygon(s, color, [(cx-18, cy-4), (cx, cy-16), (cx+18, cy-4)])
        
        # Graduation cap on top
        pygame.draw.rect(s, (50, 50, 50), (cx-8, cy-20, 16, 4))
        pygame.draw.polygon(s, (50, 50, 50), [(cx, cy-24), (cx-10, cy-20), (cx+10, cy-20)])
        
        return cls._add_label(s, "RV UNIV", size)
    
    @classmethod
    def get_icon(cls, building_name, size=64):
        """Get icon for a specific building by name"""
        # Map building names to icon methods
        icon_map = {
            "Main Entrance": cls.main_entrance,
            "Kotak Mahindra Bank": cls.kotak_mahindra_bank,
            "Health Centre": cls.health_centre,
            "Admin Block": cls.admin_block,
            "IEM Auditorium": cls.iem_auditorium,
            "Library": cls.library,
            "Temple": cls.temple,
            "Mechanical Dept": cls.mechanical_dept,
            "Civil Dept": cls.civil_dept,
            "Chem Engg & Physics Dept": cls.chem_engg_physics_dept,
            "EEE Dept": cls.eee_dept,
            "ECE Dept": cls.ece_dept,
            "CSE Dept": cls.cse_dept,
            "Telecom Dept": cls.telecom_dept,
            "Mathematics Dept": cls.mathematics_dept,
            "Biotech Quadrangle": cls.biotech_quadrangle,
            "Green House": cls.green_house,
            "Design Thinking Huddle": cls.design_thinking_huddle,
            "Kriyakalpa": cls.kriyakalpa,
            "ISE & Aerospace Dept": cls.ise_aerospace_dept,
            "Thode Aur Canteen": cls.thode_aur_canteen,
            "Mingos Canteen": cls.mingos_canteen,
            "Canteen": cls.canteen,
            "Football & Cricket Ground": cls.football_cricket_ground,
            "PE & Sports Dept": cls.pe_sports_dept,
            "Krishna Hostel": cls.krishna_hostel,
            "Cauvery Boys Hostel": cls.cauvery_boys_hostel,
            "RV University": cls.rv_university,
        }
        
        if building_name in icon_map:
            return icon_map[building_name](size)
        else:
            # Default icon
            return cls._create_default_icon(building_name, size)
    
    @classmethod
    def _create_default_icon(cls, name, size=64):
        """Create a default icon for unknown buildings"""
        s = cls._create_base_surface(size)
        cx, cy = size//2, size//2 - 8
        
        # Generic building
        pygame.draw.rect(s, (100, 100, 100), (cx-14, cy-10, 28, 26), border_radius=2)
        pygame.draw.rect(s, (150, 150, 200), (cx-10, cy-6, 20, 18))
        
        # Short name
        short_name = name[:6] if len(name) > 6 else name
        return cls._add_label(s, short_name.upper(), size)

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
        # Fullscreen mode - get actual display size
        display_info = pygame.display.Info()
        self.screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.PANEL_RATIO = 0.30
        self.panel_width = int(self.screen_width * self.PANEL_RATIO)
        self.map_width = self.screen_width - self.panel_width
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
            'easy': {
                'time': 420,
                'tasks': 5,
                'name': 'Easy',
                'hint_cost': 10,
                'rain_chance': 0.0,
                'npc_alert_radius': 2
            },
            'normal': {
                'time': 180,
                'tasks': 7,
                'name': 'Normal',
                'hint_cost': 15,
                'rain_chance': 0.15,
                'npc_alert_radius': 3
            },
            'hard': {
                'time': 100,
                'tasks': 7,
                'name': 'Hard',
                'hint_cost': 25,
                'rain_chance': 0.35,
                'npc_alert_radius': 4
            }
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
        self.max_time=1
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
        
        # Hint system
        self.hint_used = False  # Track if hint was used for current task
        # Hint cost is fixed at 15 points regardless of difficulty
        self.hint_cost = 15
        self.show_hint = False  # Whether hint is currently shown
        
        # Star shimmer effect (when gaining points)
        self.star_shimmer = 0  # Shimmer intensity (0-1, decays over time)
        self.last_score = 0  # To detect score changes
        
        # Level progression system (Runner Titles)
        self.current_level = 0  # Start as Fresher
        self.level_thresholds = {
            0: 0,      # Fresher: 0-249 points
            1: 250,    # Sophomore: 250-599 points
            2: 600,    # Senior: 600-799 points
            3: 800     # Super Senior: 800+ points
        }
        self.level_names = {0: "Fresher", 1: "Sophomore", 2: "Senior", 3: "Super Senior"}
        
        # Pathfinding usage tracking (for independent discovery bonus)
        self.used_pathfinding = False  # Did player use B/A keys for current task?
        self.independent_bonus = 20  # Bonus for finding shortest path without B/A
        
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
        
    def wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current = ""

        for word in words:
            test = current + word + " "
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current.strip())
                current = word + " "

        if current:
            lines.append(current.strip())

        return lines

        
    def load_assets(self):
        """Generate all visual assets programmatically"""
        print("Generating game assets...")
        
        # Building icons - using new custom BuildingIconGenerator
        self.building_icons = {
            name: BuildingIconGenerator.get_icon(name, 64)
            for name in [
                "Main Entrance", "Kotak Mahindra Bank", "Football & Cricket Ground",
                "Design Thinking Huddle", "Mechanical Dept", "Biotech Quadrangle", "Green House",
                "Admin Block", "IEM Auditorium", "RV University", "Chem Engg & Physics Dept",
                "Civil Dept", "Kriyakalpa", "Thode Aur Canteen", "Telecom Dept",
                "EEE Dept", "ECE Dept", "Mingos Canteen",
                "PE & Sports Dept", "CSE Dept", "Health Centre", "Temple",
                "Krishna Hostel", "Cauvery Boys Hostel", "Mathematics Dept",
                "Canteen", "Library", "ISE & Aerospace Dept"
            ]
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
        self.game_map = RVCEGameMap(40, 36)
        self.nav_graph = RVCEGraph()
        self.undo_stack = UndoStack()
        self.task_manager = TaskManager()
        # Calculate cell size - increased for more zoom/larger nodes
        map_area_width = self.map_width
        map_area_height = self.screen_height - 100
        base_cell_size = min(map_area_width // 40, map_area_height // 36)
        self.game_map.cell_size = int(base_cell_size * 1.5)  # 50% larger for spacious feel
        # Game state - use difficulty settings
        self.hint_cost = self.difficulty_settings[self.difficulty]['hint_cost']
        self.state = GameState.PLAYING
        self.player_pos = (9, 1)  # Start at Main Entrance
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
        
        # Grid display toggle (G key) - off by default
        self.show_grid = False
        
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
        self.camera = Camera(self.map_width, self.screen_height)

        # Snap camera immediately to player position
        player_world_x = self.player_pos[0] * self.game_map.cell_size + self.game_map.cell_size / 2
        player_world_y = self.player_pos[1] * self.game_map.cell_size + self.game_map.cell_size / 2
        self.camera.snap_to((player_world_x, player_world_y))
        
        # Initialize fog of war
        self.fog_of_war = FogOfWar(self.game_map.width, self.game_map.height)
        self.fog_of_war.update(self.player_pos)
        
        # Initialize event manager - DISABLED per user request
        # self.event_manager = EventManager()
        # self.event_manager.set_available_positions(self.game_map, self.tile_map)
        
        # Initialize NPC manager - professors and students for hints
        self.npc_manager = NPCManager()
        self.npc_manager.spawn_npcs(self.game_map, self.buildings)
        
        # Set NPC detection range for hint proximity (4-5 nodes)
        self.npc_hint_range = 5  # Player can ask for hint when NPC is within 5 nodes
        for npc in self.npc_manager.npcs:
            npc.detection_range = self.npc_hint_range
        
        # Track if NPC is nearby for hint notification
        self.nearby_npc = None
        
        # Construction event system - random road blocks
        self.construction_sites = []  # List of (x, y, timer) tuples
        self.construction_duration = 45  # Seconds each construction lasts
        self.construction_spawn_timer = 15  # Time until first spawn
        self.construction_spawn_interval = (30, 60)  # Random interval between spawns

        
        # Initialize mini-map (position in bottom-left corner)
        self.mini_map = MiniMap(20, self.screen_height - 170, 150)
        
        # Setup tasks
        self.setup_academic_tasks()
        # --- INITIAL EXPECTED PATH (FIRST TASK) ---
        if self.task_manager.current_task:
            target = self.buildings.get(self.task_manager.current_task['building'])
            if target:
                expected_path = self.find_path_bfs(self.player_pos, target)
                self.expected_path_length = len(expected_path)
                self.task_start_pos = self.player_pos

        # Trigger rain probabilistically based on difficulty - DISABLED
        # rain_chance = self.difficulty_settings[self.difficulty]['rain_chance']
        # if self.event_manager and random.random() < rain_chance:
        #     self.event_manager.schedule_event(
        #         RainEvent(duration=20 + int(20 * rain_chance))
        #     )

        
    def setup_rvce_campus(self):
        """
        High-resolution RVCE campus map (40x36)
        Geometry & distances derived from reference image
        Roads ONLY where image shows roads
        """
    
        W, H = 40, 36
        grid = [[1 for _ in range(W)] for _ in range(H)]
    
        def road(x1, y1, x2, y2):
            for y in range(y1, y2):
                for x in range(x1, x2):
                    grid[y][x] = 0
    
        # ================= MYSORE ROAD (TOP) =================
        road(0, 2, 40, 4)
    
        # ================= MAIN VERTICAL AXIS =================
        road(18, 4, 22, 30)
    
        # ================= PARKING ACCESS =================
        road(10, 4, 30, 6)
    
        # ================= ADMIN LOOP =================
        road(8, 8, 32, 10)
        road(8, 10, 10, 18)
        road(30, 10, 32, 18)
    
        # ================= CENTRAL ACADEMIC STRIP =================
        road(6, 14, 34, 18)  # Extended to y=18 to include IEM Auditorium at y=16
    
        # ================= EEE / ECE =================
        road(22, 16, 26, 26)  # Extended width
    
        # ================= LIBRARY ACCESS =================
        road(10, 26, 32, 30)  # Extended to reach more buildings
    
        # ================= HOSTEL ROAD =================
        road(30, 16, 38, 34)  # Start from y=16 to connect earlier
        
        # ================= ADMIN CORE VERTICAL (x=14) =================
        road(12, 10, 16, 26)  # Vertical road connecting Admin, IEM, RV Univ, Chem Dept
        
        # ================= CENTRAL STRIP VERTICAL (x=20) =================
        road(18, 14, 22, 26)  # Vertical connecting Kriyakalpa, Thode, Telecom
        
        # ================= LEFT VERTICAL PATH (DTH -> Mech -> BT-Q -> Green House -> Canteen) =================
        road(2, 8, 8, 28)  # Wider vertical path from DTH to Canteen area
        
        # ================= HORIZONTAL PATH TO CANTEEN =================
        road(2, 26, 22, 30)  # Connect left vertical to library access road
        
        # ================= PATH TO ISE-A =================
        road(24, 28, 30, 34)  # Connect library area to ISE-A at (26, 30)
        
        # ================= ENSURE ALL BUILDING POSITIONS ARE WALKABLE =================
        # Explicitly make each building cell walkable (value 0)
        building_positions = [
            (20, 3), (24, 3), (34, 5),           # Main Entrance, Bank, Sports Ground
            (4, 9), (4, 13), (4, 17), (4, 21),   # Left Academic
            (14, 12), (14, 16), (14, 20), (14, 24),  # Admin Core
            (22, 12), (20, 16), (20, 20), (20, 24),  # Central Strip - Civil, Kriyakalpa, Thode, Telecom
            (24, 16), (24, 20), (26, 24),        # EEE, ECE, Mingos
            (32, 12), (32, 16), (32, 20), (34, 20),  # PE Sports, CSE, Health, Temple
            (32, 24), (32, 28), (26, 30), (32, 32),  # Hostels
            (10, 27), (20, 28),                   # Canteen, Library
        ]
        for pos in building_positions:
            x, y = pos
            if 0 <= y < 36 and 0 <= x < 40:
                grid[y][x] = 0
                # Also make adjacent cells walkable (connectors to road)
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= ny < 36 and 0 <= nx < 40:
                        grid[ny][nx] = 0
    
        self.game_map.load_rvce_map(grid)
    
        # ================= BUILDINGS (SCALED POSITIONS) =================
        self.buildings = {
            # Top
            "Main Entrance": (20, 3),
            "Kotak Mahindra Bank": (24, 3),
            "Football & Cricket Ground": (34, 5),
    
            # Left Academic Block
            "Design Thinking Huddle": (4, 9),
            "Mechanical Dept": (4, 13),
            "Biotech Quadrangle": (4, 17),
            "Green House": (4, 21),
    
            # Admin Core
            "Admin Block": (14, 12),
            "IEM Auditorium": (14, 16),
            "RV University": (14, 20),
            "Chem Engg & Physics Dept": (14, 24),
    
            # Central Strip
            "Civil Dept": (22, 12),
            "Kriyakalpa": (20, 16),
            "Thode Aur Canteen": (20, 20),
            "Telecom Dept": (20, 24),
    
            # EEE / ECE
            "EEE Dept": (24, 16),
            "ECE Dept": (24, 20),
            "Mingos Canteen": (26, 24),
    
            # Right
            "PE & Sports Dept": (32, 12),
            "CSE Dept": (32, 16),
            "Health Centre": (32, 20),
            "Temple": (34, 20),
    
            # Hostels
            "Krishna Hostel": (32, 24),
            "Cauvery Boys Hostel": (32, 28),
            "ISE & Aerospace Dept": (26, 30),  # Between CBH and Library
            "Mathematics Dept": (32, 32),
    
            # Bottom - Canteen below Chem, left of Library
            "Canteen": (10, 27),
            "Library": (20, 28),
        }

    def setup_special_tiles(self):
        """Setup special tile types - currently disabled"""
        # All special tiles removed as per user request
        pass

    RIDDLE_BANK = {
        "Main Entrance": {
            "easy": [
                "Where journeys begin and farewells are made,\nThis threshold marks transitions in every parade.",
                "All roads lead here, at least within these walls,\nThe first step of every adventure that calls."
            ],
            "normal": [
                "Neither inside nor outside, this space exists between,\nA liminal threshold where all students convene.",
                "The first impression and the last goodbye,\nWhere campus meets the world under open sky."
            ],
            "hard": [
                "A symbolic boundary between academic and mundane,\nWhere the pursuit of knowledge first stakes its claim."
            ]
        },

        "Kotak Mahindra Bank": {
            "easy": [
                "Numbers unlock resources here.",
                "Trust flows digitally through secure machines."
            ],
            "normal": [
                "A portal to commerce, to need and to lease,\nWhere stored value finds its local release."
            ],
            "hard": [
                "It renders the abstract of credit and save,\nInto tangible notes from its metallic cave."
            ]
        },

        "Football & Cricket Ground": {
            "easy": [
                "Where leather meets willow and goals are scored,\nThis open field is where champions are forged.",
                "Cheers echo here when victory is near,\nThe playground of athletes throughout the year."
            ],
            "normal": [
                "Boundaries and goalposts define this space,\nWhere friendly rivalry finds its place.",
                "Green grass and white lines mark the field of play,\nWhere students compete at the end of each day."
            ],
            "hard": [
                "An arena of physical prowess and sport,\nWhere academic minds find their athletic court."
            ]
        },

        "Design Thinking Huddle": {
            "easy": [
                "Creativity blooms in this space of thought,\nWhere innovative solutions are carefully wrought.",
                "Ideas flow freely without constraint,\nWhere thinking outside the box has no restraint."
            ],
            "normal": [
                "Brainstorming sessions fill these walls,\nWhere imagination answers the problem's calls."
            ],
            "hard": [
                "A laboratory for structured creativity,\nWhere design meets purpose with intentional activity."
            ]
        },

        "Mechanical Dept": {
            "easy": [
                "Gears and engines are studied here,\nWhere motion and force become crystal clear.",
                "Machines obey laws taught in this space,\nWhere physics meets engineering face to face."
            ],
            "normal": [
                "Heat, force, and motion share equal importance,\nNothing moves without reason in this domain of performance."
            ],
            "hard": [
                "The discipline tasked with the willing command,\nOf energies hidden in fuel and in land."
            ]
        },

        "Biotech Quadrangle": {
            "easy": [
                "Open to the sky, surrounded by study,\nWhere discussions spill outside when rooms get muddy.",
                "A pause between theory sessions, yet still academic,\nLearning continues even without lectures endemic."
            ],
            "normal": [
                "More than a pathway, it's an extended class,\nWhere students on benches watch the world pass."
            ],
            "hard": [
                "A designed void that creates connection,\nWhere biology students find reflection."
            ]
        },

        "Green House": {
            "easy": [
                "Plants grow here under careful watch,\nWhere nature and science make the perfect match.",
                "Glass walls let sunlight in to stay,\nWhere seedlings become plants day by day."
            ],
            "normal": [
                "A controlled environment for growth and study,\nWhere chlorophyll and research become study buddies."
            ],
            "hard": [
                "An enclosed ecosystem of botanical research,\nWhere the secrets of photosynthesis wait to emerge."
            ]
        },

        "Admin Block": {
            "easy": [
                "No lectures echo here, yet decisions linger,\nForms move faster than any student's finger.",
                "Authority does not shout here, it stamps."
            ],
            "normal": [
                "Students arrive uncertain, leave with instructions,\nRules sleep inside files awaiting reproductions."
            ],
            "hard": [
                "A nexus of governance, subdued and austere,\nWhere policy hardens from idea to clear."
            ]
        },

        "IEM Auditorium": {
            "easy": [
                "Voices carry here across rows of seats,\nWhere speakers and listeners in ceremony meet.",
                "The stage awaits performers and orators alike,\nWhere presentations receive both praise and strike."
            ],
            "normal": [
                "Acoustics designed for the spoken word,\nWhere every announcement is clearly heard."
            ],
            "hard": [
                "A theater of academic discourse and display,\nWhere knowledge is performed in a structured way."
            ]
        },

        "RV University": {
            "easy": [
                "Another academic presence shares the landscape.",
                "Parallel learning paths exist, close at hand."
            ],
            "normal": [
                "Institutions coexist, knowledge overlaps,\nAcross invisible borders where students perhaps."
            ],
            "hard": [
                "A contiguous, yet distinct ecosystem of mind,\nWith its own rhythms and ties that bind."
            ]
        },

        "Chem Engg & Physics Dept": {
            "easy": [
                "Molecules and forces are studied here,\nWhere atoms and equations become crystal clear.",
                "Test tubes and equations share space,\nWhere matter and energy find their place."
            ],
            "normal": [
                "A shared home for chemical and physical decrees,\nWhere experiments unlock nature's mysteries."
            ],
            "hard": [
                "The foundational inquiry into matter and state,\nDecoding the universe, piece by piece, to illuminate fate."
            ]
        },

        "Civil Dept": {
            "easy": [
                "Buildings and bridges are planned in this space,\nWhere structural integrity finds its place.",
                "Concrete and steel are subjects of study,\nWhere construction meets theory, never muddy."
            ],
            "normal": [
                "Gravity is respected here, not challenged,\nDesign bows to physics, carefully balanced."
            ],
            "hard": [
                "The art of predicting what time will degrade,\nAnd designing defenses that will never fade."
            ]
        },

        "Kriyakalpa": {
            "easy": [
                "Innovation finds a home in this space,\nWhere creativity meets technology face to face.",
                "Projects take shape from concept to creation,\nA hub of inventive experimentation."
            ],
            "normal": [
                "Ideas are nurtured from seed to solution,\nWhere problems meet creative resolution."
            ],
            "hard": [
                "A crucible of applied creativity,\nWhere abstractions find their utility."
            ]
        },

        "Thode Aur Canteen": {
            "easy": [
                "Hunger interrupts focus, this place restores it,\nWhere empty stomachs find their spirit.",
                "Energy levels get topped up with speed,\nA practical solution for every student's need."
            ],
            "normal": [
                "Students arrive with brain-weary sighs,\nLeave with satisfied glints in their eyes."
            ],
            "hard": [
                "The metabolic pit-stop in the race of the mind,\nAn external solution to internal fatigue mankind."
            ]
        },

        "Telecom Dept": {
            "easy": [
                "Signals and waves are studied here,\nWhere communication technology becomes clear.",
                "From radio to fiber, transmission is key,\nUnlocking the secrets of connectivity."
            ],
            "normal": [
                "Distance is the enemy, distortion the thief,\nThey are the senders of tonal relief."
            ],
            "hard": [
                "The art of the vessel, the craft of the vein,\nThrough which modern society's thoughts must remain."
            ]
        },

        "EEE Dept": {
            "easy": [
                "Power and circuits are mastered here,\nWhere voltage and current become crystal clear.",
                "They speak the language of volts and phase,\nLighting our world in a controlled blaze."
            ],
            "normal": [
                "Fields, currents, and systems shape modern life,\nWhere electrons flow without any strife."
            ],
            "hard": [
                "The taming of lightning, the bending of fields,\nTo the service that modern existence yields."
            ]
        },

        "ECE Dept": {
            "easy": [
                "Signals whisper through wires here,\nInvisible yet precise, crystal clear.",
                "Communication begins with understanding waves,\nFrom microchips to the data that saves."
            ],
            "normal": [
                "Information survives noise through discipline,\nClarity is engineered, not left to whim."
            ],
            "hard": [
                "The guardians of signal integrity's flame,\nIn a universe eager to scatter the same."
            ]
        },

        "Mingos Canteen": {
            "easy": [
                "A popular spot when hunger calls,\nWhere students gather in crowded halls.",
                "Snacks and meals to fuel the day,\nA break from books along the way."
            ],
            "normal": [
                "The unofficial meeting place of the campus crowd,\nWhere laughter and chatter are always loud."
            ],
            "hard": [
                "A commercial crossroads of sustenance and social,\nWhere academic discourse becomes less formal."
            ]
        },

        "PE & Sports Dept": {
            "easy": [
                "Physical education finds its home here,\nWhere fitness and health are held dear.",
                "Sports equipment and training abound,\nWhere healthy bodies are always found."
            ],
            "normal": [
                "The body is trained as much as the mind,\nLeaving sedentary habits behind."
            ],
            "hard": [
                "A temple to physical excellence and form,\nWhere discipline of the body becomes the norm."
            ]
        },

        "CSE Dept": {
            "easy": [
                "Code is written and programs run,\nWhere computer science work is done.",
                "Algorithms and data structures fill the air,\nLogical thinking beyond compare."
            ],
            "normal": [
                "Abstractions take form here, from vague to concrete,\nAs symbols and functions find purchase complete."
            ],
            "hard": [
                "Modern-day sorcery where meaning is caught,\nIn strings of pure symbol, in patterns of thought."
            ]
        },

        "Health Centre": {
            "easy": [
                "When wellness falters, help is near,\nMedical care waits right here.",
                "First aid and checkups on campus grounds,\nWhere healing and health abounds."
            ],
            "normal": [
                "A sanctuary of care within academic walls,\nWhere the body's needs answer its calls."
            ],
            "hard": [
                "The institutional response to corporeal need,\nWhere students find relief with haste and speed."
            ]
        },

        "Temple": {
            "easy": [
                "A quiet space for reflection and prayer,\nWhere spiritual peace fills the air.",
                "Faith finds expression in this sacred space,\nA moment of calm in the academic race."
            ],
            "normal": [
                "Beyond curricula, the soul finds rest,\nIn this sanctuary considered blessed."
            ],
            "hard": [
                "A designated space for transcendent pursuit,\nWhere the material and spiritual commute."
            ]
        },

        "Krishna Hostel": {
            "easy": [
                "Where students rest when classes end,\nA home away from home, around the bend.",
                "Bunk beds and study lamps line the halls,\nResidence life within these walls."
            ],
            "normal": [
                "Shared living defines the routine here,\nPrivacy negotiated, community clear."
            ],
            "hard": [
                "The residential substrate of academic life,\nWhere one processes intellectual strife."
            ]
        },

        "Cauvery Boys Hostel": {
            "easy": [
                "Another home for students staying on campus,\nWhere daily routines develop their compass.",
                "Friends are made in common rooms,\nAs academic life around them blooms."
            ],
            "normal": [
                "Community living with structured routine,\nWhere independence meets supported scene."
            ],
            "hard": [
                "An institutional dwelling for the scholarly traveler,\nWhere the chaos of youth finds its leveler."
            ]
        },

        "Mathematics Dept": {
            "easy": [
                "Numbers and proofs are pondered here,\nWhere theorems and equations become clear.",
                "Abstract thinking reaches new heights,\nIn the pursuit of mathematical insights."
            ],
            "normal": [
                "Pure logic distilled to elegant form,\nWhere patterns and proofs are the norm."
            ],
            "hard": [
                "The language of the universe decoded and taught,\nWhere abstract beauty is carefully wrought."
            ]
        },

        "Canteen": {
            "easy": [
                "Hunger drives students to this central spot,\nWhere food and friends are always sought.",
                "Between classes, this is where you go,\nTo refuel and let your energy flow."
            ],
            "normal": [
                "The unofficial meeting place of campus life,\nWhere hunger meets relief from strife."
            ],
            "hard": [
                "A communal crossroads of sustenance and social,\nWhere academic discourse becomes less formal."
            ]
        },

        "Library": {
            "easy": [
                "Silence amplifies learning here,\nKnowledge waits on shelves, crystal clear.",
                "Books and journals line the walls,\nWhere focused study answers its calls."
            ],
            "normal": [
                "Information organized across time,\nCaptured and ordered in logical rhyme."
            ],
            "hard": [
                "A disciplined archive of accumulated thought,\nWhere solitude and collected wisdom are sought."
            ]
        },

        "ISE & Aerospace Dept": {
            "easy": [
                "Systems and software meet in this place,\nWhere engineering takes to space.",
                "Information systems and flying machines,\nStudied together in innovative scenes."
            ],
            "normal": [
                "Complex systems are analyzed and designed,\nWhere software and hardware are intertwined."
            ],
            "hard": [
                "The foresight engineering of systems that fly,\nWhere meticulous planning reaches for the sky."
            ]
        }
    }
    def setup_academic_tasks(self):
        task_id = 1

        max_tasks = self.difficulty_settings[self.difficulty]['tasks']
        for building in random.sample(list(self.buildings.keys()), max_tasks):
            if building not in self.RIDDLE_BANK:
                continue  # safety

            task = {
                "id": f"task{task_id}",
                "name": f"Visit {building}",
                "building": building,
                "riddle": random.choice(self.RIDDLE_BANK[building].get(self.difficulty,[])),
                "points": random.randint(50, 120),
                "hint": f"Explore the area related to {building}"
            }

            self.task_manager.add_task(task["id"], task)
            task_id += 1

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
                    # Skip construction tiles (dynamic obstacles)
                    nx, ny = neighbor
                    if self.tile_map and 0 <= ny < len(self.tile_map) and 0 <= nx < len(self.tile_map[0]):
                        if self.tile_map[ny][nx] == TileType.CONSTRUCTION:
                            continue
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
                
                # ========== NEW SCORING SYSTEM ==========
                # Base: 50 points for reaching building
                base_points = 50
                score_message = f"+{base_points} base"
                total_points = base_points
                
                # Bonus +20: Did NOT use B or A keys (pathfinding)
                no_pathfinding_bonus = 0
                if not self.used_pathfinding:
                    no_pathfinding_bonus = 20
                    total_points += no_pathfinding_bonus
                    score_message += f" +{no_pathfinding_bonus} (no pathfinding)"
                    
                    # Bonus +30: Reached via optimal path (requires no pathfinding)
                    if self.expected_path_length > 0 and self.task_steps <= self.expected_path_length:
                        optimal_bonus = 30
                        total_points += optimal_bonus
                        score_message += f" +{optimal_bonus} OPTIMAL PATH!"
                        if self.sound_manager:
                            self.sound_manager.play('victory')
                
                self.score += total_points
                
                print(f"✓ Task Completed: {current_task['name']} ({score_message})")
                print(f"   Path: {self.task_steps} steps vs {self.expected_path_length} expected (BFS optimal)")
                
                if self.sound_manager:
                    self.sound_manager.play('task_complete')
                
                # Check for level up (new titles: Fresher, Sophomore, Senior, Super Senior)
                old_level = self.current_level
                for level in [3, 2, 1]:
                    if self.score >= self.level_thresholds[level]:
                        self.current_level = level
                        break
                if self.current_level > old_level:
                    self.ui_message = f"🎉 LEVEL UP! Now {self.level_names[self.current_level]}!"
                    self.ui_message_timer = 3.0
                    if self.sound_manager:
                        self.sound_manager.play('victory')
                
                self.task_manager.complete_task(current_task['id'])
                
                # Reset step counter, hint, and pathfinding flag for next task
                self.task_steps = 0
                self.hint_used = False
                self.show_hint = False
                self.used_pathfinding = False
                
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
                            self.used_pathfinding = True  # Track that player used pathfinding
                            print(f"✓ BFS Path: {len(self.current_path)} cells, {self.algorithm_stats['BFS']} nodes explored")
                    # A* search disabled - using BFS only
                    # elif event.key == pygame.K_a:
                    #     if self.task_manager.current_task:
                    #         target = self.buildings[self.task_manager.current_task['building']]
                    #         self.current_path = self.find_path_astar(self.player_pos, target)
                    #         self.path_algorithm = "A*"
                    #         self.used_pathfinding = True
                    #         print(f"✓ A* Path: {len(self.current_path)} cells, {self.algorithm_stats['A*']} nodes explored")
                    elif event.key == pygame.K_c:
                        self.current_path = []
                    elif event.key == pygame.K_g:
                        # Toggle grid display
                        self.show_grid = not self.show_grid
                        self.ui_message = f"Grid: {'ON' if self.show_grid else 'OFF'}"
                        self.ui_message_timer = 1.0
                    elif event.key == pygame.K_p:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_n:
                        next_task = self.task_manager.get_next_task()
                        if next_task:
                            self.task_manager.assign_task(next_task)
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
                    # H key to show/toggle hint - ONLY works when NPC is nearby
                    elif event.key == pygame.K_h:
                        if self.task_manager.current_task:
                            # Check if an NPC is nearby (within hint range)
                            if self.nearby_npc:
                                if not self.show_hint:
                                    # First time showing hint for this task
                                    if not self.hint_used:
                                        self.score = self.score - self.hint_cost  # Allow negative
                                        self.hint_used = True
                                        npc_label = self.nearby_npc.get_label()
                                        self.ui_message = f"{npc_label} gave you a hint! (-{self.hint_cost} pts)"
                                        self.ui_message_timer = 2.0
                                        if self.sound_manager:
                                            self.sound_manager.play('npc_talk')
                                    self.show_hint = True
                                else:
                                    self.show_hint = False
                            else:
                                # No NPC nearby - show message
                                self.ui_message = "Find a professor or student to ask for hints!"
                                self.ui_message_timer = 2.0
                                if self.sound_manager:
                                    self.sound_manager.play('alert')
                    
                    # L key to ask Lab Assistant for help clearing construction
                    elif event.key == pygame.K_l:
                        if self.construction_sites:  # Only if there's active construction
                            # Check if Lab Assistant is nearby
                            lab_assistant_nearby = None
                            for npc in self.npc_manager.npcs if self.npc_manager else []:
                                if npc.npc_type == NPCType.LAB_ASSISTANT:
                                    dx = self.player_pos[0] - npc.pos[0]
                                    dy = self.player_pos[1] - npc.pos[1]
                                    distance = (dx * dx + dy * dy) ** 0.5
                                    if distance <= self.npc_hint_range:
                                        lab_assistant_nearby = npc
                                        break
                            
                            if lab_assistant_nearby:
                                # Clear all construction sites
                                for x, y, timer in self.construction_sites:
                                    if 0 <= y < self.game_map.height and 0 <= x < self.game_map.width:
                                        self.tile_map[y][x] = TileType.NORMAL
                                        self.game_map.grid[y][x] = 0
                                self.construction_sites = []
                                self.score -= 5  # Deduct 5 points
                                self.ui_message = "Lab Assistant cleared the construction! (-5 pts)"
                                self.ui_message_timer = 3.0
                                if self.sound_manager:
                                    self.sound_manager.play('booster')
                            else:
                                self.ui_message = "Find a Lab Assistant (🧪) to help clear construction!"
                                self.ui_message_timer = 2.0
                        else:
                            self.ui_message = "No construction to clear right now."
                            self.ui_message_timer = 2.0
                
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
                    if self.sound_manager:
                        self.sound_manager.play('game_over')
        
        # Update animations
        self.animation_time = current_time / 1000.0
        self.pulse_offset = math.sin(self.animation_time * 3) * 3
        self.path_animation = (self.path_animation + 1) % 60
        
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Update star shimmer effect (detect score changes)
        if self.score != self.last_score:
            if self.score > self.last_score:
                self.star_shimmer = 1.0  # Full shimmer on score increase
            self.last_score = self.score
        else:
            # Decay shimmer over time
            self.star_shimmer = max(0, self.star_shimmer - dt * 2)
        
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
            # Use BFS for NPC pathfinding since A* is disabled
            self.npc_manager.update(dt, self.player_pos, self.game_map, self.find_path_bfs)
            
            # Check for nearby NPC within hint range (5 nodes for hint access)
            self.nearby_npc = None
            for npc in self.npc_manager.npcs:
                dx = self.player_pos[0] - npc.pos[0]
                dy = self.player_pos[1] - npc.pos[1]
                distance = (dx * dx + dy * dy) ** 0.5
                if distance <= self.npc_hint_range:
                    self.nearby_npc = npc
                    break
            
            # Show hint prompt when NPC is nearby
            if self.nearby_npc and not self.hint_used and self.ui_message is None:
                npc_label = self.nearby_npc.get_label()
                self.ui_message = f"{npc_label} nearby! Press [H] for hint (-15 pts)"
                self.ui_message_timer = 0.5
            elif self.ui_message and "Press [H]" in str(self.ui_message) and not self.nearby_npc:
                self.ui_message = None
        
        # Update construction events
        self._update_construction_events(dt)
    
    def _update_construction_events(self, dt):
        """Handle construction site spawning and removal"""
        # Update spawn timer
        self.construction_spawn_timer -= dt
        
        if self.construction_spawn_timer <= 0:
            # Spawn new construction site
            self._spawn_construction_site()
            # Reset timer with random interval
            self.construction_spawn_timer = random.uniform(*self.construction_spawn_interval)
        
        # Update existing construction timers and remove expired ones
        still_active = []
        for site in self.construction_sites:
            x, y, timer = site
            timer -= dt
            if timer > 0:
                still_active.append((x, y, timer))
            else:
                # Remove construction - make tile walkable again
                if 0 <= y < self.game_map.height and 0 <= x < self.game_map.width:
                    self.tile_map[y][x] = TileType.NORMAL
                    self.game_map.grid[y][x] = 0  # Mark as walkable
                self.ui_message = "🚧 Construction cleared!"
                self.ui_message_timer = 2.0
        self.construction_sites = still_active
    
    def _spawn_construction_site(self):
        """Spawn a new random construction site on a walkable path"""
        # Find all walkable positions (not buildings, not player position)
        walkable = []
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                if self.game_map.grid[y][x] == 0 and self.tile_map[y][x] == TileType.NORMAL:
                    # Don't block building positions
                    is_building = any(bpos == (x, y) for bpos in self.buildings.values())
                    is_player = (x, y) == self.player_pos
                    if not is_building and not is_player:
                        walkable.append((x, y))
        
        if not walkable:
            return
        
        # Pick 2-4 adjacent cells for the construction zone
        center = random.choice(walkable)
        cx, cy = center
        positions = [(cx, cy)]
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            if random.random() > 0.5:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in walkable and (nx, ny) not in positions:
                    positions.append((nx, ny))
                    if len(positions) >= 4:
                        break
        
        # Create construction sites
        for x, y in positions:
            self.tile_map[y][x] = TileType.CONSTRUCTION
            self.game_map.grid[y][x] = 1  # Mark as blocked
            self.construction_sites.append((x, y, self.construction_duration))
        
        self.ui_message = f"🚧 Construction ahead! Press B to reroute"
        self.ui_message_timer = 3.0
        
        # Clear current path so player must recalculate around obstacle
        self.current_path = []
        
        if self.sound_manager:
            self.sound_manager.play('alert')

    def draw_gradient_background(self):
        for y in range(self.screen_height):
            t = y / self.screen_height
    
            if t < 0.35:  # Sky
                r = int(90 + 80 * t)
                g = int(140 + 80 * t)
                b = int(200 + 40 * t)
            elif t < 0.7:  # Green campus
                tt = (t - 0.35) / 0.35
                r = int(60 - 10 * tt)
                g = int(160 + 40 * tt)
                b = int(90 - 20 * tt)
            else:  # Walkways / ground
                tt = (t - 0.7) / 0.3
                r = int(120 + 40 * tt)
                g = int(110 + 30 * tt)
                b = int(90 + 20 * tt)
    
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
    
        # Subtle campus life details
        for _ in range(1200):
            x = random.randint(0, self.screen_width)
            y = random.randint(int(self.screen_height * 0.35), self.screen_height)
            color = random.choice([
                (90, 180, 110),
                (120, 200, 140),
                (200, 160, 80)
            ])
            self.screen.set_at((x, y), color)

    
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
        
        # Background - solid dark green campus color (no gradient)
        self.screen.fill((60, 100, 70))  # Dark green campus background
        self.screen.set_clip(pygame.Rect(0, 0, self.map_width, self.screen_height))

        # Use camera-based rendering if available
        if self.camera:
            # Camera-based map rendering
            cell_size = int(self.game_map.cell_size * self.camera.zoom)
            
            for y in range(self.game_map.height):
                for x in range(self.game_map.width):
                    # Calculate world and screen positions
                    world_x = x * self.game_map.cell_size
                    world_y = y * self.game_map.cell_size
                    
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
                    is_walkable = self.game_map.grid[y][x] == 0
                    
                    # Draw tile based on walkability
                    if tile_type == TileType.WALL or not is_walkable:
                        # GRASS - non-walkable areas
                        base_green = (80, 160, 90)
                        pygame.draw.rect(self.screen, base_green, rect)
                        # Add grass texture dots
                        if cell_size > 10:
                            for _ in range(3):
                                gx = rect.x + random.randint(2, cell_size - 2)
                                gy = rect.y + random.randint(2, cell_size - 2)
                                pygame.draw.circle(self.screen, (70, 150, 80), (gx, gy), 1)
                    elif tile_type == TileType.CONSTRUCTION:
                        # CONSTRUCTION - orange with red X
                        pygame.draw.rect(self.screen, (200, 120, 50), rect)
                        pygame.draw.line(self.screen, (200, 30, 30), 
                                       (rect.x + 5, rect.y + 5), 
                                       (rect.x + cell_size - 5, rect.y + cell_size - 5), 4)
                        pygame.draw.line(self.screen, (200, 30, 30), 
                                       (rect.x + cell_size - 5, rect.y + 5), 
                                       (rect.x + 5, rect.y + cell_size - 5), 4)
                        pygame.draw.rect(self.screen, (150, 80, 30), rect, 2)
                    else:
                        # ROAD - walkable path
                        pygame.draw.rect(self.screen, (60, 60, 65), rect)
                        # Road tile - no border (cleaner look)
                        
                        # Dashed lane marking (for larger cells)
                        if cell_size > 20:
                            cx = rect.centerx
                            pygame.draw.line(
                                self.screen,
                                (120, 120, 120),
                                (cx, rect.top + 4),
                                (cx, rect.bottom - 4),
                                2
                            )
                        
                        # Add tile-specific indicators
                        if tile_type == TileType.ICE:
                            pygame.draw.line(self.screen, (200, 240, 255), 
                                           (rect.x + 5, rect.y + 10), (rect.x + cell_size - 5, rect.y + 10), 2)
                        elif tile_type == TileType.PORTAL_A or tile_type == TileType.PORTAL_B:
                            pygame.draw.circle(self.screen, (200, 100, 255), rect.center, cell_size // 4)
                        elif tile_type == TileType.TRAP:
                            pygame.draw.line(self.screen, (255, 100, 100), 
                                           (rect.x + 5, rect.y + 5), (rect.x + cell_size - 5, rect.y + cell_size - 5), 2)
                            pygame.draw.line(self.screen, (255, 100, 100), 
                                           (rect.x + cell_size - 5, rect.y + 5), (rect.x + 5, rect.y + cell_size - 5), 2)
                        elif tile_type == TileType.BOOSTER:
                            pygame.draw.polygon(self.screen, (255, 220, 50), [
                                (rect.centerx, rect.y + 5),
                                (rect.x + 5, rect.y + cell_size - 5),
                                (rect.x + cell_size - 5, rect.y + cell_size - 5)
                            ])
                    
                    # Grid lines - only if show_grid is ON
                    if self.show_grid:
                        pygame.draw.rect(self.screen, (40, 45, 55), rect, 1)
                    
                    # Apply fog overlay for explored but not visible tiles
                    if fog_alpha > 0:
                        fog_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                        fog_surface.fill((0, 0, 0, fog_alpha))
                        self.screen.blit(fog_surface, rect.topleft)           
            # (Zone backgrounds, zone labels, and landmarks removed per user request)

            # Draw animated path
            if self.current_path:
                if self.path_algorithm == "BFS":
                    path_color = (255, 105, 180)  # Pink (hot pink)
                elif self.path_algorithm == "A*":
                    path_color = (100, 150, 255)
                else:
                    path_color = (180, 180, 180)

                for i, pos in enumerate(self.current_path):
                    px, py = pos
                    world_x = px * self.game_map.cell_size
                    world_y = py * self.game_map.cell_size
                    screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
                    rect = pygame.Rect(screen_x, screen_y, cell_size, cell_size)
                    if self.path_algorithm == "A*":
                        pygame.draw.circle(
                            self.screen,
                            (255, 255, 255),
                            rect.center,
                            3
                        )

                    path_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                    path_surface.fill((*path_color, 160))
                    self.screen.blit(path_surface, rect.topleft)
                    pygame.draw.rect(self.screen, path_color, rect, 2)
            if self.path_algorithm == "A*":
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    rect.center,
                    3
                )
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
                    # Use a fixed icon size that's visible (icons have labels built-in)
                    icon_size = max(48, cell_size * 2)  # Minimum 48px for visibility
                    icon_scaled = pygame.transform.scale(icon, (icon_size, icon_size))
                    
                    # Draw shadow under the icon for depth
                    shadow_surface = pygame.Surface((icon_size, icon_size // 3), pygame.SRCALPHA)
                    pygame.draw.ellipse(shadow_surface, (0, 0, 0, 80), shadow_surface.get_rect())
                    self.screen.blit(shadow_surface, (rect.centerx - icon_size // 2, rect.centery + icon_size // 3))
                    
                    # Draw the icon
                    self.screen.blit(icon_scaled, (rect.centerx - icon_size // 2, rect.centery - icon_size // 2))
                label_map = {
                    # Main Entrance area
                    "Main Entrance": "GATE",
                    "Kotak Mahindra Bank": "BANK",
                    "Football & Cricket Ground": "SPORTS",
                    
                    # Left side buildings
                    "Design Thinking Huddle": "DTH",
                    "Mechanical Dept": "MECH",
                    "Biotech Quadrangle": "BT-Q",
                    "Green House": "GREEN",
                    
                    # Admin and central buildings
                    "Admin Block": "ADMIN",
                    "IEM Auditorium": "IEM",
                    "RV University": "RVU",
                    "Chem Engg & Physics Dept": "CHEM",
                    
                    # Central area
                    "Civil Dept": "CIVIL",
                    "Kriyakalpa": "KRIYA",
                    "Thode Aur Canteen": "FOOD",
                    "Telecom Dept": "TELE",
                    
                    # EEE and ECE area
                    "EEE Dept": "EEE",
                    "ECE Dept": "ECE",
                    "Mingos Canteen": "MINGO",
                    
                    # Right side - Sports & Hostels
                    "PE & Sports Dept": "PE",
                    "CSE Dept": "CSE",
                    "Health Centre": "MED",
                    "Temple": "TEMPLE",
                    "Krishna Hostel": "KH",
                    "Cauvery Boys Hostel": "CBH",
                    "Mathematics Dept": "MATH",
                    
                    # Library and bottom area
                    "Canteen": "CANTEEN",
                    "Library": "LIB",
                    "ISE & Aerospace Dept": "ISE-A",
                }
                
                
                # Labels are now built into the icons, so no need for separate text rendering
                # short = label_map.get(name)
                # if short:
                #     tag = self.small_font.render(short, True, (240, 240, 240))
                #     tag_rect = tag.get_rect(center=rect.center)
                #     bg = tag_rect.inflate(6, 4)
                #     pygame.draw.rect(self.screen, (20, 20, 30), bg, border_radius=4)
                #     self.screen.blit(tag, tag_rect)

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
            
            # === PLAYER SHADOW (orientation + depth) ===
            shadow = pygame.Surface((cell_size, cell_size//2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 120), shadow.get_rect())
            self.screen.blit(shadow, (player_rect.x, player_rect.bottom - 6))

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
        
            
            # Draw event warnings - DISABLED per user request
            # if self.event_manager:
            #     if self.event_manager.is_fire_drill_active():
            #         warning_font = pygame.font.SysFont('Segoe UI', 20, bold=True)
            #         warning = warning_font.render("🚨 FIRE DRILL IN PROGRESS!", True, (255, 100, 100))
            #         self.screen.blit(warning, (self.screen_width // 3 - 100, 80))
            #         
            #     rain_intensity = self.event_manager.get_rain_intensity()
            #     if rain_intensity > 1:
            #         rain_font = pygame.font.SysFont('Segoe UI', 18)
            #         rain = rain_font.render("🌧 Rain - Movement Slowed", True, (150, 180, 255))
            #         self.screen.blit(rain, (self.screen_width // 3 - 80, 80))
        
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
        
        # Draw new top HUD (timer, riddle, score star)
        self.screen.set_clip(None)

        self.draw_top_hud()
        self.draw_right_panel()

        pygame.display.flip()
    
    def draw_top_hud(self):
        """Draw the new top HUD with timer, riddle, hint, and golden star score"""
        # === TOP TIMER BAR (across screen) ===
        bar_height = 8
        time_ratio = max(0, self.time_remaining / self.max_time)
        bar_color = (100, 255, 150) if self.time_remaining > 60 else (255, 100, 100)
        
        # Background bar
        pygame.draw.rect(self.screen, (40, 40, 50), (0, 0, self.map_width, bar_height + 4))
        # Timer progress
        pygame.draw.rect(self.screen, bar_color, (2, 2, int((self.map_width - 4) * time_ratio), bar_height))
        
        # Timer text in center
        time_text = self.font.render(f"⏱ {self.time_remaining}s", True, bar_color)
        time_rect = time_text.get_rect(center=(self.map_width // 2, bar_height + 18))
        self.screen.blit(time_text, time_rect)
        
        # === GOLDEN STAR SCORE (top right) ===
        star_x = self.map_width - 60
        star_y = 45
        star_radius = 25
        
        # Star shimmer effect
        shimmer_intensity = self.star_shimmer
        base_color = (255, 200, 50)  # Golden color
        shimmer_color = (
            min(255, int(base_color[0] + shimmer_intensity * 50)),
            min(255, int(base_color[1] + shimmer_intensity * 55)),
            min(255, int(base_color[2] + shimmer_intensity * 150))
        )
        
        # Draw glowing star background if shimmering
        if shimmer_intensity > 0.1:
            glow_radius = int(star_radius + 15 * shimmer_intensity)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*shimmer_color, int(80 * shimmer_intensity)), 
                             (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surface, (star_x - glow_radius, star_y - glow_radius))
        
        # Draw 5-pointed star
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = star_radius if i % 2 == 0 else star_radius * 0.4
            points.append((star_x + r * math.cos(angle), star_y + r * math.sin(angle)))
        pygame.draw.polygon(self.screen, shimmer_color, points)
        pygame.draw.polygon(self.screen, (255, 255, 200), points, 2)
        
        # Bright orange score text NEXT TO star (left side)
        score_text = self.large_font.render(f"{self.score}", True, (255, 140, 0))  # Bright orange
        score_rect = score_text.get_rect(midright=(star_x - star_radius - 10, star_y))
        self.screen.blit(score_text, score_rect)
        
        # Level display below score and star
        level_color = [(150, 200, 150), (100, 200, 255), (255, 200, 100)][self.current_level - 1]
        level_text = self.small_font.render(f"Lvl {self.current_level}: {self.level_names[self.current_level]}", 
                                             True, level_color)
        level_rect = level_text.get_rect(topright=(self.map_width - 15, star_y + star_radius + 5))
        self.screen.blit(level_text, level_rect)

        if self.ui_message and self.ui_message_timer > 0:
            msg = self.large_font.render(self.ui_message, True, (255, 255, 200))
            rect = msg.get_rect(center=(self.map_width // 2, self.screen_height - 70))
            bg = rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (30, 30, 40), bg, border_radius=10)
            self.screen.blit(msg, rect)
        # === CONTROLS (bottom left compact) ===
        controls_text = self.small_font.render("↑↓←→ Move | H Hint | B/A Path | P Pause | ESC Menu", 
                                                True, (90, 95, 115))
        self.screen.blit(controls_text, (10, self.screen_height - 18))
        
        
        # === GAME STATE OVERLAYS ===
        if self.state == GameState.PAUSED:
            self.draw_overlay("⏸ PAUSED", "P - Continue | R - Restart | M - Menu", (255, 220, 100))
        elif self.state == GameState.VICTORY:
            self.draw_overlay("🏆 VICTORY!", f"Score: {self.score} | R - Restart | M - Menu", (100, 255, 150))
        elif self.state == GameState.GAME_OVER:
            self.draw_overlay("⏰ TIME'S UP!", f"Score: {self.score} | R - Retry | M - Menu", (255, 100, 100))
    
    def draw_right_panel(self):
        panel_x = self.map_width
        panel = pygame.Rect(panel_x, 0, self.panel_width, self.screen_height)

        # Background
        pygame.draw.rect(self.screen, (22, 26, 38), panel)
        pygame.draw.line(self.screen, (70, 90, 140),
                        (panel_x, 0), (panel_x, self.screen_height), 3)

        x = panel_x + 20
        y = 25
        width = self.panel_width - 40

        # Difficulty + Level badge
        diff = self.difficulty_settings[self.difficulty]['name']
        badge = self.large_font.render(
            f"{diff} · Level {self.current_level}", True, (255, 200, 120)
        )
        self.screen.blit(badge, (x, y))
        pygame.draw.line(
            self.screen,
            (60, 70, 95),
            (x, y + 30),
            (x + width, y + 30),
            1
        )
        y += 55

        if not self.task_manager.current_task:
            return

        task = self.task_manager.current_task
        # === TASK CARD ===
        pygame.draw.rect(self.screen, (35, 45, 65),
                        (x, y, width, 90), border_radius=10)

        # Generic task title (does NOT reveal location)
        title_text = "Destination Identified" if self.show_hint else "Solve the Riddle"
        title = self.font.render(title_text, True, (150, 220, 255))
        self.screen.blit(title, (x + 12, y + 12))

        # Reveal location ONLY if hint is shown or task completed
        if self.show_hint:
            loc = self.small_font.render(f"📍 {task['building']}", True, (180, 180, 220))
        else:
            loc = self.small_font.render("📍 Destination unknown", True, (130, 130, 150))

        self.screen.blit(loc, (x + 12, y + 40))
        y += 110
        # === RIDDLE CARD ===
        pygame.draw.rect(self.screen, (30, 35, 55),
                        (x, y, width, 200), border_radius=10)
        ry = y + 16
        max_lines = 10
        line_count = 0
        for line in task["riddle"].split("\n"):
            wrapped = self.wrap_text(line, self.small_font, width - 24)
            for w in wrapped:
                if line_count >= max_lines:
                    break
                txt = self.small_font.render(w, True, (230, 230, 240))
                self.screen.blit(txt, (x + 12, ry))
                ry += 24
                line_count += 1
            if line_count >= max_lines:
                break
            ry += 4
        y += 220
        # === HINT CARD ===
        pygame.draw.rect(self.screen, (40, 40, 60),
                        (x, y, width, 90), border_radius=10)

        hint_text = (
            task["hint"]
            if self.show_hint
            else f"[H] Show Hint (-{self.hint_cost} pts)"
        )

        wrapped_hint = self.wrap_text(hint_text, self.small_font, width - 24)
        hy = y + 12
        for line in wrapped_hint[:3]:
            htxt = self.font.render(line, True, (220, 190, 120) if self.show_hint else (130, 130, 150))
            self.screen.blit(htxt, (x + 12, hy))
            hy += 18

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