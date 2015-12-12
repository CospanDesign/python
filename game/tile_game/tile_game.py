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

BRIGHTBLUE      = (  0, 170, 255)
WHITE           = (255, 255, 255)
BGCOLOR         = BRIGHTBLUE
TEXTCOLOR       = WHITE

UP              = 'up'
DOWN            = 'down'
LEFT            = 'left'
RIGHT           = 'right'

ASSET_BASE      = os.path.join(os.path.dirname(__file__), "assets")

DEFAULT_GAME_NAME = 'Tile Game'
DEFAULT_LEVEL_FILE = 'levels.txt'

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
        self.images = { 'uncovered goal': pygame.image.load(Game.asset('RedSelector.png')),
                        'covered goal':   pygame.image.load(Game.asset('Selector.png')),
                        'star':           pygame.image.load(Game.asset('Star.png')),
                        'corner':         pygame.image.load(Game.asset('Wall_Block_Tall.png')),
                        'wall':           pygame.image.load(Game.asset('Wood_Block_Tall.png')),
                        'inside floor':   pygame.image.load(Game.asset('Plain_Block.png')),
                        'outside floor':  pygame.image.load(Game.asset('Grass_Block.png')),
                        'title':          pygame.image.load(Game.asset('star_title.png')),
                        'solved':         pygame.image.load(Game.asset('star_solved.png')),
                        'princess':       pygame.image.load(Game.asset('princess.png')),
                        'boy':            pygame.image.load(Game.asset('boy.png')),
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
        self.read_levels_file(levels)

    def image_map(self, map_item):
        return self.tile_map[map_item]

    def get_outside_image(self, image_index):
        return self.outside_map[image_index]

    def terminate(self):
        pygame.quit()
        sys.exit()

    def loop(self):
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                # Player clicked the "X" at the corner of the window.
                self.terminate()

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
                assert startx != None and starty != None, "Level %s (around line %s) in %s is missing a '@' or '+' to make the start point." %(level_num + 1, line_num, filename)
                assert len(goals) > 0, 'level %s (around line %s) in %s must have at least one goal.' % (level_num + 1, line_num, filename)
                assert len(stars) <= len(goals), 'level %s (around line %s) in %s is impossible to solve. It has %s goals but ony %s stars.' % (level_num + 1, line_num, filename, len(goals), len(stars))
  
                game_state = {  'player':       (startx, starty),
                                'step_counter': 0,
                                'stars':        stars}
  
                level_object = {'width':        max_width,
                                'height':       len(map_object),
                                'map_object':   map_object,
                                'goals':        goals,
                                'start_state':  game_state}
  
                self.levels.append(level_object)

                map_text_lines = []
                map_object = []
                game_state = {}
                level_num += 1



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


