#! /usr/bin/env python

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
import logging
import argparse
import numpy as np
import cv2
from matplotlib import pyplot as plt
from matplotlib.figure import SubplotParams
from math import *
from klt import KLT


NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG      = "\n" \
              "\n" \
              "Examples:\n" \
              "\tSomething\n" \
              "\n"

DEFAULT_START_FEATURE           = 25
PYRAMID_DEPTH                   = 2
ROTATION_ANGLE                  = 0
VIDEO_FILE                      = "data/videoplayback.mp4"

DRAW_PATCH_SCALE                = 100

def draw_patch_callback(warped_patch, image_patch):
    print ("in draw patch callback")
    size = warped_patch.shape
    height = size[0]
    width = size[1]

    wrp_scale = np.kron(warped_patch, np.ones((DRAW_PATCH_SCALE, DRAW_PATCH_SCALE)))
    img_scale = np.kron(image_patch, np.ones((DRAW_PATCH_SCALE, DRAW_PATCH_SCALE)))

    #Create a place to put the final image
    img_patches = np.zeros((height * DRAW_PATCH_SCALE, width * DRAW_PATCH_SCALE * 2), dtype=np.uint8)

    for y in range(0, DRAW_PATCH_SCALE * height):
        for x in range(0, DRAW_PATCH_SCALE * width):
            img_patches[y][x + (width * DRAW_PATCH_SCALE * 0)] = wrp_scale[y][x]
            img_patches[y][x + (width * DRAW_PATCH_SCALE * 1)] = img_scale[y][x]

    im_color = cv2.applyColorMap(img_patches, cv2.COLORMAP_JET)
    cv2.imshow("Main", im_color)
    #cv2.imshow("Main", img_patches)
    #cv2.waitKey(10) & 0xFF == ord('q')
    cv2.waitKey(33) & 0xFF == ord('q')
    #cv2.waitKey()

def draw_images_callback(template_image, current_image):
    size = template_image.shape
    pass

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

    log = logging.getLogger("klt")
    log.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)

    # add ch to logger
    log.addHandler(ch)
    log.info("Started")

    feature_select = "%s" % DEFAULT_START_FEATURE
    angle = "%s" % ROTATION_ANGLE
    pyramid_depth = "%s" % PYRAMID_DEPTH

    parser.add_argument("-v", "--video",
                        nargs=1,
                        default=[VIDEO_FILE])
    parser.add_argument("-f", "--feature",
                        nargs=1,
                        default=[feature_select])

    parser.add_argument("-r", "--rotation",
                        nargs=1,
                        default=[angle])

    parser.add_argument("-p", "--pyramid",
                        nargs=1,
                        default=[pyramid_depth])

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    parser.add_argument("--display",
                                    action="store_true",
                                    help="Display View")

    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)

    #log.debug("Features: %s" % str(args.feature[0]))
    cap = cv2.VideoCapture(args.video[0])
    log.info("Opened video file: %s" % args.video[0])

    pyramid_depth = int(args.pyramid[0])
    log.debug("Pyramid Depth: %d" % pyramid_depth)

    klt = KLT(  draw_patch_callback = draw_patch_callback,
                pyramid_depth = pyramid_depth,
                debug = args.debug)

    count = 0
    ret, image = cap.read()
    log.debug("Shape of image: %s" % str(image.shape))
    #klt.new_image(image)
    while ret and (count < 2):
        klt.track(image)
        ret, image = cap.read()
        count += 1


if __name__ == "__main__":
    main(sys.argv)

