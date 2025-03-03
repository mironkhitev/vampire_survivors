import pygame
from enum import Enum

# Game constants
EACH_NUM_LEVEL_UP_UPGRADE_STUFF = 1
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

# Weapon types enum
class WeaponType(Enum):
    KNIFE = 1
    AXE = 2
    MAGIC = 3

# Player parameters
XP_TO_LEVEL = 1 #100