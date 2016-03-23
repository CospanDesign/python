import sys
import actor
import path
import simple_map
import simple_path
from game_defines import DIRECTIONS

CAT_IMAGE_NAME = "cat.png"


PATH_ALGORITHM = simple_path.SimplePath

class Cat(actor.Actor):
    def __init__(self, name, startx, starty):
        super (Cat, self).__init__(name, CAT_IMAGE_NAME, "cat", startx, starty)

        #Define the Path
        self.path = PATH_ALGORITHM()

    def process(self, sensor_input):
        #Process current inputs and generate a map
        #The map should consist of my location and hopefully the target location
        #Find out where the mouse is right now
        target = self.find_mouse(sensor_input)

        #Update cat position
        move_to = None

        if target is not None:
            #print "Target: %s" % str(target)
            if target[0] != self.x or target[1] != self.y:
                p = self.path.update(self.x, self.y, target[0], target[1])
                print "Path: %s" % str(p)
                move_to = path.get_next_move(p, debug = True)

                if move_to is not DIRECTIONS.NOMOVE:
                    self.move(move_to)

    def find_mouse(self, sensor_input):
        if self.map_object.is_mouse_visible():
            return self.map_object.get_mice_positions()[0]

