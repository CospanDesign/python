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
from matplotlib import pyplot as plt
from matplotlib.figure import SubplotParams
from math import *


cap = cv2.VideoCapture("data/videoplayback.mp4")

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
PATCH_SIZE                      = 3
PYRAMID_DEPTH                   = 5
MATCH_THRESHOLD                 = 0.3
CIRCLE_SIZE                     = 10
#ENERGY_THRESHOLD                = 0.1
ENERGY_THRESHOLD                = 0.0
ROTATION_ANGLE                  = 0
MAX_CORNERS                     = 100
PYRAMID_POS                     = PYRAMID_DEPTH - 1

RED   = (0xFF, 0x00, 0x00)
GREEN = (0x00, 0xFF, 0x00)
BLUE  = (0x00, 0x00, 0xFF)


# params for ShiTomasi corner detection
feature_params = dict(  maxCorners      = MAX_CORNERS,
                        qualityLevel    = 0.3,
                        minDistance             = 7,
                        blockSize       = 7 )

# Parameters for lucas kanade optical flow
lk_params = dict(       winSize         = (15,15),
                        maxLevel        = 2,
                        criteria        = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

subpix_params = dict(   zeroZone        = (-1,-1),
                        winSize         = (10,10),
                        criteria        = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS,20,0.03))


INITIAL_WARP =          [[cos(radians(ROTATION_ANGLE)), -sin(radians(ROTATION_ANGLE)), 0],
                         [sin(radians(ROTATION_ANGLE)),  cos(radians(ROTATION_ANGLE)), 0]]

def get_patch(img, point, patch_size):
    np.zeros(shape = (patch_size, patch_size), dtype=np.uint8)
    patch = np.zeros(shape = (patch_size, patch_size), dtype=np.uint8)
    for y in range((int(patch_size / 2) * -1), int(patch_size / 2) + 1):
        for x in range((int(patch_size / 2) * -1), int(patch_size / 2) + 1):
            py = y + int(patch_size / 2)
            px = x + int(patch_size / 2)
            patch[px][py] = img[point[0] + y][point[1] + x]
    return patch


def apply_affine_image_warp(in_patch, in_point, transform=[[0, 0, 0], [0, 0, 0]], energy_threshold=ENERGY_THRESHOLD):

    energy_min = 1.0 - energy_threshold

    height  = in_patch.shape[0]
    y_start = - (height / 2)
    y_end   =   (height / 2)

    width   = in_patch.shape[1]
    x_start = - (width / 2)
    x_end   =   (width / 2)


    weight_patch = np.zeros(shape = (height, width), dtype=np.float32)
    #out_patch = in_patch
    out_patch = np.zeros(shape = (height, width), dtype=np.uint8)

    #First apply the translation to the point under question
    out_point = [int(in_point[0] + transform[0][2]),
                 int(in_point[1] + transform[1][2])]

    #Apply the rotation, shearing and scaling to the in_path
    for y in range (y_start, y_end + 1):
        for x in range (x_start, x_end + 1):
            x_in = x + 1
            y_in = y + 1

            #Find the location after the rotation and scaling
            x_out = transform[0][0] * x + transform[0][1] * y
            y_out = transform[1][0] * x + transform[1][1] * y
            #Now we have the weight of how much we should put in the output image
            # so if you have 50% of 0,0 going into 1,0 then we have 0.5 * value into 1,0

            #Go through each of the output coordinates
            x_out_pos = x_out + 1
            y_out_pos = y_out + 1

            for yout in range (0, height):
                for xout in range(0, width):
                    #x_pos_diff = x_out_pos - xout
                    #y_pos_diff = y_out_pos - yout

                    x_energy = 1.0 * abs(x_out_pos - xout)
                    y_energy = 1.0 * abs(y_out_pos - yout)
                    if (x_energy < energy_min) and (y_energy < energy_min):
                        x_energy = 1.0 - x_energy
                        y_energy = 1.0 - y_energy
                        cell_energy = x_energy * y_energy
                        out_patch[yout][xout] += int(cell_energy * in_patch[y_in][x_in])
                        weight_patch[yout][xout] += cell_energy
                        print ("% 2dx% 2d -> % 2dx% 2d Output pos: % 2dx% 2d: Energy: %f: %d -> %d" %
                                (x, y,
                                 xout - 1, yout - 1,
                                 xout - 1, yout - 1,
                                 cell_energy,
                                 in_patch[y_in][x_in], 
                                out_patch[yout][xout]))

    for yout in range(0, height):
        for xout in range(0, width):
            print ("Weidth: % 2dx% 2d: %f" % (yout, xout, weight_patch[yout][xout]))
            out_patch[yout][xout] = int(out_patch[yout][xout] / weight_patch[yout][xout])

    return out_point, out_patch

