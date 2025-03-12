import pygame
import random
import math
from constants import WeaponType, WHITE, RED, GOLD, SCREEN_WIDTH, SCREEN_HEIGHT

class Weapon:
    def __init__(self, weapon_type, level=1):
        self.type = weapon_type
        self.level = level
        self.cooldown = 0
        self.projectiles = []

        # Set properties based on weapon type
        if weapon_type == WeaponType.KNIFE:
            self.base_cooldown = 30
            self.damage = 10
            self.speed = 8
            self.penetration = 1
            self.size = 10
        elif weapon_type == WeaponType.AXE:
            self.base_cooldown = 90
            self.damage = 30
            self.speed = 6
            self.penetration = 2
            self.size = 15
        elif weapon_type == WeaponType.MAGIC:
            self.base_cooldown = 60
            self.damage = 20
            self.speed = 5
            self.penetration = 3
            self.size = 20

        # Apply level bonuses
        if level > 1:
            self.apply_level_bonuses()

    def apply_level_bonuses(self):
        level_bonus = (self.level - 1) * 0.2  # 20% increase per level
        self.damage = int(self.damage * (1 + level_bonus))
        self.penetration += int((self.level - 1) / 2)
        self.base_cooldown = max(10, int(self.base_cooldown * (1 - level_bonus * 0.5)))
        self.size += int((self.level - 1) * 2)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def can_attack(self):
        return self.cooldown <= 0

    def attack(self, x, y, target_enemies):
        self.cooldown = self.base_cooldown

        if self.type == WeaponType.KNIFE:
            # Find closest enemy
            closest_enemy = None
            min_dist = float('inf')

            for enemy in target_enemies:
                dist = math.sqrt((enemy.x - x) ** 2 + (enemy.y - y) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    closest_enemy = enemy

            if closest_enemy:
                dx = closest_enemy.x - x
                dy = closest_enemy.y - y
                angle = math.atan2(dy, dx)

                self.projectiles.append({
                    'x': x,
                    'y': y,
                    'dx': math.cos(angle) * self.speed,
                    'dy': math.sin(angle) * self.speed,
                    'damage': self.damage,
                    'penetration': self.penetration,
                    'size': self.size,
                    'hits': []
                })
            # Fallback if no enemies
            elif len(self.projectiles) < 10:  # Limit number of projectiles
                angle = random.uniform(0, 2 * math.pi)
                self.projectiles.append({
                    'x': x,
                    'y': y,
                    'dx': math.cos(angle) * self.speed,
                    'dy': math.sin(angle) * self.speed,
                    'damage': self.damage,
                    'penetration': self.penetration,
                    'size': self.size,
                    'hits': []
                })

        elif self.type == WeaponType.AXE:
            # Throw in 4 directions
            for angle in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
                self.projectiles.append({
                    'x': x,
                    'y': y,
                    'dx': math.cos(angle) * self.speed,
                    'dy': math.sin(angle) * self.speed,
                    'damage': self.damage,
                    'penetration': self.penetration,
                    'size': self.size,
                    'hits': []
                })

        elif self.type == WeaponType.MAGIC:
            # Create projectiles in a circle
            num_projectiles = min(3 + self.level, 8)
            angle_step = 2 * math.pi / num_projectiles

            for i in range(num_projectiles):
                angle = i * angle_step
                self.projectiles.append({
                    'x': x,
                    'y': y,
                    'dx': math.cos(angle) * self.speed,
                    'dy': math.sin(angle) * self.speed,
                    'damage': self.damage,
                    'penetration': self.penetration,
                    'size': self.size,
                    'hits': []
                })

    def draw_projectiles(self, screen):
        for p in self.projectiles:
            if self.type == WeaponType.KNIFE:
                color = WHITE
                pygame.draw.rect(screen, color, (p['x'] - p['size'] / 2, p['y'] - p['size'] / 2, p['size'], p['size']))
            elif self.type == WeaponType.AXE:
                color = RED
                pygame.draw.rect(screen, color, (p['x'] - p['size'] / 2, p['y'] - p['size'] / 2, p['size'], p['size']))
            elif self.type == WeaponType.MAGIC:
                color = GOLD
                pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), int(p['size'] / 2))

    def update_projectiles(self):
        for p in self.projectiles[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']

            # Remove if out of bounds
            if (p['x'] < -50 or p['x'] > SCREEN_WIDTH + 50 or
                    p['y'] < -50 or p['y'] > SCREEN_HEIGHT + 50):
                if p in self.projectiles:
                    self.projectiles.remove(p)

    def check_collisions(self, enemies):
        for p in self.projectiles[:]:
            for enemy in enemies:
                if enemy not in p['hits']:  # Check if we already hit this enemy
                    dx = p['x'] - enemy.x
                    dy = p['y'] - enemy.y
                    distance = math.sqrt(dx * dx + dy * dy)

                    if distance < (p['size'] / 2 + enemy.size / 2):
                        enemy.take_damage(p['damage'])
                        p['hits'].append(enemy)

                        # Remove projectile if penetration limit reached
                        if len(p['hits']) >= p['penetration']:
                            if p in self.projectiles:
                                self.projectiles.remove(p)
                            break
