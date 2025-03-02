import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game import Game

# Initialize pygame
pygame.init()

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vampire Survivors Clone")
clock = pygame.time.Clock()

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
                            game.