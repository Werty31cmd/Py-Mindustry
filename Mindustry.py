import pygame
import random
import sys
import math
import threading

# Инициализация Pygame
pygame.init()

# Настройки окна
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Цвета (улучшенная палитра)
BLACK = (10, 10, 15)
WHITE = (240, 240, 245)
GRAY = (100, 100, 110)
DARK_GRAY = (40, 40, 50)
LIGHT_GRAY = (160, 160, 170)
RED = (220, 50, 50)
DARK_RED = (150, 30, 30)
GREEN = (50, 200, 50)
DARK_GREEN = (30, 120, 30)
BLUE = (50, 150, 255)
YELLOW = (255, 220, 50)
ORANGE = (255, 150, 50)
PURPLE = (180, 100, 255)
CYAN = (50, 255, 255)
BROWN = (139, 69, 19)
THORIUM_COLOR = (150, 0, 255)

# Улучшенная цветовая схема для ресурсов
RESOURCE_COLORS = {
    'copper': (255, 170, 60),
    'coal': (60, 60, 65),
    'titanium': (180, 180, 220),
    'thorium': (150, 0, 255)
}

class Particle:
    def __init__(self, x, y, color, velocity, size, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.size *= 0.95
        
    def draw(self, screen, camera_x, camera_y):
        if self.lifetime > 0:
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color = (*self.color[:3], alpha)
            pygame.draw.circle(screen, color[:3], (int(screen_x), int(screen_y)), int(self.size))

class ConveyorItem:
    def __init__(self, x, y, resource_type):
        self.x = x
        self.y = y
        self.type = resource_type
        self.progress = 0
        self.speed = 0.02
        
    def update(self):
        self.progress += self.speed
        
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        color = RESOURCE_COLORS.get(self.type, WHITE)
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), 5)
        pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), 2)

class Conveyor:
    def __init__(self, x, y, direction='right'):
        self.x = x
        self.y = y
        self.type = 'conveyor'
        self.health = 100
        self.max_health = 100
        self.size = 30
        self.direction = direction
        self.animation_timer = 0
        self.items = []
        self.connected_to = []
        
        self.config = {
            'color': (100, 100, 110),
            'health': 100,
            'cost': {'copper': 25},
            'size': 30
        }
        
    def add_item(self, resource_type):
        if len(self.items) < 3:
            self.items.append(ConveyorItem(self.x, self.y, resource_type))
            
    def update(self, conveyors, buildings):
        self.animation_timer += 1
        
        for item in self.items[:]:
            item.update()
            
            if self.direction == 'right':
                item.x = self.x + item.progress * 30
                item.y = self.y
            elif self.direction == 'left':
                item.x = self.x - item.progress * 30
                item.y = self.y
            elif self.direction == 'up':
                item.x = self.x
                item.y = self.y - item.progress * 30
            elif self.direction == 'down':
                item.x = self.x
                item.y = self.y + item.progress * 30
                
            if item.progress >= 1:
                next_pos = self.get_next_position()
                
                for conveyor in conveyors:
                    if conveyor != self and abs(conveyor.x - next_pos[0]) < 5 and abs(conveyor.y - next_pos[1]) < 5:
                        conveyor.add_item(item.type)
                        self.items.remove(item)
                        break
                else:
                    for building in buildings:
                        if building.type == 'core' and abs(building.x - next_pos[0]) < 40 and abs(building.y - next_pos[1]) < 40:
                            self.items.remove(item)
                            return item.type, 1
                    else:
                        self.items.remove(item)
                        
        return None, 0
        
    def get_next_position(self):
        if self.direction == 'right':
            return (self.x + 30, self.y)
        elif self.direction == 'left':
            return (self.x - 30, self.y)
        elif self.direction == 'up':
            return (self.x, self.y - 30)
        elif self.direction == 'down':
            return (self.x, self.y + 30)
        return (self.x, self.y)
        
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if -50 < screen_x < WINDOW_WIDTH + 50 and -50 < screen_y < WINDOW_HEIGHT + 50:
            pygame.draw.rect(screen, (60, 60, 70), 
                           (screen_x - 15, screen_y - 15, 30, 30))
            pygame.draw.rect(screen, (40, 40, 50), 
                           (screen_x - 15, screen_y - 15, 30, 30), 2)
            
            if self.direction in ['right', 'left']:
                for i in range(3):
                    offset = (self.animation_timer * 3 + i * 10) % 30
                    if self.direction == 'right':
                        stripe_x = screen_x - 15 + offset
                    else:
                        stripe_x = screen_x + 15 - offset
                    pygame.draw.rect(screen, (80, 80, 90), 
                                   (stripe_x, screen_y - 12, 3, 24))
            else:
                for i in range(3):
                    offset = (self.animation_timer * 3 + i * 10) % 30
                    if self.direction == 'down':
                        stripe_y = screen_y - 15 + offset
                    else:
                        stripe_y = screen_y + 15 - offset
                    pygame.draw.rect(screen, (80, 80, 90), 
                                   (screen_x - 12, stripe_y, 24, 3))
            
            center_x = screen_x
            center_y = screen_y
            if self.direction == 'right':
                pygame.draw.polygon(screen, YELLOW, [
                    (center_x + 10, center_y),
                    (center_x + 5, center_y - 5),
                    (center_x + 5, center_y + 5)
                ])
            elif self.direction == 'left':
                pygame.draw.polygon(screen, YELLOW, [
                    (center_x - 10, center_y),
                    (center_x - 5, center_y - 5),
                    (center_x - 5, center_y + 5)
                ])
            elif self.direction == 'up':
                pygame.draw.polygon(screen, YELLOW, [
                    (center_x, center_y - 10),
                    (center_x - 5, center_y - 5),
                    (center_x + 5, center_y - 5)
                ])
            elif self.direction == 'down':
                pygame.draw.polygon(screen, YELLOW, [
                    (center_x, center_y + 10),
                    (center_x - 5, center_y + 5),
                    (center_x + 5, center_y + 5)
                ])
            
            for item in self.items:
                item.draw(screen, camera_x, camera_y)

