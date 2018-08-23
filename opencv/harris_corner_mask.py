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
import argparse
import numpy as np
import cv2


KERNEL_ROW_COUNT = 5
KERNEL_ROW_HALF_COUNT = (KERNEL_ROW_COUNT - 1) / 2

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

DEFAULT_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "test_1080p.bmp"))
NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\tSomething\n" \
         "\n"

def hc(filename, debug = False):
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    #dst = cv2.cornerHarris(gray, 3, 3, 0.04)
    dst = cv2.cornerHarris(gray, 3, 3, 0.04)


    #m = np.zeros((img.shape[0], KERNEL_ROW_COUNT))
    nms = np.zeros((img.shape[0], img.shape[1]))






    gdst = dst.copy()

    print ("Min Value: %f" % gdst.min())
    print ("Max Value: %f" % gdst.max())


    if (gdst.min() < 0):
        gdst = gdst - gdst.min()

    print ("Min Value: %f" % gdst.min())
    print ("Max Value: %f" % gdst.max())


    gdst = gdst / gdst.max()
    gdst = 255 * gdst


    rows = gdst.shape[0]
    cols = gdst.shape[1]
    print ("Image Shape: %d, %d\n" % (rows, cols))

    threshold = 100
    max_val = False
    show_patch = True

    #Perform Non Maximum Suppression
    for i in range(rows):
        for j in range(cols):
            #m[i][j] = gdst[i][j]

            if ((i > KERNEL_ROW_COUNT) and ((i < (rows - KERNEL_ROW_COUNT)))) and ((j > KERNEL_ROW_COUNT) and ((j < (cols - KERNEL_ROW_COUNT)))):
                #Valid Values
                cpx = j - KERNEL_ROW_HALF_COUNT
                cpy = i - KERNEL_ROW_HALF_COUNT
                center_value = gdst[cpy, cpx]
                nms[cpy][cpy] = 0
                max_val = True



                for l in range(cpy - KERNEL_ROW_HALF_COUNT, cpy + KERNEL_ROW_HALF_COUNT + 1):
                    for k in range(cpx - KERNEL_ROW_HALF_COUNT, cpx + KERNEL_ROW_HALF_COUNT + 1):
                        if center_value < gdst[l, k]:
                            max_val = False
                            break
                    if not max_val:
                        break

                if max_val and center_value > threshold:
                    print("Feature Found at: %4d, %4d, in patch: %4d,%4d -> %4d,%4d" % (cpx, cpy, cpx - KERNEL_ROW_HALF_COUNT, cpy - KERNEL_ROW_HALF_COUNT, cpx + KERNEL_ROW_HALF_COUNT, cpy + KERNEL_ROW_HALF_COUNT))
                    nms[i][j] = center_value
                    show_patch = True

                if show_patch:
                    show_patch = False
                    for l in range(cpy - KERNEL_ROW_HALF_COUNT, cpy + KERNEL_ROW_HALF_COUNT + 1):
                        for k in range(cpx - KERNEL_ROW_HALF_COUNT, cpx + KERNEL_ROW_HALF_COUNT + 1):
                            print "%4d " % gdst[l, k],

                        print("\n")

            else:
                #Border Conditions
                nms[i][j] = 0






    #out_img = gdst.astype(np.uint8)
    thresh_img = gdst.astype(np.uint8)
    for i in range(rows):
        for j in range(cols):
            if thresh_img[i][j] < threshold:
                thresh_img[i][j] = 0

    out_img = nms.astype(np.uint8)

    #print ("Min Value: %d" % out_img.min())
    #print ("Max Value: %d" % out_img.max())
    out_img = cv2.applyColorMap(out_img, cv2.COLORMAP_JET)
    cv2.imshow('color map', out_img)
    if cv2.waitKey() & 0xFF == 27:
        cv2.destroyAllWindows()

    filename = "thres_%d_nms_%d.png" % (threshold, KERNEL_ROW_COUNT)
    cv2.imwrite(filename, nms)
    filename = "thres_%d_nms_0.png" % (threshold)
    cv2.imwrite(filename, thresh_img)


    '''
    for i in range(1, 10):
        adst = dst.copy()
        aimg = img.copy()
        #dst = cv2.dilate(dst, None)
        aimg[adst > 0.01 * i * adst.max()] = [0, 255, 0]

        cv2.imshow('Harris Corners', aimg)
        #cv2.imshow('DST', dst)
        if cv2.waitKey(1000) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
    '''

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

    parser.add_argument("-i", "--image",
                        nargs=1,
                        default=[DEFAULT_FILENAME])

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    args = parser.parse_args()
    print "Running Script: %s" % NAME


    if args.debug:
        print "image: %s" % str(args.image[0])

    hc(args.image[0], args.debug)

if __name__ == "__main__":
    main(sys.argv)


