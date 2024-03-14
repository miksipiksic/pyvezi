import os

# parameters
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
TILE_SIZE = 100
GRAVITY = 10
WIN_CNT = 4
M = 6
N = 7
INFO_HEIGHT = 30
INFO_SIDE_OFFSET = 10
FRAMES_PER_SEC = 120
INFO_FONT = None

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (192, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
YELLOW = (255, 255, 0)

# paths
GAME_FOLDER = os.path.dirname(__file__)
ACTIONS_FOLDER = os.path.join(GAME_FOLDER, 'actions')
IMG_FOLDER = os.path.join(GAME_FOLDER, 'img')
LOG_FOLDER = os.path.join(GAME_FOLDER, 'logs')
FONT_FOLDER = os.path.join(GAME_FOLDER, 'fonts')
