import pygame
import random
import math
from enum import Enum

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
ENEMY_SPAWN_RATE = 120  # Frames between enemy spawns
MAX_ENEMIES = 50
MIN_ENEMIES = 10
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vampire Survivors Clone")
clock = pygame.time.Clock()

# Font setup
font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 48)


class WeaponType(Enum):
    KNIFE = 1
    AXE = 2
    MAGIC = 3


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
        Game.paused = True
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


class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.game_over = False
        self.paused = False
        self.show_upgrade_menu = False
        self.upgrade_options = []
        self.time = 0  # Game time in frames
        self.difficulty_level = 1
        self.next_difficulty_time = 30 * FPS  # 30 seconds for first difficulty increase

    def generate_upgrade_options(self):
        options = []

        # Option 1: New weapon if < 3 weapons, otherwise upgrade random weapon
        if len(self.player.weapons) < 3:
            # Get weapons the player doesn't have yet
            current_weapon_types = [w.type for w in self.player.weapons]
            new_weapon_options = [w for w in list(WeaponType) if w not in current_weapon_types]

            if new_weapon_options:
                weapon_type = random.choice(new_weapon_options)
                options.append({
                    'type': 'new_weapon',
                    'weapon_type': weapon_type,
                    'name': f"New Weapon: {weapon_type.name}",
                    'description': f"Add a new {weapon_type.name.lower()} weapon to your arsenal."
                })

        # Option 2-3: Upgrade existing weapons
        for weapon in self.player.weapons:
            options.append({
                'type': 'upgrade_weapon',
                'weapon': weapon,
                'name': f"Upgrade {weapon.type.name}",
                'description': f"Increase damage, penetration and reduce cooldown of your {weapon.type.name.lower()}."
            })

        # Option 4: Health upgrade
        options.append({
            'type': 'health_upgrade',
            'name': "Health Boost",
            'description': "Increase max health by 25 and fully heal."
        })

        # Option 5: Speed upgrade
        options.append({
            'type': 'speed_upgrade',
            'name': "Movement Speed",
            'description': "Increase movement speed by 15%."
        })

        # Randomly select 3 different options
        if len(options) > 3:
            return random.sample(options, 3)
        return options

    def apply_upgrade(self, option):
        if option['type'] == 'new_weapon':
            self.player.weapons.append(Weapon(option['weapon_type']))

        elif option['type'] == 'upgrade_weapon':
            weapon = option['weapon']
            weapon.level += 1
            weapon.apply_level_bonuses()

        elif option['type'] == 'health_upgrade':
            self.player.max_health += 25
            self.player.health = self.player.max_health

        elif option['type'] == 'speed_upgrade':
            self.player.speed *= 1.15

    def update(self):
        if self.game_over or self.paused or self.show_upgrade_menu:
            return

        # Get keyboard input
        keys = pygame.key.get_pressed()

        # Update player
        self.player.update(keys, self.enemies)

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.player.x, self.player.y)

            # Check collision with player
            if enemy.check_collision(self.player):
                if self.player.take_damage(enemy.damage):
                    self.game_over = True

        # Check for dead enemies and remove them
        for enemy in self.enemies[:]:
            if enemy.health <= 0:
                self.show_upgrade_menu = self.player.add_xp(enemy.xp_value)
                self.player.kills += 1

                if enemy.drops_gem:
                    self.player.add_gem()

                self.enemies.remove(enemy)

        # Spawn enemies
        self.enemy_spawn_timer += 1

        spawn_rate = max(10, ENEMY_SPAWN_RATE - self.difficulty_level * 10)
        max_enemies = max(MIN_ENEMIES, 10 + self.difficulty_level * 5)

        if self.enemy_spawn_timer >= spawn_rate and len(self.enemies) < max_enemies:
            self.enemies.append(Enemy(self.player.x, self.player.y))
            self.enemy_spawn_timer = 0

        # Increase difficulty over time
        self.time += 1
        if self.time >= self.next_difficulty_time:
            self.difficulty_level += 1
            self.next_difficulty_time += 30 * FPS  # 30 more seconds for next increase

    def draw(self, screen):
        # Clear screen
        screen.fill(BLACK)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen)

        # Draw player
        self.player.draw(screen)

        # Draw UI
        self.draw_ui(screen)

        # Draw game over screen
        if self.game_over:
            self.draw_game_over(screen)

        # Draw upgrade menu
        if self.show_upgrade_menu:
            self.draw_upgrade_menu(screen)

        # Update display
        pygame.display.flip()

    def draw_ui(self, screen):
        # XP bar
        xp_bar_width = SCREEN_WIDTH - 20
        xp_bar_height = 10
        xp_bar_x = 10
        xp_bar_y = 10

        # Background (empty XP)
        pygame.draw.rect(screen, WHITE, (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height))
        # Foreground (current XP)
        current_xp_width = int((self.player.xp / self.player.xp_to_level) * xp_bar_width)
        pygame.draw.rect(screen, BLUE, (xp_bar_x, xp_bar_y, current_xp_width, xp_bar_height))

        # Level text
        level_text = font.render(f"Level: {self.player.level}", True, WHITE)
        screen.blit(level_text, (10, 25))

        # Kills text
        kills_text = font.render(f"Kills: {self.player.kills}", True, WHITE)
        screen.blit(kills_text, (10, 45))

        # Gems text
        gems_text = font.render(f"Gems: {self.player.gems}", True, GOLD)
        screen.blit(gems_text, (10, 65))

        # Time text (convert frames to seconds)
        time_seconds = self.time // FPS
        minutes = time_seconds // 60
        seconds = time_seconds % 60
        time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH - 120, 25))

        # Weapon info
        weapons_text = font.render("Weapons:", True, WHITE)
        screen.blit(weapons_text, (SCREEN_WIDTH - 120, 45))

        for i, weapon in enumerate(self.player.weapons):
            weapon_text = font.render(f"{weapon.type.name} Lv{weapon.level}", True, WHITE)
            screen.blit(weapon_text, (SCREEN_WIDTH - 120, 65 + i * 20))

    def draw_game_over(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = large_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))

        # Stats
        stats = [
            f"Level Reached: {self.player.level}",
            f"Enemies Defeated: {self.player.kills}",
            f"Gems Collected: {self.player.gems}",
            f"Time Survived: {self.time//FPS//60:02d}:{self.time//FPS%60:02d}"
        ]

        for i, stat in enumerate(stats):
            text = font.render(stat, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + i * 30))

        # Restart instruction
        restart_text = font.render("Press R to restart or ESC to quit", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 150))

    def draw_upgrade_menu(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        screen.blit(overlay, (0, 0))

        # Level up text
        level_up_text = large_font.render(f"Level Up! - Level {self.player.level}", True, GOLD)
        screen.blit(level_up_text, (SCREEN_WIDTH // 2 - level_up_text.get_width() // 2, 50))

        # Choose upgrade text
        choose_text = font.render("Choose an upgrade (press 1, 2, or 3):", True, WHITE)
        screen.blit(choose_text, (SCREEN_WIDTH // 2 - choose_text.get_width() // 2, 100))

        # Draw options
        for i, option in enumerate(self.upgrade_options):
            # Option box
            box_width = 600
            box_height = 80
            box_x = SCREEN_WIDTH // 2 - box_width // 2
            box_y = 150 + i * (box_height + 20)

            # Draw box
            pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, BLACK, (box_x + 2, box_y + 2, box_width - 4, box_height - 4))

            # Option text
            name_text = font.render(option['name'], True, GOLD)
            desc_text = font.render(option['description'], True, WHITE)

            screen.blit(name_text, (box_x + 20, box_y + 15))
            screen.blit(desc_text, (box_x + 20, box_y + 45))

            # Draw selection number
            key_text = large_font.render(str(i + 1), True, WHITE)
            screen.blit(key_text, (box_x + box_width - 30, box_y + box_height // 2 - key_text.get_height() // 2))


def main():
    game = Game()
    running = True

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Game over controls
                if game.game_over:
                    if event.key == pygame.K_r:
                        game = Game()  # Restart
                    elif event.key == pygame.K_ESCAPE:
                        running = False  # Quit

                # Upgrade menu controls
                elif game.show_upgrade_menu:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3] and len(
                            game.upgrade_options) >= event.key - pygame.K_0:
                        option_index = event.key - pygame.K_1
                        if 0 <= option_index < len(game.upgrade_options):
                            game.apply_upgrade(game.upgrade_options[option_index])
                            game.show_upgrade_menu = False

                # Pause control
                elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    game.paused = not game.paused
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    if event.key == pygame.K_1:
                        game.player.change_weapon(1)
                    elif event.key == pygame.K_2:
                        game.player.change_weapon(2)
                    elif event.key == pygame.K_3:
                        game.player.change_weapon(3)
                elif event.key == pygame.K_l and game.paused:
                    game.player.level += 1


        # Update game state
        game.update()

        # Draw everything
        game.draw(screen)

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()