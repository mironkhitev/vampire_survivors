import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game import Game
# Initialize pygame
# from ui import UI

pygame.init()

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vampire Survivors Clone")
clock = pygame.time.Clock()

def main():
    game = Game()
    # ui = UI(game)
    # game.ui = ui
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
                            game.upgrade_options = []
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
