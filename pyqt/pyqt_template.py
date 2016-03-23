#! /usr/bin/env python

# Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)
#
# NAME is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NAME is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NAME; If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import argparse
from PyQt4 import QtGui

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\tSomething\n" \
         "\n"

GUI_WIDTH = 640
GUI_HEIGHT = 480

TITLE = "Hello World"

class Example(QtGui.QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.resize(GUI_WIDTH, GUI_HEIGHT)
        self.setWindowTitle(TITLE)
        
        #Make a Button
        self.button = QtGui.QPushButton("Push Me!")
        self.button.clicked.connect(self.button_clicked)
        
        #Add a Layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel("Hello"))
        layout.addWidget(self.button)

        #Set the gui's layout
        self.setLayout(layout)
        #Show the layout
        self.show()

    def button_clicked(self):
        print "Button Clicked"

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

    app = QtGui.QApplication(sys.argv)
    gui = Example()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv)