class ResourceDeposit:
    def __init__(self, x, y, resource_type):
        self.x = x
        self.y = y
        self.type = resource_type
        self.amount = random.randint(500, 1500)
        self.size = 20
        self.pulse = random.uniform(0, math.pi * 2)
        self.veins = []
        
        for _ in range(random.randint(3, 6)):
            vein_x = random.randint(-15, 15)
            vein_y = random.randint(-15, 15)
            vein_size = random.randint(3, 8)
            self.veins.append((vein_x, vein_y, vein_size))
        
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if -50 < screen_x < WINDOW_WIDTH + 50 and -50 < screen_y < WINDOW_HEIGHT + 50:
            self.pulse += 0.03
            pulse_size = self.size + math.sin(self.pulse) * 2
            
            color = RESOURCE_COLORS.get(self.type, WHITE)
            
            glow_surf = pygame.Surface((pulse_size * 4, pulse_size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, 30), 
                             (pulse_size * 2, pulse_size * 2), pulse_size * 2)
            screen.blit(glow_surf, (screen_x - pulse_size * 2, screen_y - pulse_size * 2))
            
            for vein_x, vein_y, vein_size in self.veins:
                pygame.draw.circle(screen, color, 
                                 (int(screen_x + vein_x), int(screen_y + vein_y)), vein_size)
            
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), int(pulse_size))
            pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), int(pulse_size), 2)
            
            if self.type == 'copper':
                pygame.draw.circle(screen, (255, 200, 100), (int(screen_x), int(screen_y)), 6)
            elif self.type == 'coal':
                pygame.draw.rect(screen, (30, 30, 35), 
                               (int(screen_x) - 4, int(screen_y) - 4, 8, 8))
            elif self.type == 'titanium':
                pygame.draw.polygon(screen, (220, 220, 255), [
                    (int(screen_x), int(screen_y) - 6),
                    (int(screen_x) + 6, int(screen_y) + 6),
                    (int(screen_x) - 6, int(screen_y) + 6)
                ])

class Drill:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = 'drill'
        self.health = 100
        self.max_health = 100
        self.size = 35
        self.cooldown = 0
        self.animation_timer = 0
        self.mining_progress = 0
        self.target_deposit = None
        self.mining_speed = 2
        self.range = 100
        self.output_conveyor = None
        
        self.config = {
            'color': (150, 100, 50),
            'health': 150,
            'cost': {'copper': 75, 'coal': 25},
            'range': 100,
            'mining_speed': 2
        }
        
        self.health = self.config['health']
        self.max_health = self.health
        self.range = self.config['range']
        self.mining_speed = self.config['mining_speed']
        
    def find_nearest_deposit(self, deposits):
        nearest = None
        min_distance = float('inf')
        
        for deposit in deposits:
            if deposit.amount <= 0:
                continue
                
            dx = deposit.x - self.x
            dy = deposit.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.range and distance < min_distance:
                min_distance = distance
                nearest = deposit
                
        return nearest
        
    def update(self, deposits, conveyors):
        self.animation_timer += 1
        self.target_deposit = self.find_nearest_deposit(deposits)
        
        if self.target_deposit:
            self.mining_progress += self.mining_speed / 60
            
            if self.mining_progress >= 1:
                self.mining_progress = 0
                
                resource_type = self.target_deposit.type
                self.target_deposit.amount -= 1
                
                if self.output_conveyor:
                    self.output_conveyor.add_item(resource_type)
                    return None, 0
                else:
                    return resource_type, 1
                
        return None, 0
        
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if -50 < screen_x < WINDOW_WIDTH + 50 and -50 < screen_y < WINDOW_HEIGHT + 50:
            pygame.draw.rect(screen, (100, 100, 110), 
                           (screen_x - 15, screen_y - 15, 30, 30))
            pygame.draw.rect(screen, (60, 60, 70), 
                           (screen_x - 15, screen_y - 15, 30, 30), 3)
            
            drill_animation = math.sin(self.animation_timer * 0.2) * 5
            drill_height = 20 + drill_animation
            
            pygame.draw.rect(screen, (150, 100, 50), 
                           (screen_x - 5, screen_y - 15 - drill_height, 10, drill_height))
            
            if self.target_deposit:
                pygame.draw.circle(screen, YELLOW, 
                                 (int(screen_x), int(screen_y - 15 - drill_height)), 8)
                pygame.draw.circle(screen, ORANGE, 
                                 (int(screen_x), int(screen_y - 15 - drill_height)), 5)
            else:
                pygame.draw.circle(screen, GRAY, 
                                 (int(screen_x), int(screen_y - 15 - drill_height)), 8)
            
            if self.target_deposit:
                pygame.draw.circle(screen, GREEN, (screen_x + 10, screen_y - 10), 4)
                
                progress_width = 20
                progress_height = 4
                progress_x = screen_x - progress_width // 2
                progress_y = screen_y + 18
                
                pygame.draw.rect(screen, (30, 30, 35), 
                               (progress_x, progress_y, progress_width, progress_height))
                pygame.draw.rect(screen, YELLOW, 
                               (progress_x, progress_y, 
                                progress_width * self.mining_progress, progress_height))
            else:
                pygame.draw.circle(screen, RED, (screen_x + 10, screen_y - 10), 4)

