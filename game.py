import pygame
import random

from enemy import Enemy
from player import Player
from weapon import Weapon
from constants import FPS, WeaponType, MIN_ENEMIES, ENEMY_SPAWN_RATE, SCREEN_WIDTH, BLACK
from ui import UI


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
        self.ui = UI(self)

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
        self.upgrade_options = options
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
        self.ui.draw_ui(screen)

        # Draw game over screen
        if self.game_over:
            self.ui.draw_game_over(screen)

        # Draw upgrade menu
        if self.show_upgrade_menu:
            self.ui.draw_upgrade_menu(screen)
        #     self.generate_upgrade_options()
        #     self.apply_upgrade()
        # Update display
        pygame.display.flip()

