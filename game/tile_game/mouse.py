import actor
MOUSE_IMAGE_PATH = "mouse.png"

class Mouse(actor.Actor):
    def __init__(self, name, startx, starty):
        super (Mouse, self).__init__(name, MOUSE_IMAGE_PATH, "mouse", startx, starty)

    def process(self, sensor_input):
        #print "Mouse Process"
        pass