def get_gradiants(gray_image, ypos, xpos):
    #For all elements in a patch, find the gradiant of x, y and xy
    
    #Set the position of starting of region of interest to be half a patch before (x and y)
    ystart = ypos - int(PATCH_SIZE / 2)
    xstart = xpos - int(PATCH_SIZE / 2)
    
    #Iterate through all the elements in both Y and X region to determine the gradiant of X, Gradiant of Y and XY
    gx = gray_image[y + 0][x + 0] + \
         gray_image[y + 1][x + 0] + \
         gray_image[y + 2][x + 0] - \
         gray_image[y + 0][x + 2] - \
         gray_image[y + 1][x + 2] - \
         gray_image[y + 2][x + 2]
    gy = gray_image[y + 0][x + 0] + \
         gray_image[y + 0][x + 1] + \
         gray_image[y + 0][x + 2] - \
         gray_image[y + 2][x + 0] - \
         gray_image[y + 2][x + 1] - \
         gray_image[y + 2][x + 2]
    gxy = gx * gy
    return (gx, gy, gxy)

def find_error_coefficents(in_patch, out_patch):
    error = 0

    sigma_x = 0
    sigma_y = 0
    sigma_xy = 0
    sigma_xt = 0
    sigma_yt = 0

    h_matrix = np.zeros(shape(AFFINE_SIZE, AFFINE_SIZE), dtype=float)

    for y in range(in_patch.shape[0]):
        for x in range(in_patch.shape[1]):
            sigma_x += in_patch[y][x]

            #First Row
            h_matrix[0, 0] = Ix_sqrd * (px * px)
            h_matrix[0, 1] = Ix_sqrd * (px * py)
            h_matrix[0, 2] = Ix_sqrd * (px)
            h_matrix[0, 3] = Ixy     * (px * px)
            h_matrix[0, 4] = Ixy     * (px * py)
            h_matrix[0, 5] = Ixy     * (px)
            
            #Second Row
            h_matrix[0, 0] = Ix_sqrd * (px * py)
            h_matrix[0, 1] = Ix_sqrd * (py * py)
            h_matrix[0, 2] = Ix_sqrd * (py)
            h_matrix[0, 3] = Ixy     * (px * py)
            h_matrix[0, 4] = Ixy     * (py * py)
            h_matrix[0, 5] = Ixy     * (py)
            
            #Third Row
            h_matrix[0, 0] = Ix_sqrd * (px)
            h_matrix[0, 1] = Ix_sqrd * (py)
            h_matrix[0, 2] = Ix_sqrd
            h_matrix[0, 3] = Ixy     * (px)
            h_matrix[0, 4] = Ixy     * (py)
            h_matrix[0, 5] = Ixy
            
            #Fourth Row
            h_matrix[0, 0] = Ixy     * (px * px)
            h_matrix[0, 1] = Ixy     * (px * py)
            h_matrix[0, 2] = Ixy     * (px)
            h_matrix[0, 3] = Iy_sqrd * (px * px)
            h_matrix[0, 4] = Iy_sqrd * (px * py)
            h_matrix[0, 5] = Iy_sqrd * (px)
            
            #Fifth Row
            h_matrix[0, 0] = Ixy     * (px * py)
            h_matrix[0, 1] = Ixy     * (py * py)
            h_matrix[0, 2] = Ixy     * (py)
            h_matrix[0, 3] = Iy_sqrd * (px * py)
            h_matrix[0, 4] = Iy_sqrd * (py * py)
            h_matrix[0, 5] = Iy_sqrd * (py)
            
            #Sixth Row
            h_matrix[0, 0] = Ixy     * (px)
            h_matrix[0, 1] = Ixy     * (py)
            h_matrix[0, 2] = Ixy
            h_matrix[0, 3] = Iy_sqrd * (px)
            h_matrix[0, 4] = Iy_sqrd * (py)
            h_matrix[0, 5] = Iy_sqrd

    return error

