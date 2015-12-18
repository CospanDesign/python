import os

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)


DIRECTIONS = enum ("UP", "DOWN", "LEFT", "RIGHT")
STATE = enum ("START", "SETUP_LEVEL", "RUN_LEVEL", "FINISHED")

FPS             = 30 # frames per second to update the screen
WINWIDTH        = 800 # width of the program's window, in pixels
WINHEIGHT       = 600 # height in pixels
HALF_WINWIDTH   = int(WINWIDTH / 2)
HALF_WINHEIGHT  = int(WINHEIGHT / 2)

# The total width and height of each tile in pixels.
TILEWIDTH       = 50
TILEHEIGHT      = 85
TILEFLOORHEIGHT = 40

CAM_MOVE_SPEED  = 5 # how many pixels per frame the camera moves

# The percentage of outdoor tiles that have additional
# decoration on them, such as a tree or rock.
OUTSIDE_DECORATION_PCT = 20

GRAY        = (0x7F, 0x7F, 0x7F)
NAVYBLUE    = (0x3F, 0x3F, 0x7F)
WHITE       = (0xFF, 0xFF, 0xFF)
RED         = (0xFF, 0x00, 0x00)
GREEN       = (0x00, 0xFF, 0x00)
BLUE        = (0x00, 0x00, 0xFF)
YELLOW      = (0xFF, 0xFF, 0x00)
ORANGE      = (0xFF, 0x7F, 0x00)
PURPLE      = (0xFF, 0x00, 0xFF)
CYAN        = (0x00, 0xFF, 0xFF)
BLACK       = (0x00, 0x00, 0x00)

BRUSE       = (0x3F, 0x00, 0xFF)

BGCOLOR         = BRUSE
BGCOLOR_MANUAL  = ORANGE
TEXTCOLOR       = BLACK



ASSET_BASE      = os.path.join(os.path.dirname(__file__), "assets")

DEFAULT_GAME_NAME = 'Tile Game'
DEFAULT_LEVEL_FILE = 'levels.txt'
DEFAULT_BASIC_FONT = 'freesansbold.ttf'


