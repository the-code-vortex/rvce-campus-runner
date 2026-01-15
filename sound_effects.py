"""
Sound Effects Module for RVCE Campus Runner
Generates sounds programmatically using pygame.sndarray (no external files)
"""
import pygame
import numpy as np
import math

class SoundManager:
    """Manages all game sounds generated programmatically"""
    
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Pre-generate all sounds
        self.sounds = {}
        self._generate_sounds()
        
        # Volume settings
        self.sfx_volume = 0.5
        self.enabled = True
        
    def _generate_sounds(self):
        """Generate all game sounds"""
        self.sounds['menu_select'] = self._create_beep(440, 0.1, 'sine')
        self.sounds['menu_hover'] = self._create_beep(330, 0.05, 'sine')
        self.sounds['task_complete'] = self._create_success_sound()
        self.sounds['teleport'] = self._create_whoosh()
        self.sounds['trap'] = self._create_buzz()
        self.sounds['booster'] = self._create_powerup()
        self.sounds['ice_slide'] = self._create_slide()
        self.sounds['npc_talk'] = self._create_beep(500, 0.15, 'square')
        self.sounds['step'] = self._create_step()
        self.sounds['game_over'] = self._create_game_over()
        self.sounds['victory'] = self._create_victory()
        self.sounds['alert'] = self._create_alert()
        
    def _create_beep(self, frequency, duration, wave_type='sine'):
        """Create a simple beep sound"""
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        
        if wave_type == 'sine':
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == 'square':
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == 'triangle':
            wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        else:
            wave = np.sin(2 * np.pi * frequency * t)
        
        # Apply envelope
        envelope = np.ones(n_samples)
        attack = int(n_samples * 0.1)
        release = int(n_samples * 0.3)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        wave = (wave * envelope * 32767 * 0.5).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo)
        
    def _create_success_sound(self):
        """Create a pleasant success jingle"""
        sample_rate = 22050
        duration = 0.4
        n_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        
        # Three ascending notes
        freq1, freq2, freq3 = 523, 659, 784  # C5, E5, G5
        
        part1 = int(n_samples * 0.33)
        part2 = int(n_samples * 0.66)
        
        wave = np.zeros(n_samples, dtype=np.float32)
        wave[:part1] = np.sin(2 * np.pi * freq1 * t[:part1])
        wave[part1:part2] = np.sin(2 * np.pi * freq2 * t[part1:part2])
        wave[part2:] = np.sin(2 * np.pi * freq3 * t[part2:])
        
        # Envelope
        envelope = np.exp(-t * 3)
        wave = (wave * envelope * 32767 * 0.5).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo)
        
    def _create_whoosh(self):
        """Create a whoosh/teleport sound"""
        sample_rate = 22050
        duration = 0.3
        n_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        
        # Sweeping frequency
        freq = 200 + 800 * t / duration
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        wave = np.sin(phase)
        
        # Add some noise
        noise = np.random.randn(n_samples) * 0.2
        wave = wave * 0.7 + noise * 0.3
        
        envelope = np.exp(-t * 5)
        wave = (wave * envelope * 32767 * 0.4).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo)
        
    def _create_buzz(self):
        """Create a buzzing/trap sound"""
        sample_rate = 22050
        duration = 0.25
        n_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        
        # Harsh buzz
        wave = np.sign(np.sin(2 * np.pi * 150 * t)) * np.sin(2 * np.pi * 50 * t)
        
        envelope = np.exp(-t * 8)
        wave = (wave * envelope * 32767 * 0.4).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo)
        
    def _create_powerup(self):
        """Create a power-up sound"""
        sample_rate = 22050
        duration = 0.3
        n_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        
        # Rising tone
        freq = 300 + 400 * (t / duration) ** 2
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        wave = np.sin(phase)
        
        envelope = 1 - (t / duration) ** 0.5
        wave = (wave * envelope * 32767 * 0.5).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo)
        
    def _create_slide(self):
        """Create an ice slide sound"""
        sample_rate = 22050
        duration = 0.15
        n_samples = int(sample_rate * duration)
        
        # White noise with filter effect
        noise = np.random.randn(n_samples)
        
        # Simple lowpass
        filtered = np.convolve(noise, np.ones(10)/10, mode='same')
        
        envelope = np.exp(-np.linspace(0, 1, n_samples) * 4)
        wave = (filtered * envelope * 32767 * 0.3).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo)
        
    def _create_step(self):
        """Create a footstep sound"""
        sample_rate = 22050
        duration = 0.08
        n_samples = int(sample_rate * duration)
        
        # Short thump
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        wave = np.sin(2 * np.pi * 80 * t) * np.exp(-t * 50)
        
        wave = (wave * 32767 * 0.2).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo)
        
    def _create_game_over(self):
        """Create a game over sound"""
        sample_rate = 22050
        duration = 0.6
        n_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        
        # Descending tones
        freq = 400 - 200 * (t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        wave = np.sin(phase)
        
        envelope = np.exp(-t * 2)
        wave = (wave * envelope * 32767 * 0.5).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo)
        
    def _create_victory(self):
        """Create a victory fanfare"""
        sample_rate = 22050
        duration = 0.8
        n_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        
        # Happy ascending arpeggio
        freqs = [523, 659, 784, 1047]  # C5, E5, G5, C6
        part_len = n_samples // 4
        
        wave = np.zeros(n_samples, dtype=np.float32)
        for i, freq in enumerate(freqs):
            start = i * part_len
            end = min((i + 1) * part_len, n_samples)
            wave[start:end] = np.sin(2 * np.pi * freq * t[start:end])
        
        envelope = np.exp(-t * 1.5)
        wave = (wave * envelope * 32767 * 0.5).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo)
        
    def _create_alert(self):
        """Create an alert/warning sound"""
        sample_rate = 22050
        duration = 0.3
        n_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        
        # Two-tone alert
        mid = n_samples // 2
        wave = np.zeros(n_samples, dtype=np.float32)
        wave[:mid] = np.sin(2 * np.pi * 800 * t[:mid])
        wave[mid:] = np.sin(2 * np.pi * 600 * t[mid:])
        
        envelope = np.ones(n_samples)
        envelope[-int(n_samples * 0.2):] = np.linspace(1, 0, int(n_samples * 0.2))
        
        wave = (wave * envelope * 32767 * 0.4).astype(np.int16)
        stereo = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo)
        
    def play(self, sound_name):
        """Play a sound by name"""
        if not self.enabled:
            return
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(self.sfx_volume)
            self.sounds[sound_name].play()
            
    def set_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
    def toggle(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        return self.enabled
