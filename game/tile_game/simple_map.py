import level_map
from game_defines import *


class SimpleMap(level_map.LevelMap):
    def __init__(self, map_object, actors, assets):
        super(SimpleMap, self).__init__(map_object, actors, assets)

    def get_mice_positions(self):
        #Don't need any processing to find the mouse
        mlist = []
        for name in self.actors:
            actor = self.actors[name]
            if actor.get_type() == "mouse":
                mlist.append((actor.get_x(), actor.get_y()))

        return mlist

    def is_mouse_at_position(self, x, y):
        mlist = self.get_mice_positions()
        for m in mlist:
            if m.get_x() == x and m.get_y() == y:
                return True
        return False

    def kill_mouse_at_position(self, x, y):
        dead_mouse = None
        mlist = self.get_mice_positions()
        for m in mlist:
            if m.get_x() == x and m.get_y() == y:
                dead_mouse = m
                break

        del(self.actors[dead_mouse.name()])

    def get_mice_count(self):
        mlist = self.get_mice_positions()
        return len(mlist)

    def is_mouse_visible(self):
        return True