def klt_track(image,
              prev_gray,
              gray,
              features,
              patch_size = PATCH_SIZE,
              pyramid_depth = PYRAMID_DEPTH,
              match_threshold = MATCH_THRESHOLD,
              feature_pos = 0,
              angle = INITIAL_WARP,
              pyramid_pos = PYRAMID_POS,
              energy_threshold=ENERGY_THRESHOLD,
              debug = False):

    #Create the Pyramids
    pyramids = []
    ppyramids = []
    for i in range(pyramid_depth):
        if (i == 0):
            pyramids.append(gray)
            ppyramids.append(prev_gray)
        else:
            pyramids.append(cv2.pyrDown(pyramids[i - 1]))
            ppyramids.append(cv2.pyrDown(ppyramids[i - 1]))


    point = features[feature_pos][0];
    pyramid_points = [0] * pyramid_depth

    if debug:
        fig = cv2.figure(figsize=(10, 15))

    for i in range (pyramid_depth):

        r = (pyramid_depth - 1) - i
        scale = 2 ** r
        x = int(point[0] / scale)
        y = int(point[1] / scale)
        pyramid_points[r] = [x, y]
        #print "Pyramid Points: %d: (%d, %d)" % (r, x, y)

        if debug:
            pos = (i * 2) + 1
            a = fig.add_subplot(pyramid_depth, 2, pos)
            img = cv2.cvtColor(ppyramids[-1 + (-1 * i)], cv2.COLOR_GRAY2RGB)
            cv2.circle(img, (x, y), (CIRCLE_SIZE / scale), RED, -1)
            cv2.imshow(img, interpolation='none')
            a.set_title("Template: %d" % (r + 1))
         
            pos += 1
            a = fig.add_subplot(pyramid_depth, 2, pos)
            img = cv2.cvtColor(pyramids[-1 + (-1 * i)], cv2.COLOR_GRAY2RGB)
            cv2.imshow(img, interpolation='none')
            a.set_title("Image: %d" % (r + 1))

    #print "Find patch from template image"
    #print "Patch at top of pyramid (As seen on template '%d')" % pyramid_depth

    #pyramid_pos = 4
    in_point = pyramid_points[pyramid_pos]
    in_template_image = ppyramids[pyramid_pos]
    in_dut_image = pyramids[pyramid_pos]
    in_patch = get_patch(in_template_image, in_point, patch_size)

    #Initial Transform is no movement
    transform = [[cos(radians(angle)), -sin(radians(angle)), 0],
                 [sin(radians(angle)),  cos(radians(angle)), 0]]

    out_point, xfrm_patch = apply_affine_image_warp(in_patch, in_point, transform, energy_threshold)
    dut_patch = get_patch(in_dut_image, out_point, patch_size)

    patch_width = PATCH_SIZE
    patch_height = PATCH_SIZE
    patch_scale = 100

    #in_patch.resize             ((patch_width * patch_scale, patch_height * patch_scale))
    #xfrm_patch.resize ((patch_width * patch_scale, patch_height * patch_scale))
    #dut_patch.resize      ((patch_width * patch_scale, patch_height * patch_scale))

    in_patch_scale        = np.kron(in_patch,     np.ones((patch_scale, patch_scale)))
    xfrm_patch_scale      = np.kron(xfrm_patch,   np.ones((patch_scale, patch_scale)))
    dut_patch_scale       = np.kron(dut_patch,    np.ones((patch_scale, patch_scale)))

    img_patches = np.zeros((patch_height * patch_scale, patch_width * patch_scale * 3), dtype=np.uint8)

    for y in range(0, patch_scale * patch_height):
        for x in range(0, patch_scale * patch_width):
            img_patches[y][x + (patch_width * patch_scale * 0)] = in_patch_scale[y][x]
            img_patches[y][x + (patch_width * patch_scale * 1)] = xfrm_patch_scale[y][x]
            img_patches[y][x + (patch_width * patch_scale * 2)] = dut_patch_scale[y][x]

    #img_patches = cv2.cvtColor(img_patches, cv2.CV_8UC1)
    im_color = cv2.applyColorMap(img_patches, cv2.COLORMAP_JET)
    #cv2.imshow("Main", img_patches)
    cv2.imshow("Main", im_color)

    #fig = cv2.figure(figsize=(10, 15))
    #a = fig.add_subplot(1, 3, 1)
    #cv2.imshow(in_patch, cmap="gray", interpolation='none')
    #XXX: cv2.imshow("Main Window", in_patch)
    #a.set_title("Template Patch")

    #a = fig.add_subplot(1, 3, 2)
    #cv2.imshow(xfrm_patch, cmap="gray", interpolation='none')
    #XXX: cv2.imshow("Main Window", xfrm_patch)
    #a.set_title("Template Patch Post Transform")

    #a = fig.add_subplot(1, 3, 3)
    #cv2.imshow(dut_patch, cmap="gray", interpolation='none')
    #XXX: cv2.imshow("Main Window", dut_patch)
    #a.set_title("DUT Patch")

    print ("Template Feature Point         (%d, %d) Template Original Patch:\n%s" %
        (in_point[0],  in_point[1],  str(in_patch)))
    print ("Template Transform Point Point (%d, %d) Template Transform Patch:\n%s" %
        (out_point[0], out_point[1], str(xfrm_patch)))
    print ("DUT Image Point                (%d, %d) DUT Patch:\n%s" %
        (out_point[0], out_point[1], str(dut_patch)))

    #error = find_patch_error(xfrm_patch, dut_patch)
    #print ("Error: %d" % error)


