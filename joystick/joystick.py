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
import time
import select
import tty
import termios
import struct
import math
import argparse

from evdev import list_devices
from evdev import InputDevice
from evdev import InputDevice
from evdev import categorize
from evdev import ecodes



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


    print ("List Devices: %s" % str(list_devices()))

    devices = list_devices()
    device  = None
    for dpath in devices:
        print ("Openning: %s" % str(dpath))
        device = InputDevice(dpath)
        if device.name == "8BitDo SN30 Pro+":
            print ("Found 8BitDo SN30 Pro+")
            break
        del(device)
        device = None

    if device is None:
        print ("No Devices Found")
        return

    ins = [device.fd]
    outs = []
    exs = []


    quit = False
    while not quit:
        r, w, x = select.select(ins, outs, exs)
        for fd in r:
            if fd is device.fd:
                for event in device.read():
                    print (event)
                    #print ("Active Keys: %s" % device.active_keys(verbose=True))
                    #print ("Active Abs Pos: %s" % str(device.absinfo(ecodes.ABS_X)))
                    if event.type == ecodes.EV_KEY:
                        if event.code == ecodes.BTN_TR:
                            print ("Finished")
                            quit = True





    #print ("Device: %s" % str(device))
    #print ("Device Name: %s" % device.name)
    #for event in device.read_loop():
    #    #print ("Event: %s" % str(event))
    #    if event.type == ecodes.EV_KEY:
    #        print ("Keycode: %s" % event.code)
    #        if event.code == ecodes.BTN_TR:
    #            print ("Finished")
    #            break
    #        #if categorize(event).keycode[0] == "KEY_MENU":
    #        #    print ("Finished")
    #        #    break
    #    if event.type == ecodes.EV_ABS:
    #        pass

    #EVENT_SIZE = struct.calcsize("LhBB")
    #with open("/dev/input/js0", "rb") as f:
    #    ins = [f]
    #    outs = []
    #    exs = []
    #    while True:
    #        r, w, e = select.select(ins, outs, exs)
    #        for s in r:
    #            if s is f:
    #                ev = f.read(EVENT_SIZE)
    #                if args.debug: print (struct.unpack("LhBB", ev))
    #                (tv_msec, value, typ, num) = struct.unpack("LhBB", ev)

    #                if typ == 1:
    #                    print ("Digital: %d" % num)
    #                    if num == 2:
    #                        break

    #                if typ == 2:
    #                    v = float(value)
    #                    if num == 1:
    #                        print ("Left Stick  Forward/Back: %0.02f" % v)
    #                    if num == 4:
    #                        print ("Right Stick Forward/Back: %0.02f" % v)


if __name__ == "__main__":
    main(sys.argv)


