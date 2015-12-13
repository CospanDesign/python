import pygame
import random
from game_defines import *

class LevelMap(object):

    def __init__(self, map_object, actors, level_assets):
        self.map_object = map_object
        self.actors = actors
        self.map_surface = None

        self.assets = level_assets

        self.tile_image = { 'x': self.assets['corner'],
                            '#': self.assets['wall'],
                            'o': self.assets['inside floor'],
                            ' ': self.assets['outside floor']}

        self.out_image  = { '1': self.assets['rock'],
                            '2': self.assets['short tree'],
                            '3': self.assets['tall tree'],
                            '4': self.assets['ugly tree']}

        self.decorate_map()
        for name in self.actors:
            self.actors[name].set_map(self)


    def is_wall(self, x, y):
        if x < 0 or x >= len(self.map_object) or y < 0 or y >= len(self.map_object[x]):
            return False
        if self.map_object[x][y] in ('#', 'x'):
            return True
        return False

    def is_blocked(self, x, y):
        if self.is_wall(x, y):
            return True
        elif x < 0 or x >= len(self.map_object) or y < 0 or y >= len(self.map_object[x]):
            print "Assertion errro!"
            return True
        return False

    def decorate_map(self):
        '''
        Replace the nothingness void that is my life outside the walls of the
        level with random prettyness
        '''
        for x in range(len(self.map_object)):
            for y in range(len(self.map_object[0])):
                if self.map_object[x][y] in ('$', '.', '@', '+', '*'):
                    self.map_object[x][y] = ' '

        self.flood_fill(self.actors["cat"].get_x(), self.actors["cat"].get_y(), ' ', 'o')

        #Convert adjoined walls into corner tiles
        for x in range(len(self.map_object)):
            for y in range(len(self.map_object[0])):
                if self.map_object[x][y] == '#':
                    if (self.is_wall(x, y-1) and self.is_wall(x+1, y)) or \
                       (self.is_wall(x+1, y) and self.is_wall(x, y+1)) or \
                       (self.is_wall(x, y+1) and self.is_wall(x-1, y)) or \
                       (self.is_wall(x-1, y) and self.is_wall(x, y-1)):
                        self.map_object[x][y] = 'x'

                elif self.map_object[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                    self.map_object[x][y] = random.choice(list(self.out_image.keys()))


    def flood_fill(self, x, y, old_char, new_char):
        """Changes any values matching oldCharacter on the map object to
        newCharacter at the (x, y) position, and does the same for the
        positions to the left, right, down, and up of (x, y), recursively."""

        # In this game, the flood fill algorithm creates the inside/outside
        # floor distinction. This is a "recursive" function.
        # For more info on the Flood Fill algorithm, see:
        #   http://en.wikipedia.org/wiki/Flood_fill

        if self.map_object[x][y] == old_char:
            self.map_object[x][y] = new_char

        if x < len(self.map_object) - 1 and self.map_object[x+1][y] == old_char:
            self.flood_fill(x+1, y, old_char, new_char) # call right
        if x > 0 and self.map_object[x-1][y] == old_char:
            self.flood_fill(x-1, y, old_char, new_char) # call left
        if y < len(self.map_object[x]) - 1 and self.map_object[x][y+1] == old_char:
            self.flood_fill(x, y+1, old_char, new_char) # call down
        if y > 0 and self.map_object[x][y-1] == old_char:
            self.flood_fill(x, y-1, old_char, new_char) # call up

    def draw_map(self):
        map_width = len(self.map_object) * TILEWIDTH
        map_height = (len(self.map_object[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
        self.map_surface = pygame.Surface((map_width, map_height))
        self.map_surface.fill(BGCOLOR)

        for x in range(len(self.map_object)):
            for y in range(len(self.map_object[x])):
                space_rect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
                if self.map_object[x][y] in self.tile_image:
                    base_tile = self.tile_image[self.map_object[x][y]]
                elif self.map_object[x][y] in self.out_image:
                    base_tile = self.tile_image[' ']

                self.map_surface.blit(base_tile, space_rect)
                if self.map_object[x][y] in self.out_image:
                    self.map_surface.blit(self.out_image[self.map_object[x][y]], space_rect)

        #Add Actors
        for name in self.actors:
            actor = self.actors[name]
            x = actor.get_x()
            y = actor.get_y()
            space_rect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
            self.map_surface.blit(actor.get_image(), space_rect)

    def get_level_surface(self):
        return self.map_surface

    def get_actors(self):
        return self.actors