def update_klt(features, gray, prev_gray, image, feature_select, angle, pyramid_pos, energy_threshold, debug = False):
    print "Feature Count: %d" % len(features)

    if debug:
        cv2.imshow(image)
        cv2.title("All Features Found (Red is focused)")

    for point in features:
        cv2.circle( image,
                    (   int(point[0][0]),
                        int(point[0][1])),
                    CIRCLE_SIZE,GREEN,
                    -1)

    point = features[feature_select]
    cv2.circle(     image,
                    (
                        int(point[0][0]),
                        int(point[0][1])),
                    CIRCLE_SIZE,RED,
                    -1)
    klt_track(image,
              prev_gray,
              gray,
              features,
              patch_size = PATCH_SIZE,
              pyramid_depth = PYRAMID_DEPTH,
              match_threshold = MATCH_THRESHOLD,
              feature_pos = feature_select,
              pyramid_pos = pyramid_pos,
              angle = angle,
              energy_threshold=ENERGY_THRESHOLD,
              debug = False)


def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )
    feature_select = "%s" % DEFAULT_START_FEATURE
    angle = "%s" % ROTATION_ANGLE
    pyramid_pos = "%s" % PYRAMID_POS
    energy_threshold = "%s" % ENERGY_THRESHOLD
    parser.add_argument("-f", "--feature",
                        nargs=1,
                        default=[feature_select])

    parser.add_argument("-r", "--rotation",
                        nargs=1,
                        default=[angle])

    parser.add_argument("-e", "--energy",
                        nargs=1,
                        default=[energy_threshold])

    parser.add_argument("-p", "--pyramid",
                        nargs=1,
                        default=[pyramid_pos])

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    parser.add_argument("--display",
                                    action="store_true",
                                    help="Display View")


    args = parser.parse_args()
    print "Running Script: %s" % NAME

    if args.debug:
        print "feature: %s" % str(args.feature[0])

    feature_select = int(args.feature[0])
    angle = int(args.rotation[0])
    pyramid_pos = int(args.pyramid[0])
    energy_threshold = float(args.energy[0])


    ret, image = cap.read()
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gimage = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    # search for good points
    features = cv2.goodFeaturesToTrack(gray, **feature_params)

    # refine the corner locations
    cv2.cornerSubPix(gray,features, **subpix_params)

    prev_gray = gray
    #Track Features until we loose a few of them
    ret, image = cap.read()

    gray = cv2.cvtColor(image,cv2. COLOR_BGR2GRAY)
    while (True):
        update_klt(features, gray, prev_gray, gimage, feature_select, angle, pyramid_pos, energy_threshold, args.debug)

        angle += 5
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main(sys.argv)

