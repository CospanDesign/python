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

from game_defines import *


from cat import Cat
from mouse import Mouse

from simple_map import SimpleMap

NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\tSomething\n" \
         "\n"

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

        self.assets = { 'uncovered goal': pygame.image.load(Game.asset('RedSelector.png')),
                        'covered goal':   pygame.image.load(Game.asset('Selector.png')),
                        'star':           pygame.image.load(Game.asset('Star.png')),
                        'corner':         pygame.image.load(Game.asset('Wall_Block_Tall.png')),
                        'wall':           pygame.image.load(Game.asset('Wood_Block_Tall.png')),
                        'inside floor':   pygame.image.load(Game.asset('Plain_Block.png')),
                        'outside floor':  pygame.image.load(Game.asset('Grass_Block.png')),
                        'title':          pygame.image.load(Game.asset('the_path_title.png')),
                        'solved':         pygame.image.load(Game.asset('star_solved.png')),
                        'princess':       pygame.image.load(Game.asset('princess.png')),
                        'cat':            pygame.image.load(Game.asset('cat.png')),
                        'mouse':          pygame.image.load(Game.asset('mouse.png')),
                        'catgirl':        pygame.image.load(Game.asset('catgirl.png')),
                        'horngirl':       pygame.image.load(Game.asset('horngirl.png')),
                        'pinkgirl':       pygame.image.load(Game.asset('pinkgirl.png')),
                        'rock':           pygame.image.load(Game.asset('Rock.png')),
                        'short tree':     pygame.image.load(Game.asset('Tree_Short.png')),
                        'tall tree':      pygame.image.load(Game.asset('Tree_Tall.png')),
                        'ugly tree':      pygame.image.load(Game.asset('Tree_Ugly.png'))}


        self.levels = []
        self.level_map = None
        self.read_levels_file(levels)
        self.main_character = 'cat'
        #Starting Level
        self.level_num = 0
        self.current_level = None
        self.state = STATE.START
        self.manual_mode = True

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
                mice = []
                for x in range(max_width):
                    for y in range(len(map_object[x])):
                        if map_object[x][y] in ('@', '+'):
                            startx = x
                            starty = y
                        if map_object[x][y] in ('.', '+', '*'):
                            # '.' is goal, '*' is star & goal
                            goals.append((x, y))
                        if map_object[x][y] in ('$', '*'):
                            mice.append((x, y))

                #Sanity Checks
                assert startx != None and starty != None, "Level %s (around line %s) in %s is missing a '@' or '+' to make the start point." %(level_num + 1, line_num, filepath)
                #assert len(goals) > 0, 'level %s (around line %s) in %s must have at least one goal.' % (level_num + 1, line_num, filepath)
                #assert len(mice) <= len(goals), 'level %s (around line %s) in %s is impossible to solve. It has %s goals but ony %s mice.' % (level_num + 1, line_num, filepath, len(goals), len(mice))

                game_state = {  'player':       (startx, starty),
                                'step_counter': 0,
                                'mice':        mice}

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
        title_rect = self.assets['title'].get_rect()
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
        self.display_surface.blit(self.assets["title"], title_rect)

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

#Level Specific Functions
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
                if event.key == K_m:
                    self.manual_mode = not self.manual_mode
                if self.manual_mode:
                    if event.key == K_LEFT:
                        player_move_to = DIRECTIONS.LEFT
                    if event.key == K_RIGHT:
                        player_move_to = DIRECTIONS.RIGHT
                    if event.key == K_UP:
                        player_move_to = DIRECTIONS.UP
                    if event.key == K_DOWN:
                        player_move_to = DIRECTIONS.DOWN

        redraw_map = False

        actors = self.level_map.get_actors()
        if self.manual_mode:
            if player_move_to is not None:
                print "Move:"
                actors[self.main_character].move(player_move_to)
                self.level_map.draw_map()
            '''
            #if player_move_to is not None:
                #cat = self.players["cat"]
                #moved = cat.make_move(self.players["cat"], player_move_to)
            
                #if moved:
                #    state['step_counter'] += 1
                #    self.draw_map() 
            '''
            
            self.display_surface.fill(BGCOLOR_MANUAL)


        else:
            #Use the automatic movement
            self.display_surface.fill(BGCOLOR)
            for name in actors:
                actors[name].process(None)
                self.level_map.draw_map()

        map_surface = self.level_map.get_level_surface()
        map_surface_rect = map_surface.get_rect()
        map_surface_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

        self.display_surface.blit(map_surface, map_surface_rect)

        pygame.display.update()
        self.fpsclock.tick()

    def setup_level(self):
        self.current_level = self.levels[self.level_num]
        start_state = self.current_level["start_state"]
        #Add the game actors
        actors = {}
        actors["cat"] = Cat("cat", start_state['player'][0], start_state['player'][1])
        for i in range (len(start_state["mice"])):
            m = start_state["mice"][i]
            name = "mouse %d" % i
            actors[name] = Mouse(name, m[0], m[1])

        self.level_map = SimpleMap(self.current_level["map_object"], actors, self.assets)
        self.level_map.draw_map()

        self.state = STATE.RUN_LEVEL

#Map Specific Functions

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

