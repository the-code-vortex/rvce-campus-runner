"""
Game Screens Module for RVCE Campus Runner
Contains all menu screens, buttons, and UI components
"""
import pygame
import math
import json
import os
from datetime import datetime

# Colors
COLORS = {
    'bg_dark': (15, 20, 35),
    'bg_medium': (25, 35, 55),
    'primary': (100, 200, 255),
    'secondary': (255, 200, 100),
    'success': (100, 255, 150),
    'danger': (255, 100, 100),
    'text_light': (220, 230, 255),
    'text_muted': (150, 160, 180),
    'card_bg': (35, 45, 65),
    'gold': (255, 215, 0),
    'silver': (192, 192, 192),
    'bronze': (205, 127, 50),
}


class Button:
    """Reusable button component with hover effects"""
    
    def __init__(self, x, y, width, height, text, color=None, text_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color or COLORS['primary']
        self.text_color = text_color or COLORS['bg_dark']
        self.hover = False
        self.click_animation = 0
        
    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
        if self.click_animation > 0:
            self.click_animation -= 0.1
            
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.click_animation = 1.0
                return True
        return False
    
    def draw(self, screen, font):
        # Calculate animation offset
        scale = 1.0 + (0.05 if self.hover else 0) - (0.02 * self.click_animation)
        
        # Draw shadow
        shadow_rect = self.rect.inflate(4, 4)
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        # Draw button
        color = self.color
        if self.hover:
            color = tuple(min(255, c + 30) for c in self.color)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255, 100), self.rect, 2, border_radius=10)
        
        # Draw text
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class MenuParticle:
    """Floating particles for menu background"""
    
    def __init__(self, screen_width, screen_height):
        self.x = pygame.time.get_ticks() % screen_width
        self.y = pygame.time.get_ticks() % screen_height
        self.reset(screen_width, screen_height)
        
    def reset(self, screen_width, screen_height):
        import random
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.vx = random.uniform(-20, 20)
        self.vy = random.uniform(-20, 20)
        self.size = random.randint(2, 5)
        self.alpha = random.randint(50, 150)
        self.color = (random.randint(80, 150), random.randint(150, 220), 255)
        
    def update(self, dt, screen_width, screen_height):
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        if self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height:
            self.reset(screen_width, screen_height)
            
    def draw(self, screen):
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha), (self.size, self.size), self.size)
        screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class HighScoreManager:
    """Manages high score persistence"""
    
    def __init__(self, scores_file="high_scores.json"):
        self.scores_file = scores_file
        self.scores = []
        self.load_scores()
        
    def load_scores(self):
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    data = json.load(f)
                    self.scores = data.get('scores', [])
        except (json.JSONDecodeError, IOError):
            self.scores = []
            
    def save_scores(self):
        try:
            with open(self.scores_file, 'w') as f:
                json.dump({'scores': self.scores}, f, indent=2)
        except IOError:
            pass
            
    def add_score(self, name, score, difficulty="Normal"):
        entry = {
            'name': name[:10],  # Limit name length
            'score': score,
            'difficulty': difficulty,
            'date': datetime.now().strftime("%Y-%m-%d")
        }
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:10]  # Keep top 10
        self.save_scores()
        
    def is_high_score(self, score):
        if len(self.scores) < 10:
            return True
        return score > self.scores[-1]['score']
    
    def get_rank(self, score):
        for i, entry in enumerate(self.scores):
            if score >= entry['score']:
                return i + 1
        return len(self.scores) + 1


