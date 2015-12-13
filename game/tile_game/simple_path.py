from game_defines import *
from path import Path


class SimplePath(Path):
    def __init__(self):
        super(SimplePath, self).__init__()

    def update(self, pos_x, pos_y, target_x, target_y):
        if pos_x != target_x:
            if pos_x < target_x:
                return DIRECTIONS.RIGHT
            else:
                return DIRECTIONS.LEFT

        if pos_y != target_y:
            if pos_y < target_y:
                return DIRECTIONS.DOWN
            else:
                return DIRECTIONS.UP

        return None

