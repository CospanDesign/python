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
import cv2
import numpy as np

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

NAME = os.path.basename(os.path.realpath(__file__))
IMAGE_PATH = "data/art.png"

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\tSomething\n" \
         "\n"

DEFAULT_ROTATION = 275.0
DEFAULT_SCALE = 1.0

def rotate_sub_image(image, sub_start_x, sub_start_y, sub_width, sub_height, angle, scale, debug=False):
    sub_center = (sub_width / 2, sub_height / 2)
    rot_mat = gen_rot_mat(sub_center, angle, scale)
    # generate map
    image_map = np.zeros((2, sub_height, sub_width))
    for y in range(sub_height):
        for x in range(sub_width):
            image_map[0][y][x], image_map[1][y][x] = calc_movement(image, start_pos_x + x, start_pos_y + y)

    print ("Image Map: %s" % str(image_map))

def calc_movement(m, start_pos_x, start_pos_y):
    #print ("Start Position: %d, %d" % (start_pos_x, start_pos_y))
    print ("Start Position: %d, %d" % (start_pos_x, start_pos_y))
    new_pos_x  = (start_pos_x * m[0][0] + start_pos_y * m[0][1]) + m[0][2]
    new_pos_y  = (start_pos_x * m[1][0] + start_pos_y * m[1][1]) + m[1][2]
    new_pos_x  -= start_pos_x
    new_pos_y  -= start_pos_y
    print ("%f, %f ->  %f, %f" % (start_pos_x, start_pos_y, new_pos_x, new_pos_y))
    return (new_pos_x, new_pos_y)

def gen_rot_mat(center, angle, scale):
    alpha = scale * np.cos(angle * np.pi / 180)
    beta = scale * np.sin(angle * np.pi / 180)
    cx = (1 - alpha) * center[0] - beta * center[1]
    cy = beta * center[0] + (1 - alpha) * center[1]
    rot_mat = [ [ alpha, beta,  cx],
                [-beta,  alpha, cy]]
    return rot_mat

   

def rotate_image(image, angle, scale = 1.0, debug=False):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    #print ("Image Center: %s" % str(image_center))
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, scale)
    print ("CV Rotation Matrix: \n%s\n" % str(rot_mat))
    rm = gen_rot_mat(image_center, angle, scale)
    print ("MY Rotation Matrix: \n%s\n" % str(rm))

    print ("Image Center: %d x %d" % (image_center[0], image_center[1]))
    print ("Rotation \n%s" % (str(rot_mat)))
    print ("Image Shape: %d x %d" % (image.shape[1], image.shape[0]))
    #start_pos_x = -1 * image.shape[1] // 2
    #start_pos_y = -1 * image.shape[0] // 2
    start_pos_x = 0
    start_pos_y = 0
    new_pos_x, new_pos_y = calc_movement(rot_mat, start_pos_x, start_pos_y)


    start_pos_x = 0
    start_pos_y = 480
    calc_movement(rot_mat, start_pos_x, start_pos_y)
    image = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)

    # Vertical Middle of the image in red
    height, width, channels = image.shape

    image = cv2.line(image, (width // 2,  0),  (width // 2 , height), (255, 0, 0), 1, 1)
    image = cv2.line(image, (0,  height // 2), (width, height // 2),  (255, 0, 0), 1, 1)
    image = cv2.circle(image, (width // 2, height // 2), radius=0, color=(0, 0, 255), thickness = 4)
    offset = 40
    image = cv2.putText(image,
                        "%d, %d" % (width // 2, height // 2),
                         ((width // 2) + offset, (height // 2) + offset),
                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                         2,
                         cv2.LINE_AA)

    image = cv2.line( image,
                      (int(new_pos_x), 0), (int(new_pos_x), height),
                      (0, 0, 255),
                      1,
                      1)

    image = cv2.line( image,
                      (0, int(new_pos_y)), (width, int(new_pos_y)),
                      (0, 0, 255),
                      1,
                      1)

    return image

def add_grid_to_image(image, grid_x_size, grid_y_size):
    height, width, channels = image.shape
    for x in range (0, width - 1, grid_x_size):
        image = cv2.line(image, (x, 0), (x, height), (0, 255, 0), 1, 1)

    for y in range (0, height - 1, grid_y_size):
        image = cv2.line(image, (0, y), (width, y),  (0, 255, 0), 1, 1)

    return image

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

    parser.add_argument("-r", "--rotation",
                        nargs=1,
                        default=["%s" % DEFAULT_ROTATION])

    parser.add_argument("-s", "--scale",
                        nargs=1,
                        default=["%s" % DEFAULT_SCALE])


    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    args = parser.parse_args()
    print ("Running Script: %s" % NAME)

    rotation = float(args.rotation[0])
    scale = float(args.scale[0])
    print ("Rotation: %f, Scale: %f" % (rotation, scale))


    if args.debug:
        print ("test: %s" % str(args.test[0]))

    src = cv2.imread(IMAGE_PATH)
    window_name = "Image"
    #image = cv2.rotate(src, cv2.ROTATE_90_CLOCKWISE)
    image = rotate_image(src, rotation, scale, debug = args.debug)
    #image = add_grid_to_image(image, 20, 20)

    cv2.imshow(window_name, image)
    cv2.waitKey(0)

if __name__ == "__main__":
    main(sys.argv)


