import pygame
import random
import math
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, RED, BLUE, PURPLE, GREEN

class Enemy:
    def __init__(self, player_x, player_y, enemy_type=None):
        # Randomize spawn location outside the screen but not too far
        side = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left

        if side == 0:  # Top
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = -20
        elif side == 1:  # Right
            self.x = SCREEN_WIDTH + 20
            self.y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # Bottom
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = SCREEN_HEIGHT + 20
        else:  # Left
            self.x = -20
            self.y = random.randint(0, SCREEN_HEIGHT)

        # Enemy type (if not specified, choose randomly with weights)
        if enemy_type is None:
            # As player progresses, different enemies have different spawn chances
            enemy_types = ['basic', 'fast', 'tank']
            weights = [0.7, 0.2, 0.1]  # Default weights
            enemy_type = random.choices(enemy_types, weights=weights)[0]

        self.type = enemy_type

        # Set properties based on type
        if enemy_type == 'basic':
            self.size = 15
            self.color = RED
            self.speed = 2
            self.health = 30
            self.max_health = 30
            self.damage = 10
            self.xp_value = 10
        elif enemy_type == 'fast':
            self.size = 10
            self.color = BLUE
            self.speed = 3.5
            self.health = 15
            self.max_health = 15
            self.damage = 5
            self.xp_value = 15
        elif enemy_type == 'tank':
            self.size = 25
            self.color = PURPLE
            self.speed = 1
            self.health = 80
            self.max_health = 80
            self.damage = 20
            self.xp_value = 25

        # 10% chance to drop a gem
        self.drops_gem = random.random() < 0.1

    def update(self, player_x, player_y):
        # Move towards player
        dx = player_x - self.x
        dy = player_y - self.y
        dist = max(0.1, math.sqrt(dx * dx + dy * dy))  # Avoid division by zero

        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

    def draw(self, screen):
        # Draw enemy
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

        # Draw health bar for bigger enemies
        if self.size >= 15:
            health_width = self.size * 2
            health_height = 3
            health_x = self.x - health_width / 2
            health_y = self.y - self.size - 5

            # Background (empty health)
            pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
            # Foreground (current health)
            current_health_width = (self.health / self.max_health) * health_width
            pygame.draw.rect(screen, GREEN, (health_x, health_y, current_health_width, health_height))

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True  # Enemy died
        return False

    def check_collision(self, player):
        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < (self.size + player.size):
            return True
        return False
