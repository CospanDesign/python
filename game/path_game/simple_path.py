from game_defines import *
from path import Path

class SimplePath(Path):
    def __init__(self):
        super(SimplePath, self).__init__()
        #Used to remeber the previous version of the path
        self.path = None

    def update(self, pos_x, pos_y, target_x, target_y):
        path = []
        x = pos_x
        y = pos_y
        path.append((pos_x, pos_y))

        while x != target_x or y != target_y:
            if x < target_x:
                x = x + 1
            elif x > target_x:
                x = x - 1

            if y < target_y:
                y = y + 1
            elif y > target_y:
                y = y - 1

            path.append((x,y))

        self.path = path
        return path

    def get_path(self):
        return self.path
