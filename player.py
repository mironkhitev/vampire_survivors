import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED, WHITE, RED, GREEN
from weapon import Weapon, WeaponType

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.size = 20
        self.color = WHITE
        self.speed = PLAYER_SPEED
        self.weapons = [Weapon(WeaponType.KNIFE), Weapon(WeaponType.AXE), Weapon(WeaponType.MAGIC)]
        self.max_health = 100
        self.active_weapon = self.weapons[0]
        self.health = 100
        self.level = 1
        self.xp = 0
        self.xp_to_level = 100
        self.kills = 0
        self.gems = 0
        self.invulnerable = 0  # Invulnerability frames
        self.levelup_points = 0

    def update(self, keys, enemies):
        # Movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y = max(self.y - self.speed, self.size)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y = min(self.y + self.speed, SCREEN_HEIGHT - self.size)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x = max(self.x - self.speed, self.size)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x = min(self.x + self.speed, SCREEN_WIDTH - self.size)

        # Weapon updates and attacks
        for weapon in self.weapons:
            weapon.update()
            if weapon == self.active_weapon and weapon.can_attack():
                weapon.attack(self.x, self.y, enemies)
            weapon.update_projectiles()
            weapon.check_collisions(enemies)

        # Update invulnerability frames
        if self.invulnerable > 0:
            self.invulnerable -= 1

    def draw(self, screen):
        # Draw player
        if self.invulnerable == 0 or self.invulnerable % 4 < 2:  # Flash when invulnerable
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

        # Draw weapons' projectiles
        for weapon in self.weapons:
            weapon.draw_projectiles(screen)

        # Draw health bar
        health_width = 50
        health_height = 5
        health_x = self.x - health_width // 2
        health_y = self.y - self.size - 10

        # Background (empty health)
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        # Foreground (current health)
        current_health_width = int((self.health / self.max_health) * health_width)
        pygame.draw.rect(screen, GREEN, (health_x, health_y, current_health_width, health_height))

    def take_damage(self, damage):
        if self.invulnerable <= 0:
            self.health -= damage
            self.invulnerable = 30  # Half second of invulnerability

            if self.health <= 0:
                self.health = 0
                return True  # Player died
        return False

    def add_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_level:
            return self.level_up()
        else:
            return False

    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_level
        self.xp_to_level = int(self.xp_to_level * 1.5)
        self.levelup_points += 1
        # Heal on level up
        self.max_health += 20
        self.health = self.max_health

        # Every 3 levels, get a new weapon or upgrade existing
        if self.level % 3 == 0:
            return True  # Signal to show upgrade menu
        return False

    def add_gem(self):
        self.gems += 1
        # Every 10 gems, get a health boost
        if self.gems % 10 == 0:
            self.max_health += 10
            self.health += 10

    def change_weapon(self, weapon_number):
        if len(self.weapons) >= weapon_number:
            self.active_weapon = self.weapons[weapon_number - 1]
