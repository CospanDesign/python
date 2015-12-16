import os
import pygame

from game_defines import DIRECTIONS

ASSET_BASE      = os.path.join(os.path.dirname(__file__), "assets")

class Actor(object):
    @staticmethod
    def asset(name):
        return os.path.join(ASSET_BASE, name)

    def __init__(self, name, image_path, actor_type, startx, starty):
        self.image = pygame.image.load(Actor.asset(image_path))
        self.name = name
        self.x = startx
        self.y = starty
        self.actor_type = actor_type
        self.map_object = None

    def process(self, sensor_input):
        raise AssertionError("Process Needs to be overriden")

    def get_image(self):
        return self.image

    def get_type(self):
        return self.actor_type

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_map(self, map_object):
        self.map_object = map_object

    def move(self, move_to):
        x_offset = 0
        y_offset = 0

        if move_to == DIRECTIONS.UP:
            x_offset = 0
            y_offset = -1

        elif move_to == DIRECTIONS.UPRIGHT:
            x_offset = 1
            y_offset = -1

        elif move_to == DIRECTIONS.UPLEFT:
            x_offset = -1
            y_offset = -1

        elif move_to == DIRECTIONS.RIGHT:
            x_offset = 1
            y_offset = 0

        elif move_to == DIRECTIONS.DOWN:
            x_offset = 0
            y_offset = 1

        elif move_to == DIRECTIONS.DOWNRIGHT:
            x_offset = 1
            y_offset = 1

        elif move_to == DIRECTIONS.DOWNLEFT:
            x_offset = -1
            y_offset = 1

        elif move_to == DIRECTIONS.LEFT:
            x_offset = -1
            y_offset = 0

        if self.map_object.is_blocked(self.x + x_offset, self.y + y_offset):
            return False

        self.x += x_offset
        self.y += y_offset
        return True

 
