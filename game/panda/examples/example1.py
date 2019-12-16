#! /usr/bin/env python3

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
from panda3d.core import Point3

NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\tSomething\n" \
         "\n"

ENVIRONMENT = "models/environment"
PANDA_ACTOR = "models/panda-model"
PANDA_ACTIONS = {"walk": "models/panda-walk4"}

class MyApp (ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        #Load the Environment Model
        self.environ = self.loader.loadModel(ENVIRONMENT)
        #Reparent the model to the render controller
        self.environ.reparentTo(self.render)
        #Apply scale and position transform on the model
        self.environ.setScale(0.25, 0.25, 0.25)
        self.environ.setPos(-8, 42, 0)

        #Add the spin camera taks procedure to the taks manager
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

        #Load and transform the panda actor
        self.panda_actor = Actor(   PANDA_ACTOR,
                                    PANDA_ACTIONS)

        self.panda_actor.setScale(0.005, 0.005, 0.005)
        self.panda_actor.reparentTo(self.render)
        #Loop it's animation
        self.panda_actor.loop("walk")



        #Create the four lerp intervals needed for the panda to walk band and forth
        panda_pos_interval1 = self.panda_actor.posInterval( 4,
                                                            Point3(0, -10, 0),
                                                            startPos=Point3(0, 10, 0))
        panda_pos_interval2 = self.panda_actor.posInterval( 4,
                                                            Point3(0, 10, 0),
                                                            startPos=Point3(0, -10, 0))
        panda_hpr_interval1 = self.panda_actor.hprInterval( 1,
                                                            Point3(180, 0, 0),
                                                            startHpr=Point3(0, 0, 0))
        panda_hpr_interval2 = self.panda_actor.hprInterval( 1,
                                                            Point3(0, 0, 0),
                                                            startHpr=Point3(180, 0, 0))


        #Create and play the sequence that coordinates the interval
        self.panda_pace = Sequence( panda_pos_interval1,
                                    panda_hpr_interval1,
                                    panda_pos_interval2,
                                    panda_hpr_interval2,
                                    name="panda_pace")

        self.panda_pace.loop()


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
    print ("Running Script: %s" % NAME)


    if args.debug:
        print ("test: %s" % str(args.test[0]))

    app = MyApp()
    app.run()

if __name__ == "__main__":
    main(sys.argv)



