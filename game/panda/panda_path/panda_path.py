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

from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import CollideMask
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import Point3
from panda3d.core import PandaNode, NodePath, Camera, TextNode


from panda3d.core import lookAt
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import Texture, GeomNode
from panda3d.core import PerspectiveLens
from panda3d.core import CardMaker
from panda3d.core import Light, Spotlight
from panda3d.core import TextNode
from panda3d.core import LVector3


NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\tSomething\n" \
         "\n"

ENVIRONMENT   = "models/world"
RALPH_ACTOR   = "models/ralph"
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
        #Set up the window, camera, etc.
        ShowBase.__init__(self)

        #Set the background color to black
        self.win.setClearColor((0, 0, 0, 1))

        # This is used to store which keys are currently pressed.
        self.key_map = {
            "left":         0,
            "right":        0,
            "forward":      0,
            "cam-left":     0,
            "cam-right":    0}

        #Post the Instruction
        self.title = add_title( "Panda 3D Demo")

        #Instructions
        self.inst1 = add_instructions(0.06, "[ESC]: Quit")
        self.inst2 = add_instructions(0.12, "[Left Arrow]: Rotate Left")
        self.inst3 = add_instructions(0.18, "[Right Arrow]: Rotate Ralph Right")
        self.inst4 = add_instructions(0.24, "[Up Arrow]: Run Ralph Forward")
        #self.inst6 = add_instructions(0.30, "[A]: Rotate Camera Left")
        #self.inst7 = add_instructions(0.36, "[S]: Rotate Camera Right")

        #Load the Environment Model
        self.environ = self.loader.loadModel(ENVIRONMENT)
        #Reparent the model to the render controller
        self.environ.reparentTo(render)


        #Apply scale and position transform on the model
        #self.environ.setScale(0.25, 0.25, 0.25)
        #self.environ.setPos(-8, 42, 0)

        #Create the Main Character
        #Load and transform the panda actor
        ralph_start_pos = self.environ.find("**/start_point").getPos()
        self.ralph = Actor( RALPH_ACTOR,
                            RALPH_ACTIONS)

        #self.ralph.setScale(0.005, 0.005, 0.005)
        self.ralph.reparentTo(render)
        #Loop it's animation
        self.ralph.setScale(0.2)
        self.ralph.setPos(ralph_start_pos + (0, 0, 0.5))
        #self.ralph.loop("walk")

        #Create a floater object, which floats 2 units above rlaph. We use this as a target for the camera to look at
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.ralph)
        #2 Units above Ralph
        self.floater.setZ(2.0)

        #Configure the Camera
        #Add the spin camera taks procedure to the taks manager
        #self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")


        #Accept certain control keys
        self.accept("escape",           sys.exit)
        self.accept("arrow_left",       self.set_key, ["left",      True])
        self.accept("arrow_right",      self.set_key, ["right",     True])
        self.accept("arrow_up",         self.set_key, ["forward",   True])
        self.accept("a",                self.set_key, ["cam-left",  True])
        self.accept("s",                self.set_key, ["cam-right", True])
        self.accept("arrow_left-up",    self.set_key, ["left",      False])
        self.accept("arrow_right-up",   self.set_key, ["right",     False])
        self.accept("arrow_up-up",      self.set_key, ["forward",   False])
        self.accept("a-up",             self.set_key, ["cam-left",  False])
        self.accept("s-up",             self.set_key, ["cam-right", False])

        #Game States
        taskMgr.add(self.move, "moveTask")
        self.is_moving = False

        self.disableMouse()
        self.camera.setPos(self.ralph.getX(), self.ralph.getY() + 10, 2)
        self.camera.lookAt(self.floater)



        '''
        Detect the height of hte terrain by creating a collision ray and casting it down towards the terrain.

        One ray will start above ralph's head and the other will start above the camera.
        A ray may hit the terrain, or it may hit a rock or a tree.
        If it hits the terrain we ca ndetect the height.

        If it hits anything else, we rule that the move is illegal.
        '''
        self.cTrav = CollisionTraverser()

        #Create a vector, it's location is at the top of ralph's head
        self.ralph_ground_ray = CollisionRay()
        self.ralph_ground_ray.setOrigin(0, 0, 9)                # Top of ralph's head
        self.ralph_ground_ray.setDirection(0, 0, -1)            # Points -Z axis

        #Create a Collision node
        self.ralph_ground_col = CollisionNode('ralph_ray')      # Give the node a name
        self.ralph_ground_col.addSolid(self.ralph_ground_ray)   # the vector from ralph's head to the ground is solid
        self.ralph_ground_col.setFromCollideMask(CollideMask.bit(0))    # ??
        self.ralph_ground_col.setIntoCollideMask(CollideMask.allOff())  # ?? This seems like it defines the behavior of ray
        self.ralph_ground_col_np = self.ralph.attachNewNode(self.ralph_ground_col)  #Attach the ray to ralph
        self.ralph_ground_handler = CollisionHandlerQueue()     #I think that when a collision occurs it sends through this
        self.cTrav.addCollider(self.ralph_ground_col_np, self.ralph_ground_handler)    #Attach the collision

        '''
        Attach the a camera ray to the camera
        '''
        self.cam_ground_ray = CollisionRay()
        self.cam_ground_ray.setOrigin(0, 0, 9)
        self.cam_ground_ray.setDirection(0, 0, -1)
        self.cam_ground_col = CollisionNode("camera_ray")
        self.cam_ground_col.addSolid(self.cam_ground_ray)
        self.cam_ground_col.setFromCollideMask(CollideMask.bit(0))
        self.cam_ground_col.setIntoCollideMask(CollideMask.allOff())
        self.cam_ground_col_np = self.camera.attachNewNode(self.cam_ground_col)
        self.cam_ground_handler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.cam_ground_col_np, self.cam_ground_handler)

        #Uncomment the following lines to view the rays
        self.ralph_ground_col_np.show()
        self.cam_ground_col_np.show()

        #Uncomment this line to show a visual representation of the Collision occuring
        self.cTrav.showCollisions(render)


        # Create some lighting
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor((0.3, 0.3, 0.3, 1))
        directional_light = DirectionalLight("directional_light")
        directional_light.setDirection((-5, -5, -5))
        directional_light.setColor((1, 1, 1, 1,))
        directional_light.setSpecularColor((1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambient_light))
        render.setLight(render.attachNewNode(directional_light))



        #Add Cube
        X_OFFSET = 0
        Y_OFFSET = -3
        Z_OFFSET = 1

        CUBE_SIZE = 2

        x, y, z = ralph_start_pos
        x += X_OFFSET
        y += Y_OFFSET
        z += Z_OFFSET

        #make_cube(x, y, z, CUBE_SIZE)

    def set_key(self, key, value):
        self.key_map[key] = value

    def move(self, task):
        dt = globalClock.getDt()
        #print "DT: %f" % dt
        
        #****: Movement
        #Get Ralph's position before we do anything to it
        start_pos = self.ralph.getPos()

        #User wants to turn
        if self.key_map["left"]:
            self.ralph.setH(self.ralph.getH() + 300 * dt)
        if self.key_map["right"]:
            self.ralph.setH(self.ralph.getH() - 300 * dt)

        #Perform a move forward
        if self.key_map["forward"]:
            self.ralph.setY(self.ralph, -25 * dt)
        

        #****: Animation
        if self.key_map["forward"] or self.key_map["left"] or self.key_map["right"]:
            if not self.is_moving:
                self.ralph.loop("run")
                self.is_moving = True

        else:
            if self.is_moving:
                self.ralph.stop()
                self.ralph.pose("walk", 5)
                self.is_moving = False


        #****: Camera Movement
        if self.key_map["cam-left"]:
            self.camera.setX(self.camera, -20 * dt)
        elif self.key_map["cam-right"]:
            self.camera.setX(self.camera, +20 * dt)

        #If the camera is too far from ralph, move it closer
        #If the camera is too close to ralph, move it farther
        camvec = self.ralph.getPos() - self.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            self.camera.setPos(self.camera.getPos() + camvec * (camdist - 10))
            camdist = 10.0
        if camdist < 5.0:
            self.camera.setPos(self.camera.getPos() - camvec * (5 - camdist))
            camdist - 5.0


        #****: Collision
        """
        Normally, we would have to call traverse() to check for collisions.

        However, the class ShowBase that we inherit from has a task to do this for us

        If we assign a CollisionTraverser to self.cTrav

        Adjust ralph's Z coordinate. If ralph's ray hit terrain update his Z.

        If it hit anything else, or didn't hit anything put him back where he was last frame.
        """

        entries = list(self.ralph_ground_handler.getEntries())
        entries.sort(key = lambda x: x.getSurfacePoint(render).getZ())
        #print "Entry count: %d" % len(entries)

        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            self.ralph.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.ralph.setPos(start_pos)

        #Keep the camera at one foot above the terrain or two feet above ralph, whichever is greater
        entries = list(self.cam_ground_handler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            self.camera.setZ(entries[0].getSurfacePoint(render).getZ() + 1.0)
        if self.camera.getZ() < self.ralph.getZ() + 2.0:
            self.camera.setZ(self.ralph.getZ() + 2.0)

        """
        The camera should look in rlaphs direction, but it should also try to stay horizontal so look at a
        floater which hovers above ralph's head
        """
        self.camera.lookAt(self.floater)
        return task.cont





# You can't normalize inline so this is a helper function
def normalized(*args):
    myVec = LVector3(*args)
    myVec.normalize()
    return myVec

def make_cube(x, y, z, size):
    squares = []
    squares.append(make_square(x - (size/2), y - (size/2), z - (size/2), x + (size/2), y - (size/2), z + (size/2)))
    squares.append(make_square(x - (size/2), y + (size/2), z - (size/2), x + (size/2), y + (size/2), z + (size/2)))
    squares.append(make_square(x - (size/2), y + (size/2), z + (size/2), x + (size/2), y - (size/2), z + (size/2)))
    squares.append(make_square(x - (size/2), y + (size/2), z - (size/2), x + (size/2), y - (size/2), z - (size/2)))
    squares.append(make_square(x - (size/2), y - (size/2), z - (size/2), x - (size/2), y + (size/2), z + (size/2)))
    squares.append(make_square(x + (size/2), y - (size/2), z - (size/2), x + (size/2), y + (size/2), z + (size/2)))

    snode = GeomNode('square')
    for s in squares:
        snode.addGeom(s)

    cube = render.attachNewNode(snode)
    cube.setTwoSided(True)

def make_square(x1, y1, z1, x2, y2, z2):
    format = GeomVertexFormat.getV3n3cpt2()
    vdata = GeomVertexData('square', format, Geom.UHDynamic)

    vertex   = GeomVertexWriter(vdata, 'vertex')
    normal   = GeomVertexWriter(vdata, 'normal')
    color    = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    if x1 != x2:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y1, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y2, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y2 - 1, 2 * z2 - 1))

    else:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y2, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y1, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z2 - 1))

    # adding different colors to the vertex for visibility
    color.addData4f(1.0, 0.0, 0.0, 1.0)
    color.addData4f(0.0, 1.0, 0.0, 1.0)
    color.addData4f(0.0, 0.0, 1.0, 1.0)
    color.addData4f(1.0, 0.0, 1.0, 1.0)

    texcoord.addData2f(0.0, 1.0)
    texcoord.addData2f(0.0, 0.0)
    texcoord.addData2f(1.0, 0.0)
    texcoord.addData2f(1.0, 1.0)

    # Quads aren't directly supported by the Geom interface
    # you might be interested in the CardMaker class if you are
    # interested in rectangle though
    tris = GeomTriangles(Geom.UHDynamic)
    tris.addVertices(0, 1, 3)
    tris.addVertices(1, 2, 3)

    square = Geom(vdata)
    square.addPrimitive(tris)
    return square



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

