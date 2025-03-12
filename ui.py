import pygame
from constants import WHITE, BLACK, BLUE, RED, GOLD, SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 48)
    
    def draw_ui(self, screen):
        # XP bar
        xp_bar_width = SCREEN_WIDTH - 20
        xp_bar_height = 10
        xp_bar_x = 10
        xp_bar_y = 10

        # Background (empty XP)
        pygame.draw.rect(screen, WHITE, (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height))
        # Foreground (current XP)
        current_xp_width = int((self.game.player.xp / self.game.player.xp_to_level) * xp_bar_width)
        pygame.draw.rect(screen, BLUE, (xp_bar_x, xp_bar_y, current_xp_width, xp_bar_height))

        # Level text
        level_text = self.font.render(f"Level: {self.game.player.level}", True, WHITE)
        screen.blit(level_text, (10, 25))

        # Kills text
        kills_text = self.font.render(f"Kills: {self.game.player.kills}", True, WHITE)
        screen.blit(kills_text, (10, 45))

        # Gems text
        gems_text = self.font.render(f"Gems: {self.game.player.gems}", True, GOLD)
        screen.blit(gems_text, (10, 65))

        # Time text (convert frames to seconds)
        time_seconds = self.game.time // FPS
        minutes = time_seconds // 60
        seconds = time_seconds % 60
        time_text = self.font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH - 120, 25))

        # Weapon info
        weapons_text = self.font.render("Weapons:", True, WHITE)
        screen.blit(weapons_text, (SCREEN_WIDTH - 120, 45))

        for i, weapon in enumerate(self.game.player.weapons):
            weapon_text = self.font.render(f"{weapon.type.name} Lv{weapon.level}", True, WHITE)
            screen.blit(weapon_text, (SCREEN_WIDTH - 120, 65 + i * 20))

    def draw_game_over(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = self.large_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))

        # Stats
        stats = [
            f"Level Reached: {self.game.player.level}",
            f"Enemies Defeated: {self.game.player.kills}",
            f"Gems Collected: {self.game.player.gems}",
            f"Time Survived: {self.game.time//FPS//60:02d}:{self.game.time//FPS%60:02d}"
        ]

        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + i * 30))

        # Restart instruction
        restart_text = self.font.render("Press R to restart or ESC to quit", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 150))

    def draw_upgrade_menu(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        screen.blit(overlay, (0, 0))

        # Level up text
        level_up_text = self.large_font.render(f"Level Up! - Level {self.game.player.level}", True, GOLD)
        screen.blit(level_up_text, (SCREEN_WIDTH // 2 - level_up_text.get_width() // 2, 50))

        # Choose upgrade text
        choose_text = self.font.render("Choose an upgrade (press 1, 2, or 3):", True, WHITE)
        screen.blit(choose_text, (SCREEN_WIDTH // 2 - choose_text.get_width() // 2, 100))

        # Draw options
        for i, option in enumerate(self.game.upgrade_options):
            # Option box
            box_width = 600
            box_height = 80
            box_x = SCREEN_WIDTH // 2 - box_width // 2
            box_y = 150 + i * (box_height + 20)

            # Draw box
            pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, BLACK, (box_x + 2, box_y + 2, box_width - 4, box_height - 4))

            # Option text
            name_text = self.font.render(option['name'], True, GOLD)
            desc_text = self.font.render(option['description'], True, WHITE)

            screen.blit(name_text, (box_x + 20, box_y + 15))
            screen.blit(desc_text, (box_x + 20, box_y + 45))

            # Draw selection number
            key_text = self.large_font.render(str(i + 1), True, WHITE)
            screen.blit(key_text, (box_x + box_width - 30, box_y + box_height // 2 - key_text.get_height() // 2))
