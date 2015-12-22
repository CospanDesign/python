#! /usr/bin/env python

# Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)
#
# Game is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Game is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Game; If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import argparse
from math import pi, sin, cos
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.gui.OnscreenText import OnscreenText

from panda3d.core import Point3
from panda3d.core import PandaNode, NodePath, Camera, TextNode

NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\tSomething\n" \
         "\n"

ENVIRONMENT = "models/world"
RALPH_ACTOR = "models/ralph"
RALPH_ACTIONS = {"walk": "models/ralph-walk",
                 "run": "models/ralph-run"}


# Function to put instructions on the screen.
def add_instructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                        shadow=(0, 0, 0, 1), parent=base.a2dTopLeft,
                        pos=(0.08, -pos - 0.04), align=TextNode.ALeft)

# Function to put title on the screen.
def add_title(text):
    return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1), scale=.07,
                        parent=base.a2dBottomRight, align=TextNode.ARight,
                        pos=(-0.1, 0.09), shadow=(0, 0, 0, 1))


class PandaPath (ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        #Set the background color to black
        self.win.setClearColor((0, 0, 0, 1))


        # This is used to store which keys are currently pressed.
        self.key_map = {
            "left": 0, "right": 0, "forward": 0, "cam-left": 0, "cam-right": 0}


        #Load the Environment Model
        self.environ = self.loader.loadModel(ENVIRONMENT)
        #Reparent the model to the render controller
        self.environ.reparentTo(self.render)


        #Apply scale and position transform on the model
        #self.environ.setScale(0.25, 0.25, 0.25)
        #self.environ.setPos(-8, 42, 0)

        #Load and transform the panda actor
        ralph_start_pos = self.environ.find("**/start_point").getPos()
        self.ralph = Actor( RALPH_ACTOR,
                            RALPH_ACTIONS)

        #self.ralph.setScale(0.005, 0.005, 0.005)
        self.ralph.reparentTo(self.render)
        #Loop it's animation
        self.ralph.setScale(0.2)
        self.ralph.setPos(ralph_start_pos + (0, 0, 0.5))
        self.ralph.loop("walk")

        #Create a floater object, which floats 2 units above rlaph. We use this as a target for the camera to look at

        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.ralph)
        self.floater.setZ(2.0)



        #Configure the Camera
        #Add the spin camera taks procedure to the taks manager
        #self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        #self.disableMouse()
        self.camera.setPos(self.ralph.getX(), self.ralph.getY() + 10, 2)



        #Create the four lerp intervals needed for the panda to walk band and forth
        panda_pos_interval1 = self.ralph.posInterval( 4,
                                                            Point3(0, -10, 0),
                                                            startPos=Point3(0, 10, 0))
        panda_pos_interval2 = self.ralph.posInterval( 4,
                                                            Point3(0, 10, 0),
                                                            startPos=Point3(0, -10, 0))
        panda_hpr_interval1 = self.ralph.hprInterval( 1,
                                                            Point3(180, 0, 0),
                                                            startHpr=Point3(0, 0, 0))
        panda_hpr_interval2 = self.ralph.hprInterval( 1,
                                                            Point3(0, 0, 0),
                                                            startHpr=Point3(180, 0, 0))


        #Create and play the sequence that coordinates the interval
        '''
        self.ralph_pace = Sequence( panda_pos_interval1,
                                    panda_hpr_interval1,
                                    panda_pos_interval2,
                                    panda_hpr_interval2,
                                    name="panda_pace")

        self.ralph_pace.loop()
        '''



        #Post the Instruction
        self.title = add_title( "Panda 3D Tutorial: Roaming Panda!")

        #Instructions
        self.inst1 = add_instructions(0.06, "[ESC]: Quit")

        #Accept certain control keys
        self.accept("escape", sys.exit)

        self.camera.lookAt(self.floater)

    def spinCameraTask(self, task):
        angle_degrees = task.time * 6.0
        angle_radians = angle_degrees * (pi / 180.0)
        self.camera.setPos(20.0 * sin(angle_radians), -20.0 * cos(angle_radians), 3)
        self.camera.setHpr(angle_degrees, 0, 0)
        #self.camera.setHpr(angle_degrees, 0, angle_degrees)
        return Task.cont

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

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    args = parser.parse_args()
    print "Running Script: %s" % NAME


    if args.debug:
        print "test: %s" % str(args.test[0])

    app = PandaPath()
    app.run()

if __name__ == "__main__":
    main(sys.argv)