class Building:
    def __init__(self, x, y, building_type):
        self.x = x
        self.y = y
        self.type = building_type
        self.health = 100
        self.max_health = 100
        self.size = 30
        self.cooldown = 0
        self.animation_timer = 0
        
        # Настройки для разных типов зданий
        self.config = {
            'core': {'color': (0, 200, 255), 'health': 500, 'cost': {}, 'size': 40},
            'turret': {'color': (255, 100, 100), 'health': 200, 'cost': {'copper': 50}, 'range': 150, 'damage': 10, 'fire_rate': 30, 'size': 30},
            'trio': {'color': (255, 150, 50), 'health': 250, 'cost': {'copper': 75, 'coal': 25}, 'range': 170, 'damage': 8, 'fire_rate': 40, 'size': 35},
            'factory': {'color': (100, 255, 100), 'health': 150, 'cost': {'copper': 100, 'coal': 50}, 'production_type': 'copper', 'production': 5, 'size': 30},
            'coal_factory': {'color': (60, 60, 65), 'health': 150, 'cost': {'copper': 150, 'coal': 50}, 'production_type': 'coal', 'production': 3, 'size': 35},
            'titanium_factory': {'color': (180, 180, 220), 'health': 150, 'cost': {'copper': 200, 'coal': 100}, 'production_type': 'titanium', 'production': 2, 'size': 35},
            'thorium_factory': {'color': THORIUM_COLOR, 'health': 200, 'cost': {'copper': 300, 'coal': 150, 'titanium': 100}, 'production_type': 'thorium', 'production': 1, 'size': 40},
            'wall': {'color': (150, 150, 160), 'health': 400, 'cost': {'copper': 20}, 'size': 28},
            'drill': {'color': (150, 100, 50), 'health': 150, 'cost': {'copper': 75, 'coal': 25}, 'size': 35}
        }
        
        self.health = self.config[building_type]['health']
        self.max_health = self.health
        self.size = self.config[building_type]['size']
        
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if -50 < screen_x < WINDOW_WIDTH + 50 and -50 < screen_y < WINDOW_HEIGHT + 50:
            config = self.config[self.type]
            self.animation_timer += 1
            
            if self.type == 'core':
                pulse = math.sin(self.animation_timer * 0.05) * 10
                glow_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (0, 200, 255, 50), (50, 50), 50 + pulse)
                screen.blit(glow_surf, (screen_x - 50, screen_y - 50))
                
                points = []
                for i in range(6):
                    angle = math.pi / 3 * i + self.animation_timer * 0.01
                    px = screen_x + math.cos(angle) * 35
                    py = screen_y + math.sin(angle) * 35
                    points.append((px, py))
                pygame.draw.polygon(screen, config['color'], points)
                pygame.draw.polygon(screen, WHITE, points, 3)
                
                inner_points = []
                for i in range(6):
                    angle = math.pi / 3 * i - self.animation_timer * 0.01
                    px = screen_x + math.cos(angle) * 20
                    py = screen_y + math.sin(angle) * 20
                    inner_points.append((px, py))
                pygame.draw.polygon(screen, CYAN, inner_points)
                
            elif self.type in ['turret', 'trio']:
                pygame.draw.circle(screen, (60, 60, 70), (screen_x, screen_y), self.size)
                pygame.draw.circle(screen, config['color'], (screen_x, screen_y), self.size - 5)
                
                if self.cooldown > 0:
                    angle = self.animation_timer * 0.2
                else:
                    angle = 0
                
                if self.type == 'trio':
                    for offset in [-15, 0, 15]:
                        end_x = screen_x + math.cos(angle + offset * 0.1) * (self.size - 5)
                        end_y = screen_y + math.sin(angle + offset * 0.1) * (self.size - 5)
                        pygame.draw.line(screen, DARK_GRAY, (screen_x, screen_y), (end_x, end_y), 4)
                else:
                    end_x = screen_x + math.cos(angle) * (self.size - 5)
                    end_y = screen_y + math.sin(angle) * (self.size - 5)
                    pygame.draw.line(screen, DARK_GRAY, (screen_x, screen_y), (end_x, end_y), 6)
                
                pygame.draw.circle(screen, (80, 80, 90), (screen_x, screen_y), 10)
                pygame.draw.circle(screen, YELLOW, (screen_x, screen_y), 4)
                
            elif self.type in ['factory', 'coal_factory', 'titanium_factory', 'thorium_factory']:
                pulse = math.sin(self.animation_timer * 0.1) * 3
                
                if self.type == 'thorium_factory':
                    pygame.draw.rect(screen, config['color'], 
                                   (screen_x - 20 - pulse, screen_y - 20 - pulse, 
                                    40 + pulse * 2, 40 + pulse * 2))
                    pygame.draw.rect(screen, PURPLE, 
                                   (screen_x - 20 - pulse, screen_y - 20 - pulse, 
                                    40 + pulse * 2, 40 + pulse * 2), 3)
                    
                    glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (150, 0, 255, 40), (30, 30), 30)
                    screen.blit(glow_surf, (screen_x - 30, screen_y - 30))
                else:
                    pygame.draw.rect(screen, config['color'], 
                                   (screen_x - 15 - pulse, screen_y - 15 - pulse, 
                                    30 + pulse * 2, 30 + pulse * 2))
                    pygame.draw.rect(screen, DARK_GREEN, 
                                   (screen_x - 15 - pulse, screen_y - 15 - pulse, 
                                    30 + pulse * 2, 30 + pulse * 2), 3)
                
                if self.animation_timer % 30 < 15:
                    smoke_y = screen_y - 20 - (self.animation_timer % 30) * 2
                    smoke_alpha = 100 - (self.animation_timer % 30) * 3
                    smoke_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                    pygame.draw.circle(smoke_surf, (150, 150, 150, smoke_alpha), (10, 10), 8)
                    screen.blit(smoke_surf, (screen_x - 10, smoke_y))
                
                pygame.draw.rect(screen, DARK_GRAY, (screen_x - 12, screen_y + 5, 24, 6))
                moving_stripe = (self.animation_timer * 2) % 24 - 12
                pygame.draw.rect(screen, YELLOW, (screen_x + moving_stripe, screen_y + 6, 4, 4))
                
            elif self.type == 'wall':
                pygame.draw.rect(screen, config['color'], 
                               (screen_x - 14, screen_y - 14, 28, 28))
                
                for dx, dy in [(-10, -10), (10, -10), (-10, 10), (10, 10)]:
                    pygame.draw.circle(screen, DARK_GRAY, (screen_x + dx, screen_y + dy), 3)
                    pygame.draw.circle(screen, LIGHT_GRAY, (screen_x + dx, screen_y + dy), 2)
                
                if self.health < self.max_health * 0.5:
                    crack_points = [
                        (screen_x - 8, screen_y - 8),
                        (screen_x - 3, screen_y + 2),
                        (screen_x + 2, screen_y - 5),
                        (screen_x + 8, screen_y + 6)
                    ]
                    pygame.draw.lines(screen, DARK_GRAY, False, crack_points, 2)
            
            elif self.type == 'drill':
                pygame.draw.rect(screen, (100, 100, 110), 
                               (screen_x - 15, screen_y - 15, 30, 30))
                pygame.draw.rect(screen, (60, 60, 70), 
                               (screen_x - 15, screen_y - 15, 30, 30), 3)
                
                drill_animation = math.sin(self.animation_timer * 0.2) * 5
                drill_height = 20 + drill_animation
                
                pygame.draw.rect(screen, (150, 100, 50), 
                               (screen_x - 5, screen_y - 15 - drill_height, 10, drill_height))
                
                pygame.draw.circle(screen, GRAY, 
                                 (int(screen_x), int(screen_y - 15 - drill_height)), 8)
            
            if self.health < self.max_health:
                bar_width = 40
                bar_height = 6
                bar_x = screen_x - bar_width // 2
                bar_y = screen_y - self.size - 15
                
                pygame.draw.rect(screen, (30, 30, 35), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
                
                health_ratio = self.health / self.max_health
                health_color = GREEN if health_ratio > 0.5 else (YELLOW if health_ratio > 0.25 else RED)
                
                pygame.draw.rect(screen, health_color, (bar_x, bar_y, bar_width * health_ratio, bar_height))
                pygame.draw.rect(screen, (255, 255, 255, 50), (bar_x, bar_y, bar_width * health_ratio, bar_height // 2))

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.speed = 1.5 if enemy_type == 'basic' else 0.7
        self.health = 50 if enemy_type == 'basic' else 150
        self.max_health = self.health
        self.damage = 10 if enemy_type == 'basic' else 25
        self.size = 15 if enemy_type == 'basic' else 25
        self.attack_cooldown = 0
        self.animation_timer = random.uniform(0, math.pi * 2)
        
    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if -50 < screen_x < WINDOW_WIDTH + 50 and -50 < screen_y < WINDOW_HEIGHT + 50:
            self.animation_timer += 0.1
            
            if self.type == 'basic':
                bob = math.sin(self.animation_timer * 3) * 3
                
                glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 50, 50, 40), (20, 20), 20)
                screen.blit(glow_surf, (screen_x - 20, screen_y - 20 + bob))
                
                pygame.draw.circle(screen, (200, 50, 50), (screen_x, screen_y + bob), self.size)
                pygame.draw.circle(screen, (255, 100, 100), (screen_x, screen_y + bob), self.size - 3)
                
                pygame.draw.circle(screen, RED, (screen_x, screen_y + bob), 5)
                pygame.draw.circle(screen, YELLOW, (screen_x, screen_y + bob), 2)
                
            else:
                track_offset = math.sin(self.animation_timer * 5) * 2
                pygame.draw.rect(screen, (50, 50, 55), 
                               (screen_x - self.size, screen_y - self.size + track_offset, 
                                self.size * 2, self.size * 2))
                
                pygame.draw.rect(screen, (180, 40, 40), 
                               (screen_x - self.size + 3, screen_y - self.size + 3, 
                                self.size * 2 - 6, self.size * 2 - 6))
                
                pygame.draw.circle(screen, (220, 60, 60), (screen_x, screen_y), self.size * 0.8)
                
                angle = math.atan2(self.y - camera_y, self.x - camera_x)
                end_x = screen_x + math.cos(angle) * self.size * 1.3
                end_y = screen_y + math.sin(angle) * self.size * 1.3
                pygame.draw.line(screen, (40, 40, 45), (screen_x, screen_y), (end_x, end_y), 5)
            
            if self.health < self.max_health:
                bar_width = 30
                bar_height = 5
                bar_x = screen_x - bar_width // 2
                bar_y = screen_y - self.size - 15
                
                pygame.draw.rect(screen, (30, 30, 35), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
                
                health_ratio = self.health / self.max_health
                health_color = GREEN if health_ratio > 0.5 else (YELLOW if health_ratio > 0.25 else RED)
                pygame.draw.rect(screen, health_color, (bar_x, bar_y, bar_width * health_ratio, bar_height))

class Bullet:
    def __init__(self, x, y, target_x, target_y, damage):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = 10
        self.size = 4
        self.trail = []
        
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.dx = dx / distance
            self.dy = dy / distance
        else:
            self.dx = 0
            self.dy = 0
            
    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
            
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        
    def draw(self, screen, camera_x, camera_y):
        for i, (tx, ty) in enumerate(self.trail):
            screen_tx = tx - camera_x
            screen_ty = ty - camera_y
            alpha = int(255 * (i / len(self.trail)))
            pygame.draw.circle(screen, (255, 200, 50), 
                             (int(screen_tx), int(screen_ty)), max(1, self.size * i // len(self.trail)))
        
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        pygame.draw.circle(screen, YELLOW, (int(screen_x), int(screen_y)), self.size)
        pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), self.size - 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Mini Mindustry - С консолью")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 36)
        
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 12
        
        # Ресурсы игрока
        self.copper = 500
        self.coal = 300
        self.titanium = 150
        self.thorium = 0
        
        self.buildings = []
        self.enemies = []
        self.bullets = []
        self.resources = []
        self.particles = []
        self.drills = []
        self.conveyors = []
        
        self.core = Building(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 'core')
        self.buildings.append(self.core)
        
        self.generate_resources()
        
        self.build_mode = None
        self.selected_building = None
        self.current_category = 'turrets'
        self.conveyor_direction = 'right'
        
        self.wave = 0
        self.enemy_spawn_timer = 0
        self.enemies_to_spawn = 0
        
        self.start_wave()
        
        # Запускаем консоль в отдельном потоке
        self.console_thread = threading.Thread(target=self.console_commands, daemon=True)
        self.console_thread.start()
        
    def console_commands(self):
        """Обработка консольных команд"""
        while True:
            try:
                command = input("Введите команду: ").strip().lower()
                
                if command.startswith("give "):
                    parts = command.split()
                    if len(parts) >= 3:
                        resource = parts[1]
                        try:
                            amount = int(parts[2])
                            self.give_resource(resource, amount)
                        except ValueError:
                            print("Ошибка: количество должно быть числом")
                    else:
                        print("Использование: give <ресурс> <количество>")
                        
                elif command == "gameover":
                    print("Игра завершена!")
                    self.core.health = 0
                    
                elif command.startswith("summon "):
                    parts = command.split()
                    if len(parts) >= 2:
                        enemy_type = parts[1]
                        self.summon_enemy(enemy_type)
                    else:
                        print("Использование: summon <тип врага>")
                        
                elif command == "help":
                    print("Доступные команды:")
                    print("  give <ресурс> <количество> - выдать ресурс (copper, coal, titanium, thorium)")
                    print("  gameover - завершить игру")
                    print("  summon <тип врага> - призвать врага (basic, tank)")
                    print("  help - показать справку")
                    
                else:
                    print("Неизвестная команда. Введите 'help' для справки.")
                    
            except Exception as e:
                print(f"Ошибка: {e}")
                
    def give_resource(self, resource, amount):
        """Выдача ресурсов игроку"""
        resource_names = {
            'copper': 'copper',
            'coal': 'coal',
            'titanium': 'titanium',
            'thorium': 'thorium',
            'медь': 'copper',
            'уголь': 'coal',
            'титан': 'titanium',
            'торий': 'thorium'
        }
        
        if resource in resource_names:
            resource_type = resource_names[resource]
            if resource_type == 'copper':
                self.copper += amount
                print(f"Выдано {amount} меди. Теперь у вас {self.copper} меди.")
            elif resource_type == 'coal':
                self.coal += amount
                print(f"Выдано {amount} угля. Теперь у вас {self.coal} угля.")
            elif resource_type == 'titanium':
                self.titanium += amount
                print(f"Выдано {amount} титана. Теперь у вас {self.titanium} титана.")
            elif resource_type == 'thorium':
                self.thorium += amount
                print(f"Выдано {amount} тория. Теперь у вас {self.thorium} тория.")
        else:
            print(f"Неизвестный ресурс: {resource}")
            print("Доступные ресурсы: copper, coal, titanium, thorium")
            
    def summon_enemy(self, enemy_type):
        """Призыв врага"""
        enemy_names = {
            'basic': 'basic',
            'tank': 'tank',
            'обычный': 'basic',
            'танк': 'tank'
        }
        
        if enemy_type in enemy_names:
            actual_type = enemy_names[enemy_type]
            # Спавним врага рядом с ядром
            x = self.core.x + random.randint(-200, 200)
            y = self.core.y + random.randint(-200, 200)
            self.enemies.append(Enemy(x, y, actual_type))
            print(f"Призван враг типа '{actual_type}' на позиции ({x}, {y})")
        else:
            print(f"Неизвестный тип врага: {enemy_type}")
            print("Доступные типы: basic, tank")
        
    def generate_resources(self):
        resource_types = ['copper', 'coal', 'titanium']
        
        for _ in range(20):
            cluster_x = random.randint(100, WINDOW_WIDTH * 4)
            cluster_y = random.randint(100, WINDOW_HEIGHT * 4)
            resource_type = random.choice(resource_types)
            
            for _ in range(random.randint(3, 6)):
                offset_x = random.randint(-100, 100)
                offset_y = random.randint(-100, 100)
                deposit = ResourceDeposit(cluster_x + offset_x, cluster_y + offset_y, resource_type)
                self.resources.append(deposit)
        
    def start_wave(self):
        self.wave += 1
        self.enemies_to_spawn = 5 + self.wave * 2
        self.enemy_spawn_timer = 0
        
    def spawn_enemy(self):
        side = random.randint(0, 3)
        if side == 0:
            x = random.randint(0, WINDOW_WIDTH * 4)
            y = -50
        elif side == 1:
            x = random.randint(0, WINDOW_WIDTH * 4)
            y = WINDOW_HEIGHT * 4 + 50
        elif side == 2:
            x = -50
            y = random.randint(0, WINDOW_HEIGHT * 4)
        else:
            x = WINDOW_WIDTH * 4 + 50
            y = random.randint(0, WINDOW_HEIGHT * 4)
            
        enemy_type = 'basic' if self.wave < 3 else random.choice(['basic', 'tank'])
        self.enemies.append(Enemy(x, y, enemy_type))
        
    def create_particles(self, x, y, color, count=10):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(2, 5)
            lifetime = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, velocity, size, lifetime))
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                # Переключение разделов
                if event.key == pygame.K_1:
                    self.current_category = 'turrets'
                    self.build_mode = None
                elif event.key == pygame.K_2:
                    self.current_category = 'factories'
                    self.build_mode = None
                elif event.key == pygame.K_3:
                    self.current_category = 'armor'
                    self.build_mode = None
                elif event.key == pygame.K_4:
                    self.current_category = 'logistics'
                    self.build_mode = None
                elif event.key == pygame.K_ESCAPE:
                    self.build_mode = None
                    
                # Выбор здания в текущем разделе
                if self.current_category == 'turrets':
                    if event.key == pygame.K_t:
                        self.build_mode = 'turret'
                    elif event.key == pygame.K_y:
                        self.build_mode = 'trio'
                elif self.current_category == 'factories':
                    if event.key == pygame.K_f:
                        self.build_mode = 'factory'
                    elif event.key == pygame.K_d:
                        self.build_mode = 'drill'
                    elif event.key == pygame.K_c:
                        self.build_mode = 'coal_factory'
                    elif event.key == pygame.K_v:
                        self.build_mode = 'titanium_factory'
                    elif event.key == pygame.K_b:
                        self.build_mode = 'thorium_factory'
                elif self.current_category == 'armor':
                    if event.key == pygame.K_w:
                        self.build_mode = 'wall'
                elif self.current_category == 'logistics':
                    if event.key == pygame.K_c:
                        self.build_mode = 'conveyor'
                    elif event.key == pygame.K_r:
                        directions = ['right', 'down', 'left', 'up']
                        current_index = directions.index(self.conveyor_direction)
                        self.conveyor_direction = directions[(current_index + 1) % 4]
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.build_mode:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        world_x = mouse_x + self.camera_x
                        world_y = mouse_y + self.camera_y
                        
                        cost = self.get_building_cost(self.build_mode)
                        if self.can_afford(cost):
                            if self.build_mode == 'drill':
                                drill = Drill(world_x, world_y)
                                self.drills.append(drill)
                                self.buildings.append(drill)
                            elif self.build_mode == 'conveyor':
                                conveyor = Conveyor(world_x, world_y, self.conveyor_direction)
                                self.conveyors.append(conveyor)
                            else:
                                self.buildings.append(Building(world_x, world_y, self.build_mode))
                            
                            self.pay_cost(cost)
                            self.create_particles(world_x, world_y, (100, 255, 100), 15)
                            
                elif event.button == 3:
                    self.build_mode = None
                    
    def get_building_cost(self, building_type):
        costs = {
            'turret': {'copper': 50},
            'trio': {'copper': 75, 'coal': 25},
            'factory': {'copper': 100, 'coal': 50},
            'coal_factory': {'copper': 150, 'coal': 50},
            'titanium_factory': {'copper': 200, 'coal': 100},
            'thorium_factory': {'copper': 300, 'coal': 150, 'titanium': 100},
            'wall': {'copper': 20},
            'drill': {'copper': 75, 'coal': 25},
            'conveyor': {'copper': 25}
        }
        return costs.get(building_type, {})
        
    def can_afford(self, cost):
        if cost.get('copper', 0) > self.copper:
            return False
        if cost.get('coal', 0) > self.coal:
            return False
        if cost.get('titanium', 0) > self.titanium:
            return False
        if cost.get('thorium', 0) > self.thorium:
            return False
        return True
        
    def pay_cost(self, cost):
        self.copper -= cost.get('copper', 0)
        self.coal -= cost.get('coal', 0)
        self.titanium -= cost.get('titanium', 0)
        self.thorium -= cost.get('thorium', 0)
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera_x -= self.camera_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x += self.camera_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera_y -= self.camera_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y += self.camera_speed
            
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
                
        # Обновление буров
        for drill in self.drills[:]:
            if not drill.output_conveyor:
                for conveyor in self.conveyors:
                    dx = abs(conveyor.x - drill.x)
                    dy = abs(conveyor.y - drill.y)
                    if dx <= 35 and dy <= 35:
                        drill.output_conveyor = conveyor
                        break
                        
            resource_type, amount = drill.update(self.resources, self.conveyors)
            
            if resource_type and amount > 0:
                if resource_type == 'copper':
                    self.copper += amount
                elif resource_type == 'coal':
                    self.coal += amount
                elif resource_type == 'titanium':
                    self.titanium += amount
                    
        # Обновление конвейеров
        for conveyor in self.conveyors[:]:
            resource_type, amount = conveyor.update(self.conveyors, self.buildings)
            
            if resource_type and amount > 0:
                if resource_type == 'copper':
                    self.copper += amount
                elif resource_type == 'coal':
                    self.coal += amount
                elif resource_type == 'titanium':
                    self.titanium += amount
                    
        # Спавн врагов
        if self.enemies_to_spawn > 0:
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= 60:
                self.spawn_enemy()
                self.enemies_to_spawn -= 1
                self.enemy_spawn_timer = 0
                
        # Обновление турелей
        for building in self.buildings:
            if building.type in ['turret', 'trio']:
                if building.cooldown > 0:
                    building.cooldown -= 1
                    
                nearest_enemy = None
                min_distance = float('inf')
                
                for enemy in self.enemies:
                    dx = enemy.x - building.x
                    dy = enemy.y - building.y
                    distance = math.sqrt(dx**2 + dy**2)
                    
                    if distance < building.config[building.type]['range'] and distance < min_distance:
                        min_distance = distance
                        nearest_enemy = enemy
                        
                if nearest_enemy and building.cooldown <= 0:
                    if building.type == 'trio':
                        for angle_offset in [-10, 0, 10]:
                            angle = math.atan2(nearest_enemy.y - building.y, 
                                             nearest_enemy.x - building.x) + math.radians(angle_offset)
                            target_x = building.x + math.cos(angle) * 100
                            target_y = building.y + math.sin(angle) * 100
                            self.bullets.append(Bullet(building.x, building.y, 
                                                      target_x, target_y,
                                                      building.config[building.type]['damage']))
                    else:
                        self.bullets.append(Bullet(building.x, building.y, 
                                                  nearest_enemy.x, nearest_enemy.y,
                                                  building.config[building.type]['damage']))
                    
                    building.cooldown = building.config[building.type]['fire_rate']
                    self.create_particles(building.x, building.y, (255, 200, 50), 5)
                    
            elif building.type in ['factory', 'coal_factory', 'titanium_factory', 'thorium_factory']:
                if pygame.time.get_ticks() % 1000 < 50:
                    if building.type == 'factory':
                        self.copper += 5
                        self.create_particles(building.x, building.y, (255, 170, 60), 3)
                    elif building.type == 'coal_factory':
                        self.coal += 3
                        self.create_particles(building.x, building.y, (60, 60, 65), 3)
                    elif building.type == 'titanium_factory':
                        self.titanium += 2
                        self.create_particles(building.x, building.y, (180, 180, 220), 3)
                    elif building.type == 'thorium_factory':
                        if self.copper >= 5:
                            self.copper -= 5
                            self.thorium += 1
                            self.create_particles(building.x, building.y, THORIUM_COLOR, 5)
                    
        # Обновление врагов
        for enemy in self.enemies[:]:
            enemy.move_towards(self.core.x, self.core.y)
            
            dx = enemy.x - self.core.x
            dy = enemy.y - self.core.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 40:
                if enemy.attack_cooldown <= 0:
                    self.core.health -= enemy.damage
                    enemy.attack_cooldown = 60
                    self.create_particles(self.core.x, self.core.y, (255, 50, 50), 20)
                    
            if enemy.attack_cooldown > 0:
                enemy.attack_cooldown -= 1
                
            if enemy.health <= 0:
                self.create_particles(enemy.x, enemy.y, (255, 100, 100), 20)
                self.enemies.remove(enemy)
                self.copper += 10
                
        # Обновление пуль
        for bullet in self.bullets[:]:
            bullet.update()
            
            for enemy in self.enemies:
                dx = bullet.x - enemy.x
                dy = bullet.y - enemy.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < enemy.size + bullet.size:
                    enemy.health -= bullet.damage
                    self.create_particles(bullet.x, bullet.y, (255, 255, 100), 10)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
                    
            if (bullet.x < self.camera_x - 100 or bullet.x > self.camera_x + WINDOW_WIDTH + 100 or
                bullet.y < self.camera_y - 100 or bullet.y > self.camera_y + WINDOW_HEIGHT + 100):
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                    
        # Проверка окончания волны
        if self.enemies_to_spawn == 0 and len(self.enemies) == 0:
            self.start_wave()
            self.copper += 50
            self.create_particles(self.core.x, self.core.y, (255, 220, 50), 30)
            
        # Проверка поражения
        if self.core.health <= 0:
            self.game_over()
            
    def game_over(self):
        print("Игра окончена! Нажмите Enter для перезапуска...")
        self.__init__()
        
    def draw_grid(self):
        grid_size = 50
        start_x = (self.camera_x // grid_size) * grid_size
        start_y = (self.camera_y // grid_size) * grid_size
        
        for x in range(int(start_x), int(start_x + WINDOW_WIDTH + grid_size), grid_size):
            screen_x = x - self.camera_x
            pygame.draw.line(self.screen, (30, 30, 40), (screen_x, 0), (screen_x, WINDOW_HEIGHT), 1)
            
        for y in range(int(start_y), int(start_y + WINDOW_HEIGHT + grid_size), grid_size):
            screen_y = y - self.camera_y
            pygame.draw.line(self.screen, (30, 30, 40), (0, screen_y), (WINDOW_WIDTH, screen_y), 1)
            
    def draw_ui(self):
        # Панель ресурсов
        panel_surf = pygame.Surface((WINDOW_WIDTH, 40))
        for i in range(40):
            alpha = 200 - i * 3
            pygame.draw.line(panel_surf, (30, 30, 40, alpha), (0, i), (WINDOW_WIDTH, i))
        self.screen.blit(panel_surf, (0, 0))
        
        resources_text = f"Медь: {self.copper}  Уголь: {self.coal}  Титан: {self.titanium}  Торий: {self.thorium}  Волна: {self.wave}"
        text_surface = self.font.render(resources_text, True, WHITE)
        self.screen.blit(text_surface, (15, 10))
        
        # Панель строительства
        build_panel = pygame.Surface((WINDOW_WIDTH, 150))
        build_panel.fill((25, 25, 35))
        build_panel.set_alpha(230)
        self.screen.blit(build_panel, (0, WINDOW_HEIGHT - 150))
        
        # Разделы
        categories = [
            ("1 - Турели", 'turrets', (255, 100, 100)),
            ("2 - Заводы", 'factories', (100, 255, 100)),
            ("3 - Броня", 'armor', (150, 150, 160)),
            ("4 - Логистика", 'logistics', (255, 200, 50))
        ]
        
        tab_width = 180
        tab_height = 30
        tab_y = WINDOW_HEIGHT - 150
        
        for i, (text, category, color) in enumerate(categories):
            tab_x = 10 + i * (tab_width + 10)
            
            if self.current_category == category:
                pygame.draw.rect(self.screen, (60, 60, 80), (tab_x, tab_y, tab_width, tab_height))
                pygame.draw.rect(self.screen, color, (tab_x, tab_y, tab_width, tab_height), 2)
            else:
                pygame.draw.rect(self.screen, (40, 40, 50), (tab_x, tab_y, tab_width, tab_height))
            
            text_surface = self.small_font.render(text, True, WHITE if self.current_category == category else GRAY)
            text_rect = text_surface.get_rect(center=(tab_x + tab_width // 2, tab_y + tab_height // 2))
            self.screen.blit(text_surface, text_rect)
        
        # Здания в текущем разделе
        buildings_y = WINDOW_HEIGHT - 115
        
        if self.current_category == 'turrets':
            building_info = [
                ("Турель", 'turret', (255, 100, 100), "T"),
                ("Трио", 'trio', (255, 150, 50), "Y")
            ]
        elif self.current_category == 'factories':
            building_info = [
                ("Фабрика меди", 'factory', (100, 255, 100), "F"),
                ("Бур", 'drill', (150, 100, 50), "D"),
                ("Завод угля", 'coal_factory', (60, 60, 65), "C"),
                ("Завод титана", 'titanium_factory', (180, 180, 220), "V"),
                ("Ториевый завод", 'thorium_factory', THORIUM_COLOR, "B")
            ]
        elif self.current_category == 'armor':
            building_info = [
                ("Стена", 'wall', (150, 150, 160), "W")
            ]
        elif self.current_category == 'logistics':
            building_info = [
                ("Конвейер", 'conveyor', (255, 200, 50), "C"),
                ("Поворот", None, None, "R")
            ]
        else:
            building_info = []
        
        x_offset = 20
        for name, building_type, color, hotkey in building_info:
            if self.build_mode == building_type:
                pygame.draw.rect(self.screen, (80, 80, 100), 
                               (x_offset - 5, buildings_y - 5, 150, 40))
            
            if building_type == 'conveyor':
                pygame.draw.rect(self.screen, color, (x_offset + 5, buildings_y + 5, 15, 15))
            elif building_type and color:
                pygame.draw.rect(self.screen, color, (x_offset + 5, buildings_y + 5, 15, 15))
            
            name_surface = self.small_font.render(f"{name} [{hotkey}]", True, 
                                                 WHITE if self.build_mode == building_type else LIGHT_GRAY)
            self.screen.blit(name_surface, (x_offset + 25, buildings_y + 5))
            
            x_offset += 160
        
        # Показываем рецепт только когда выбрано здание
        if self.build_mode:
            cost = self.get_building_cost(self.build_mode)
            recipe_text = "Требуется: "
            parts = []
            if 'copper' in cost:
                parts.append(f"{cost['copper']} меди")
            if 'coal' in cost:
                parts.append(f"{cost['coal']} угля")
            if 'titanium' in cost:
                parts.append(f"{cost['titanium']} титана")
            if 'thorium' in cost:
                parts.append(f"{cost['thorium']} тория")
            
            recipe_text += ", ".join(parts)
            
            recipe_surface = self.small_font.render(recipe_text, True, YELLOW)
            recipe_rect = recipe_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 15))
            self.screen.blit(recipe_surface, recipe_rect)
            
            build_text = f"ЛКМ - построить, ПКМ - отменить"
            build_surface = self.small_font.render(build_text, True, GREEN)
            self.screen.blit(build_surface, (15, 45))
            
        # Здоровье ядра
        health_ratio = self.core.health / self.core.max_health
        health_color = GREEN if health_ratio > 0.5 else (YELLOW if health_ratio > 0.25 else RED)
        
        health_bar_width = 200
        health_bar_height = 15
        health_bar_x = WINDOW_WIDTH - health_bar_width - 20
        health_bar_y = 10
        
        pygame.draw.rect(self.screen, (30, 30, 35), 
                        (health_bar_x - 2, health_bar_y - 2, 
                         health_bar_width + 4, health_bar_height + 4))
        pygame.draw.rect(self.screen, health_color, 
                        (health_bar_x, health_bar_y, 
                         health_bar_width * health_ratio, health_bar_height))
        
        health_text = f"Ядро: {self.core.health}/{self.core.max_health}"
        text_surface = self.small_font.render(health_text, True, WHITE)
        self.screen.blit(text_surface, (health_bar_x, health_bar_y + 20))
        
    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        
        for resource in self.resources:
            resource.draw(self.screen, self.camera_x, self.camera_y)
            
        for conveyor in self.conveyors:
            conveyor.draw(self.screen, self.camera_x, self.camera_y)
            
        for building in self.buildings:
            building.draw(self.screen, self.camera_x, self.camera_y)
            
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x, self.camera_y)
            
        for bullet in self.bullets:
            bullet.draw(self.screen, self.camera_x, self.camera_y)
            
        for particle in self.particles:
            particle.draw(self.screen, self.camera_x, self.camera_y)
            
        self.draw_ui()
        
        pygame.display.flip()
        
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
