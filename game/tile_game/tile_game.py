#! /usr/bin/env python

# This code is taken from Star Push
# Star Pusher (a Sokoban clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import sys
import os
import random
import sys
import copy

import argparse
import pygame

from pygame.locals import *

NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\tSomething\n" \
         "\n"


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
TEXTCOLOR       = BLACK



ASSET_BASE      = os.path.join(os.path.dirname(__file__), "assets")

DEFAULT_GAME_NAME = 'Tile Game'
DEFAULT_LEVEL_FILE = 'levels.txt'
DEFAULT_BASIC_FONT = 'freesansbold.ttf'


class Game(object):

    @staticmethod
    def asset(name):
        return os.path.join(ASSET_BASE, name)

    def __init__(self, name = DEFAULT_GAME_NAME, levels = DEFAULT_LEVEL_FILE):
        pygame.init()

        #Setup frames per second clock
        self.fpsclock = pygame.time.Clock()
        #Setup the main display surface
        self.display_surface = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
        pygame.display.set_caption(name)

        #Setup the fonts
        self.basic_font = pygame.font.Font(DEFAULT_BASIC_FONT, 18)

        self.images = { 'uncovered goal': pygame.image.load(Game.asset('RedSelector.png')),
                        'covered goal':   pygame.image.load(Game.asset('Selector.png')),
                        'star':           pygame.image.load(Game.asset('Star.png')),
                        'corner':         pygame.image.load(Game.asset('Wall_Block_Tall.png')),
                        'wall':           pygame.image.load(Game.asset('Wood_Block_Tall.png')),
                        'inside floor':   pygame.image.load(Game.asset('Plain_Block.png')),
                        'outside floor':  pygame.image.load(Game.asset('Grass_Block.png')),
                        'title':          pygame.image.load(Game.asset('the_path_title.png')),
                        'solved':         pygame.image.load(Game.asset('star_solved.png')),
                        'princess':       pygame.image.load(Game.asset('princess.png')),
                        'jeff':           pygame.image.load(Game.asset('boy.png')),
                        'catgirl':        pygame.image.load(Game.asset('catgirl.png')),
                        'horngirl':       pygame.image.load(Game.asset('horngirl.png')),
                        'pinkgirl':       pygame.image.load(Game.asset('pinkgirl.png')),
                        'rock':           pygame.image.load(Game.asset('Rock.png')),
                        'short tree':     pygame.image.load(Game.asset('Tree_Short.png')),
                        'tall tree':      pygame.image.load(Game.asset('Tree_Tall.png')),
                        'ugly tree':      pygame.image.load(Game.asset('Tree_Ugly.png'))}

        self.tile_image = { 'x': self.images['corner'],
                            '#': self.images['wall'],
                            'o': self.images['inside floor'],
                            ' ': self.images['outside floor']}

        self.out_image  = { '1': self.images['rock'],
                            '2': self.images['short tree'],
                            '3': self.images['tall tree'],
                            '4': self.images['ugly tree']}

        self.levels = []
        self.level_map = None
        self.read_levels_file(levels)
        self.main_character = 'jeff'
        #Starting Level
        self.level_num = 0
        self.current_level = None
        self.state = STATE.START

    def image_map(self, map_item):
        return self.tile_map[map_item]

    def get_outside_image(self, image_index):
        return self.outside_map[image_index]

    def terminate(self):
        pygame.quit()
        sys.exit()

    def loop(self):
        if self.state == STATE.START:
            self.start_screen()

        elif self.state == STATE.SETUP_LEVEL:
            self.setup_level()

        elif self.state == STATE.RUN_LEVEL:
            self.run_level()

    def read_levels_file(self, filepath):
        if not os.path.exists(filepath):
            filepath = Game.asset(filepath)
        assert os.path.exists(filepath), "Cannot find the level file: %s" % (filepath)

        map_file = open(filepath, 'r')
        #Each Level must end with a blank line
        content = map_file.readlines() + ['\r\n']
        map_file.close()

        levels = []             #Contains a list of levels
        level_num = 0
        map_text_lines = []     #Contains the lines for a single level's map
        map_object = []         #The map objects made from the data in map text lines

        for line_num in range(len(content)):
            #Process each line
            line = content[line_num].rstrip('\r\n')
            if ';' in line:
                #Remove comments
                line = line[:line.find(';')]

            if line != '':
                #Usable Map Data
                map_text_lines.append(line)

            #Finished with data
            elif line == '' and len(map_text_lines) > 0:
                #Encountered a blank line, this is the end of a level map
                #Convert the text into an actual level
                max_width = -1
                for i in range(len(map_text_lines)):
                    if len(map_text_lines[i]) > max_width:
                        #Adjust width
                        max_width = len(map_text_lines[i])

                #Add spaces to the end of the shorter rows. This ensures the map is
                #rectangular
                for i in range(len(map_text_lines)):
                    map_text_lines[i] += ' ' * (max_width - len(map_text_lines[i]))

                #Convert map text lines to a map object
                for x in range(len(map_text_lines[0])):
                    map_object.append([])

                #Convert list of string to 2D Matrix of objects
                for y in range(len(map_text_lines)):
                    for x in range(max_width):
                        map_object[x].append(map_text_lines[y][x])

                #Loop through the spaes in a map and find the @, ., and $
                #Characters for the starting game state
                startx = None
                starty = None
                goals = []
                stars = []
                for x in range(max_width):
                    for y in range(len(map_object[x])):
                        if map_object[x][y] in ('@', '+'):
                            startx = x
                            starty = y
                        if map_object[x][y] in ('.', '+', '*'):
                            # '.' is goal, '*' is star & goal
                            goals.append((x, y))
                        if map_object[x][y] in ('$', '*'):
                            stars.append((x, y))

                #Sanity Checks
                assert startx != None and starty != None, "Level %s (around line %s) in %s is missing a '@' or '+' to make the start point." %(level_num + 1, line_num, filepath)
                #assert len(goals) > 0, 'level %s (around line %s) in %s must have at least one goal.' % (level_num + 1, line_num, filepath)
                #assert len(stars) <= len(goals), 'level %s (around line %s) in %s is impossible to solve. It has %s goals but ony %s stars.' % (level_num + 1, line_num, filepath, len(goals), len(stars))

                game_state = {  'player':       (startx, starty),
                                'step_counter': 0,
                                'stars':        stars}

                level_object = {'width':        max_width,
                                'height':       len(map_object),
                                'map_object':   map_object,
                                'goals':        goals,
                                'start_state':  game_state,
                                'state':        None}

                self.levels.append(level_object)

                map_text_lines = []
                map_object = []
                game_state = {}
                level_num += 1

    def start_screen(self):
        """
        Display the start screen
        """
        title_rect = self.images['title'].get_rect()
        top_coord = 50
        title_rect.top = top_coord
        title_rect.centerx = HALF_WINWIDTH
        top_coord += title_rect.height

        # Unfortunately, Pygame's font & text system only shows one line at
        # a time, so we can't use strings with \n newline characters in them.
        # So we will use a list with each line in it.
        instruction_text = ['Path... or not, it\'s up to you...',
                            'Arrow keys to move, WASD for camera control, P to change character.',
                            'Backspace to reset level, Esc to quit.',
                            'N for next level, B to go back a level.']

        #Start Drawing a blank color to the entire window
        self.display_surface.fill(BGCOLOR)
        self.display_surface.blit(self.images["title"], title_rect)

        #Position and draw the text
        for i in range(len(instruction_text)):
            inst_surf = self.basic_font.render(instruction_text[i], 1, TEXTCOLOR)
            inst_rect = inst_surf.get_rect()
            top_coord += 10 # 10 Pixels will go in between each line of text
            inst_rect.top = top_coord
            inst_rect.centerx = HALF_WINWIDTH
            top_coord += inst_rect.height
            self.display_surface.blit(inst_surf, inst_rect)

        while True:
            #Loop till the user presses something
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.terminate()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.terminate()
                    self.state = STATE.SETUP_LEVEL
                    return

            pygame.display.update()
            self.fpsclock.tick()

    def run_level(self):
        key_press = False
        player_move_to = None
        state = self.current_level['state']
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                # Player clicked the "X" at the corner of the window.
                self.terminate()

            if event.type == KEYDOWN:
                key_press = True
                if event.key == K_LEFT:
                    player_move_to = DIRECTIONS.LEFT
                if event.key == K_RIGHT:
                    player_move_to = DIRECTIONS.RIGHT
                if event.key == K_UP:
                    player_move_to = DIRECTIONS.UP
                if event.key == K_DOWN:
                    player_move_to = DIRECTIONS.DOWN

        redraw_map = False
        if player_move_to is not None:
            moved = self.make_move(player_move_to)

            if moved:
                state['step_counter'] += 1
                redraw_map = True

        if redraw_map:
               self.draw_map() 

        self.display_surface.fill(BGCOLOR)
        map_surface_rect = self.level_map.get_rect()
        map_surface_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

        self.display_surface.blit(self.level_map, map_surface_rect)

        pygame.display.update()
        self.fpsclock.tick()

    def setup_level(self):
        self.current_level = copy.deepcopy(self.levels[self.level_num])
        start_state = copy.deepcopy(self.current_level["start_state"])
        level_surface = self.basic_font.render("Level %s of %s" % (self.level_num + 1, len(self.levels)), 1, TEXTCOLOR)
        level_rect = level_surface.get_rect()
        level_rect.bottomleft = (20, WINHEIGHT - 35)
        map_object = self.decorate_map()
        self.current_level["map_object"] = map_object
        state = {   "x":            start_state["player"][0],
                    "y":            start_state["player"][1],
                    "step_counter": 0,
                    "stars":        start_state["stars"]}
        self.current_level["state"] = state
        self.draw_map()
        self.state = STATE.RUN_LEVEL

    def draw_map(self):
        map_object = self.current_level["map_object"]
        state = self.current_level["state"]
        goals = self.current_level["goals"]
        map_width = len(map_object) * TILEWIDTH
        map_height = (len(map_object[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
        map_surface = pygame.Surface((map_width, map_height))
        map_surface.fill(BGCOLOR)

        for x in range(len(map_object)):
            for y in range(len(map_object[x])):
                space_rect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
                if map_object[x][y] in self.tile_image:
                    base_tile = self.tile_image[map_object[x][y]]
                elif map_object[x][y] in self.out_image:
                    base_tile = self.tile_image[' ']

                map_surface.blit(base_tile, space_rect)
                if map_object[x][y] in self.out_image:
                    map_surface.blit(self.out_image[map_object[x][y]], space_rect)

                elif (x, y) in state['stars']:
                    if (x, y) in goals:
                        # A goal AND star are on thsi space, draw goal first
                        map_surface.blit(self.images["covered goal"], space_rect)

                    #Draw the star afterwards (It will be on top!)
                    map_surface.blit(self.images["star"], space_rect)

                elif (x, y) in goals:
                    #Draw a goal without a star on it
                    map_surface.blit(self.images['uncovered goal'], space_rect)

                if (x, y) == (state['x'], state['y']):
                    map_surface.blit(self.images[self.main_character], space_rect)

        self.level_map = map_surface

    def decorate_map(self):
        '''
        Replace the nothingness void that is my life outside the walls of the
        level with random prettyness
        '''
        startx = self.current_level['start_state']['player'][0]
        starty = self.current_level['start_state']['player'][1]
        map_object = self.current_level['map_object']
        for x in range(len(map_object)):
            for y in range(len(map_object[0])):
                if map_object[x][y] in ('$', '.', '@', '+', '*'):
                    map_object[x][y] = ' '
        #Flood fill to determine inside and outside of floor tiles
        self.flood_fill(map_object, startx, starty, ' ', 'o')

        #Convert adjoined walls into corner tiles
        for x in range(len(map_object)):
            for y in range(len(map_object[0])):
                if map_object[x][y] == '#':
                    if (self.is_wall(x, y-1) and self.is_wall(x+1, y)) or \
                       (self.is_wall(x+1, y) and self.is_wall(x, y+1)) or \
                       (self.is_wall(x, y+1) and self.is_wall(x-1, y)) or \
                       (self.is_wall(x-1, y) and self.is_wall(x, y-1)):
                        map_object[x][y] = 'x'

                elif map_object[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                    map_object[x][y] = random.choice(list(self.out_image.keys()))
        return map_object



    def is_blocked(self, x, y):
        """Returns True if the (x, y) position on the map is
        blocked by a wall or star, otherwise return False."""
        map_object = self.current_level["map_object"]
        state = self.current_level['state']

        if self.is_wall(x, y):
            return True

        elif x < 0 or x >= len(map_object) or y < 0 or y >= len(map_object[x]):
            return True # x and y aren't actually on the map.

        elif (x, y) in state['stars']:
            return True # a star is blocking

        return False



    def is_wall(self, x, y):
        """Returns True if the (x, y) position on
        the map is a wall, otherwise return False."""
        map_object = self.current_level['map_object']
        if x < 0 or x >= len(map_object) or y < 0 or y >= len(map_object[x]):
            return False # x and y aren't actually on the map.
        elif map_object[x][y] in ('#', 'x'):
            return True # wall is blocking
        return False

    def flood_fill(self, map_object, x, y, old_char, new_char):
        """Changes any values matching oldCharacter on the map object to
        newCharacter at the (x, y) position, and does the same for the
        positions to the left, right, down, and up of (x, y), recursively."""

        # In this game, the flood fill algorithm creates the inside/outside
        # floor distinction. This is a "recursive" function.
        # For more info on the Flood Fill algorithm, see:
        #   http://en.wikipedia.org/wiki/Flood_fill

        if map_object[x][y] == old_char:
            map_object[x][y] = new_char

        if x < len(map_object) - 1 and map_object[x+1][y] == old_char:
            self.flood_fill(map_object, x+1, y, old_char, new_char) # call right
        if x > 0 and map_object[x-1][y] == old_char:
            self.flood_fill(map_object, x-1, y, old_char, new_char) # call left
        if y < len(map_object[x]) - 1 and map_object[x][y+1] == old_char:
            self.flood_fill(map_object, x, y+1, old_char, new_char) # call down
        if y > 0 and map_object[x][y-1] == old_char:
            self.flood_fill(map_object, x, y-1, old_char, new_char) # call up

    #Movement Functions
    def make_move(self, move_to):
        state = self.current_level["state"]
        px = state['x']
        py = state['y']
        stars = state['stars']
        map_object = self.current_level["map_object"]

        if move_to == DIRECTIONS.UP:
            x_offset = 0
            y_offset = -1
        elif move_to == DIRECTIONS.RIGHT:
            x_offset = 1
            y_offset = 0
        elif move_to == DIRECTIONS.DOWN:
            x_offset = 0
            y_offset = 1
        elif move_to == DIRECTIONS.LEFT:
            x_offset = -1
            y_offset = 0

        if self.is_wall(px + x_offset, py + y_offset):
            return False

        if (px + x_offset, py + y_offset) in stars:
            if not self.is_blocked(px + (x_offset * 2), py + (y_offset * 2)):
                #Move the star
                ind = stars.index((px + x_offset, py + y_offset))
                stars[ind] = (stars[ind][0] + x_offset, stars[ind][1] + y_offset)
            else:
                return False

        state['x'] = px + x_offset
        state['y'] = py + y_offset
        return True


def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

    parser.add_argument("-t", "--test",
                        nargs=1,
                        default=["something"])

    parser.add_argument("--name",
                        nargs=1,
                        default=[DEFAULT_GAME_NAME])

    parser.add_argument("--levels",
                        nargs=1,
                        default=[DEFAULT_LEVEL_FILE])

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    args = parser.parse_args()
    print "Running Script: %s" % NAME


    if args.debug:
        print "test: %s" % str(args.test[0])

    game = Game(args.name[0], args.levels[0])
    while True:
        game.loop()

if __name__ == "__main__":
    main(sys.argv)