class MainMenuScreen:
    """Main menu with animated title and buttons"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Fonts
        self.title_font = pygame.font.SysFont('Segoe UI', 72, bold=True)
        self.subtitle_font = pygame.font.SysFont('Segoe UI', 36, bold=True)
        self.button_font = pygame.font.SysFont('Segoe UI', 24, bold=True)
        self.small_font = pygame.font.SysFont('Segoe UI', 18)
        
        # Animation
        self.animation_time = 0
        self.particles = [MenuParticle(screen_width, screen_height) for _ in range(50)]
        
        # Create buttons
        button_width = 280
        button_height = 55
        button_x = (screen_width - button_width) // 2
        button_start_y = screen_height // 2 - 20
        button_spacing = 70
        
        self.buttons = {
            'start': Button(button_x, button_start_y, button_width, button_height, 
                           "🎮  Start Game", COLORS['success']),
            'difficulty': Button(button_x, button_start_y + button_spacing, button_width, button_height,
                                "⚙️  Difficulty", COLORS['primary']),
            'how_to_play': Button(button_x, button_start_y + button_spacing * 2, button_width, button_height,
                                 "📖  How To Play", COLORS['secondary']),
            'high_scores': Button(button_x, button_start_y + button_spacing * 3, button_width, button_height,
                                 "🏆  High Scores", COLORS['gold']),
            'exit': Button(button_x, button_start_y + button_spacing * 4, button_width, button_height,
                          "🚪  Exit", COLORS['danger']),
        }
        
    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.is_clicked(event):
                return name
        return None
    
    def update(self, dt):
        self.animation_time += dt
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons.values():
            button.update(mouse_pos)
            
        for particle in self.particles:
            particle.update(dt, self.screen_width, self.screen_height)
            
    def draw(self, screen):
        # Draw gradient background
        for y in range(self.screen_height):
            progress = y / self.screen_height
            r = int(10 + progress * 20)
            g = int(15 + progress * 25)
            b = int(35 + progress * 30)
            pygame.draw.line(screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw animated title
        title_y = self.screen_height // 6
        glow_offset = math.sin(self.animation_time * 2) * 5
        
        # Title glow
        for i in range(3):
            glow_alpha = 100 - i * 30
            glow_color = (100, 200, 255)
            title = self.title_font.render("RVCE", True, glow_color)
            title.set_alpha(glow_alpha)
            title_rect = title.get_rect(center=(self.screen_width // 2 + glow_offset, title_y))
            screen.blit(title, title_rect)
        
        # Main title
        title = self.title_font.render("RVCE", True, COLORS['primary'])
        title_rect = title.get_rect(center=(self.screen_width // 2, title_y))
        screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.subtitle_font.render("Campus Runner", True, COLORS['text_light'])
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, title_y + 70))
        screen.blit(subtitle, subtitle_rect)
        
        # Tagline
        tagline = self.small_font.render("Master Pathfinding Algorithms on RVCE Campus", True, COLORS['text_muted'])
        tagline_rect = tagline.get_rect(center=(self.screen_width // 2, title_y + 110))
        screen.blit(tagline, tagline_rect)
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen, self.button_font)
        
        # Footer
        footer = self.small_font.render("DSA Project - Pathfinding Algorithms | Press ESC to Exit", 
                                        True, COLORS['text_muted'])
        footer_rect = footer.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        screen.blit(footer, footer_rect)


class HowToPlayScreen:
    """Tutorial screen with game instructions"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.title_font = pygame.font.SysFont('Segoe UI', 48, bold=True)
        self.heading_font = pygame.font.SysFont('Segoe UI', 24, bold=True)
        self.text_font = pygame.font.SysFont('Segoe UI', 18)
        self.button_font = pygame.font.SysFont('Segoe UI', 22, bold=True)
        
        self.back_button = Button((screen_width - 200) // 2, screen_height - 80, 
                                  200, 50, "← Back to Menu", COLORS['primary'])
        
        self.instructions = [
            ("🎯 OBJECTIVE", [
                "Complete academic tasks by navigating to different campus buildings.",
                "Earn points by completing tasks before time runs out!",
            ]),
            ("⌨️ MOVEMENT", [
                "↑ ↓ ← → (Arrow Keys) - Move your character",
                "U - Undo last move",
            ]),
            ("🔍 PATHFINDING", [
                "B - Show path using BFS (Breadth-First Search) - Green",
                "A - Show path using A* Algorithm - Blue",
                "C - Clear the current path",
            ]),
            ("🎮 GAME CONTROLS", [
                "P - Pause/Resume game",
                "R - Restart game",
                "ESC - Exit to menu",
            ]),
            ("💡 TIPS", [
                "Follow the glowing yellow building - that's your target!",
                "A* algorithm is usually more efficient than BFS!",
                "Complete tasks quickly for bonus time points!",
            ]),
        ]
        
    def handle_event(self, event):
        if self.back_button.is_clicked(event):
            return 'back'
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'back'
        return None
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.update(mouse_pos)
        
    def draw(self, screen):
        # Background
        screen.fill(COLORS['bg_dark'])
        
        # Title
        title = self.title_font.render("📖 How To Play", True, COLORS['primary'])
        title_rect = title.get_rect(center=(self.screen_width // 2, 60))
        screen.blit(title, title_rect)
        
        # Instructions cards
        card_width = min(700, self.screen_width - 100)
        card_x = (self.screen_width - card_width) // 2
        y_offset = 120
        
        for section_title, items in self.instructions:
            # Section title
            heading = self.heading_font.render(section_title, True, COLORS['secondary'])
            screen.blit(heading, (card_x, y_offset))
            y_offset += 35
            
            # Section items
            for item in items:
                text = self.text_font.render(item, True, COLORS['text_light'])
                screen.blit(text, (card_x + 20, y_offset))
                y_offset += 25
                
            y_offset += 20
        
        # Back button
        self.back_button.draw(screen, self.button_font)


class HighScoresScreen:
    """Display top 10 high scores"""
    
    def __init__(self, screen_width, screen_height, score_manager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.score_manager = score_manager
        
        self.title_font = pygame.font.SysFont('Segoe UI', 48, bold=True)
        self.score_font = pygame.font.SysFont('Segoe UI', 22)
        self.rank_font = pygame.font.SysFont('Segoe UI', 26, bold=True)
        self.button_font = pygame.font.SysFont('Segoe UI', 22, bold=True)
        
        self.back_button = Button((screen_width - 200) // 2, screen_height - 80,
                                  200, 50, "← Back to Menu", COLORS['primary'])
        
    def handle_event(self, event):
        if self.back_button.is_clicked(event):
            return 'back'
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'back'
        return None
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.update(mouse_pos)
        
    def draw(self, screen):
        screen.fill(COLORS['bg_dark'])
        
        # Title
        title = self.title_font.render("🏆 High Scores", True, COLORS['gold'])
        title_rect = title.get_rect(center=(self.screen_width // 2, 60))
        screen.blit(title, title_rect)
        
        # Score list
        scores = self.score_manager.scores
        card_width = min(600, self.screen_width - 100)
        card_x = (self.screen_width - card_width) // 2
        y_offset = 130
        
        if not scores:
            no_scores = self.score_font.render("No high scores yet. Play to set a record!", 
                                               True, COLORS['text_muted'])
            no_scores_rect = no_scores.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(no_scores, no_scores_rect)
        else:
            # Header
            header = self.score_font.render("RANK    NAME           SCORE    DIFFICULTY    DATE", 
                                           True, COLORS['text_muted'])
            screen.blit(header, (card_x, y_offset))
            y_offset += 40
            
            for i, entry in enumerate(scores[:10]):
                # Rank color
                if i == 0:
                    rank_color = COLORS['gold']
                    medal = "🥇"
                elif i == 1:
                    rank_color = COLORS['silver']
                    medal = "🥈"
                elif i == 2:
                    rank_color = COLORS['bronze']
                    medal = "🥉"
                else:
                    rank_color = COLORS['text_light']
                    medal = f"#{i+1}"
                
                # Card background
                card_rect = pygame.Rect(card_x - 10, y_offset - 5, card_width + 20, 40)
                pygame.draw.rect(screen, COLORS['card_bg'], card_rect, border_radius=8)
                
                # Rank
                rank_text = self.rank_font.render(medal, True, rank_color)
                screen.blit(rank_text, (card_x + 10, y_offset))
                
                # Name
                name_text = self.score_font.render(entry['name'].ljust(12), True, COLORS['text_light'])
                screen.blit(name_text, (card_x + 80, y_offset + 3))
                
                # Score
                score_text = self.score_font.render(str(entry['score']).ljust(8), True, COLORS['success'])
                screen.blit(score_text, (card_x + 230, y_offset + 3))
                
                # Difficulty
                diff_text = self.score_font.render(entry.get('difficulty', 'Normal').ljust(10), 
                                                   True, COLORS['secondary'])
                screen.blit(diff_text, (card_x + 340, y_offset + 3))
                
                # Date
                date_text = self.score_font.render(entry['date'], True, COLORS['text_muted'])
                screen.blit(date_text, (card_x + 480, y_offset + 3))
                
                y_offset += 50
        
        self.back_button.draw(screen, self.button_font)


class DifficultySelectScreen:
    """Difficulty selection screen"""
    
    DIFFICULTIES = {
        'easy': {'name': 'Easy', 'time': 420, 'tasks': 5, 'color': COLORS['success'], 
                 'desc': '7 minutes, 5 tasks'},
        'normal': {'name': 'Normal', 'time': 300, 'tasks': 7, 'color': COLORS['primary'],
                   'desc': '5 minutes, all 7 tasks'},
        'hard': {'name': 'Hard', 'time': 180, 'tasks': 7, 'color': COLORS['danger'],
                 'desc': '3 minutes, all 7 tasks'},
    }
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.selected_difficulty = 'normal'
        
        self.title_font = pygame.font.SysFont('Segoe UI', 48, bold=True)
        self.button_font = pygame.font.SysFont('Segoe UI', 24, bold=True)
        self.desc_font = pygame.font.SysFont('Segoe UI', 18)
        
        # Difficulty buttons
        button_width = 250
        button_height = 80
        button_x = (screen_width - button_width) // 2
        button_start_y = screen_height // 3
        button_spacing = 100
        
        self.difficulty_buttons = {}
        for i, (key, diff) in enumerate(self.DIFFICULTIES.items()):
            self.difficulty_buttons[key] = Button(
                button_x, button_start_y + i * button_spacing,
                button_width, button_height,
                f"{diff['name']}", diff['color']
            )
        
        self.back_button = Button((screen_width - 200) // 2, screen_height - 80,
                                  200, 50, "← Back to Menu", COLORS['text_muted'])
        
    def handle_event(self, event):
        for key, button in self.difficulty_buttons.items():
            if button.is_clicked(event):
                self.selected_difficulty = key
                return ('select', key)
        
        if self.back_button.is_clicked(event):
            return ('back', None)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return ('back', None)
        return None
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.difficulty_buttons.values():
            button.update(mouse_pos)
        self.back_button.update(mouse_pos)
        
    def draw(self, screen):
        screen.fill(COLORS['bg_dark'])
        
        # Title
        title = self.title_font.render("⚙️ Select Difficulty", True, COLORS['primary'])
        title_rect = title.get_rect(center=(self.screen_width // 2, 70))
        screen.blit(title, title_rect)
        
        # Difficulty buttons with descriptions
        for key, button in self.difficulty_buttons.items():
            button.draw(screen, self.button_font)
            
            # Description below button
            diff = self.DIFFICULTIES[key]
            desc = self.desc_font.render(diff['desc'], True, COLORS['text_muted'])
            desc_rect = desc.get_rect(center=(button.rect.centerx, button.rect.bottom + 15))
            screen.blit(desc, desc_rect)
            
            # Check mark for selected
            if key == self.selected_difficulty:
                check = self.button_font.render("✓", True, COLORS['success'])
                screen.blit(check, (button.rect.right + 15, button.rect.centery - 12))
        
        self.back_button.draw(screen, self.button_font)


class NameEntryScreen:
    """Screen for entering name after high score"""
    
    def __init__(self, screen_width, screen_height, score, rank):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.score = score
        self.rank = rank
        self.name = ""
        self.max_length = 10
        
        self.title_font = pygame.font.SysFont('Segoe UI', 48, bold=True)
        self.text_font = pygame.font.SysFont('Segoe UI', 24)
        self.name_font = pygame.font.SysFont('Segoe UI', 36, bold=True)
        self.button_font = pygame.font.SysFont('Segoe UI', 22, bold=True)
        
        self.submit_button = Button((screen_width - 200) // 2, screen_height - 150,
                                    200, 50, "Submit Score", COLORS['success'])
        self.skip_button = Button((screen_width - 200) // 2, screen_height - 80,
                                  200, 50, "Skip", COLORS['text_muted'])
        
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.name:
                return ('submit', self.name)
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif event.key == pygame.K_ESCAPE:
                return ('skip', None)
            elif len(self.name) < self.max_length:
                if event.unicode.isalnum() or event.unicode == ' ':
                    self.name += event.unicode.upper()
        
        if self.submit_button.is_clicked(event) and self.name:
            return ('submit', self.name)
        if self.skip_button.is_clicked(event):
            return ('skip', None)
        
        return None
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.submit_button.update(mouse_pos)
        self.skip_button.update(mouse_pos)
        
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
    def draw(self, screen):
        screen.fill(COLORS['bg_dark'])
        
        # Celebration title
        title = self.title_font.render("🎉 NEW HIGH SCORE! 🎉", True, COLORS['gold'])
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title, title_rect)
        
        # Score display
        score_text = self.text_font.render(f"Score: {self.score} | Rank: #{self.rank}", 
                                           True, COLORS['success'])
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 140))
        screen.blit(score_text, score_rect)
        
        # Prompt
        prompt = self.text_font.render("Enter your name:", True, COLORS['text_light'])
        prompt_rect = prompt.get_rect(center=(self.screen_width // 2, 220))
        screen.blit(prompt, prompt_rect)
        
        # Name input box
        box_width = 400
        box_height = 60
        box_x = (self.screen_width - box_width) // 2
        box_y = 260
        
        pygame.draw.rect(screen, COLORS['card_bg'], 
                        (box_x, box_y, box_width, box_height), border_radius=10)
        pygame.draw.rect(screen, COLORS['primary'], 
                        (box_x, box_y, box_width, box_height), 3, border_radius=10)
        
        # Name text with cursor
        display_name = self.name
        if self.cursor_visible:
            display_name += "_"
        name_text = self.name_font.render(display_name, True, COLORS['text_light'])
        name_rect = name_text.get_rect(center=(self.screen_width // 2, box_y + box_height // 2))
        screen.blit(name_text, name_rect)
        
        # Character count
        count = self.text_font.render(f"{len(self.name)}/{self.max_length}", True, COLORS['text_muted'])
        count_rect = count.get_rect(topright=(box_x + box_width - 10, box_y + box_height + 5))
        screen.blit(count, count_rect)
        
        # Buttons
        self.submit_button.draw(screen, self.button_font)
        self.skip_button.draw(screen, self.button_font)
