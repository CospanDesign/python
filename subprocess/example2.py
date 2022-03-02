#! /usr/bin/env python3

# Copyright (c) 2017 Dave McCoy (dave.mccoy@cospandesign.com)
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
import subprocess

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


    print ("Wait for the process to end")
    proc = subprocess.Popen(["cat"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    output, errors = proc.communicate(input = "Hello")
    proc.wait()
    print (output)
    print(errors)

    print ("Poll the process")
    proc = subprocess.Popen(["cat"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    output, errors = proc.communicate(input = "Hello")
    while (proc.poll() is None):
        print ("Waiting...")
    print (output)
    print(errors)

    print ("Run a bash script")
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test.sh"))
    print ("Script Path: %s" % script_path)
    proc = subprocess.Popen([script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    output, errors = proc.communicate(input = "Hello")
    while (proc.poll() is None):
        print ("Waiting...")
    print (output)
    print(errors)






if __name__ == "__main__":
    main(sys.argv)


