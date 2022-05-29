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

DEFAULT_ROTATION = 90.0
DEFAULT_SCALE = 1.0

def rotate_sub_image(image, sub_start_x, sub_start_y, sub_width, sub_height, angle, scale, linear_interpolate = False, debug=False):
    sub_center = (sub_width / 2, sub_height / 2)
    rot_mat = gen_rot_mat(sub_center, angle, scale)
    #print ("Sub Start: %d x %d, Sub Size: %d x %d" % (sub_start_x, sub_start_y, sub_width, sub_height))
    print ("Rotation Matrix: %s" % str(rot_mat))
    # generate map
    image_map = np.zeros((sub_height, sub_width, 2), np.float)
    for y in range(sub_height):
        for x in range(sub_width):
            #print ("x: %s sub_start_x: %s" % (str(x), str(sub_start_x)))
            #print ("y: %s sub_start_y: %s" % (str(y), str(sub_start_y)))
            image_map[y][x][0], image_map[y][x][1] = calc_movement(rot_mat, x, y)
            image_map[y][x][0] += sub_start_x
            image_map[y][x][1] += sub_start_y

    #print ("Image Map: %s" % str(image_map))
    #print ("Image Map[0][0]: %s" % str(image_map[0][0]))
    #new_image = np.zeros((sub_height, sub_width, 1), np.uint8)
    new_image = np.zeros((sub_height, sub_width, 1), dtype = "uint8")
    src_image = np.zeros((sub_height, sub_width, 1), dtype = "uint8")
    lb = np.zeros((2, 2), np.float)
    lbw = np.zeros((2, 2), np.float)
    image_width = image.shape[1]
    image_height = image.shape[0]
    #print ("Image Shape: %d x %d" % (image_width, image_height))
    #new_image = cv2.CreateMat(sub_height, sub_width, cv2.CV_8UC1)
    #new_image = np.CreateMat(sub_height, sub_width, cv2.CV_8UC1)
    for y in range(sub_height):
        for x in range(sub_width):
            new_x = image_map[y][x][0]
            new_y = image_map[y][x][1]

            fx = new_x - int(new_x)
            fy = new_y - int(new_y)
            ix = int(new_x)
            iy = int(new_y)

            #print ("X Map: %f -> %f, Y Map: %f -> %f" % (   x,
            #                                                new_x,
            #                                                y,
            #                                                new_y))

            if linear_interpolate:
                #lbw[0][0] = (1.0 - fy) * (1.0 - fx)  # x = 0, y = 0
                #lbw[0][1] = (      fy) * (1.0 - fx)
                #lbw[1][0] = (1.0 - fy) * (      fx)
                #lbw[1][1] = (      fy) * (      fx)
                xs = 1.0 - fx
                xe = fx
                ys = 1.0 - fy
                ye = fy

                xmt = 0
                xmb = 0

                #print ("LBW: %f  %f" % (lbw[0][0], lbw[0][1]))
                #print ("     %f  %f" % (lbw[1][0], lbw[1][1]))


                # 0, 0
                if (new_x + 0) < 0 or (new_x + 0) >= image_width or \
                   (new_y + 0) < 0 or (new_y + 0) >= image_height:
                    lb[0][0] = 0
                else:
                    lb[0][0] = image[iy + 0][ix + 0] * xs

                # 0, 1
                if (new_x + 1) < 0 or (new_x + 1) >= image_width or \
                   (new_y + 0) < 0 or (new_y + 0) >= image_height:
                    lb[0][1] = 0
                else:
                    lb[0][1] = image[iy + 0][ix + 1]  * xe

                xmt = lb[0][0] + lb[0][1]

                # 1, 0
                if (new_x + 0) < 0 or (new_x + 0) >= image_width or \
                   (new_y + 1) < 0 or (new_y + 1) >= image_height:
                    lb[1][0] = 0
                else:
                    lb[1][0] = image[iy + 1][ix + 0] * xs

                # 1, 1
                if (new_x + 1) < 0 or (new_x + 1) >= image_width or \
                   (new_y + 1) < 0 or (new_y + 1) >= image_height:
                    lb[1][1] = 0
                else:
                    lb[1][1] = image[iy + 1][ix + 1] * xe

                xmb = lb[1][0] + lb[1][1]

                new_image[y][x] = xmt * ys + xmb * ye


                #lbw[0][0] = (1.0 - fy) * (1.0 - fx)  # x = 0, y = 0
                #lbw[0][1] = (      fy) * (1.0 - fx)
                #lbw[1][0] = (1.0 - fy) * (      fx)
                #lbw[1][1] = (      fy) * (      fx)


                ## 0, 0
                #if (new_x + 0) < 0 or (new_x + 0) >= image_width or \
                #   (new_y + 0) < 0 or (new_y + 0) >= image_height:
                #    lb[0][0] = 0
                #else:
                #    lb[0][0] = image[iy + 0][ix + 0] * lbw[0][0]

                ## 0, 1
                #if (new_x + 1) < 0 or (new_x + 1) >= image_width or \
                #   (new_y + 0) < 0 or (new_y + 0) >= image_height:
                #    lb[0][1] = 0
                #else:
                #    lb[0][1] = image[iy + 0][ix + 1]  * lbw[0][1]

                ## 1, 0
                #if (new_x + 0) < 0 or (new_x + 0) >= image_width or \
                #   (new_y + 1) < 0 or (new_y + 1) >= image_height:
                #    lb[1][0] = 0
                #else:
                #    lb[1][0] = image[iy + 1][ix + 0] * lbw[1][0]

                ## 1, 1
                #if (new_x + 1) < 0 or (new_x + 1) >= image_width or \
                #   (new_y + 1) < 0 or (new_y + 1) >= image_height:
                #    lb[1][1] = 0
                #else:
                #    lb[1][1] = image[iy + 1][ix + 1] * lbw[1][1]

                #new_image[y][x] = lb[0][0] + lb[1][0] + lb[0][1] + lb[1][1]




            else:
                if new_x < 0 or new_x >= image.shape[1] or \
                   new_y < 0 or new_y >= image.shape[0]:
                    new_image[y][x] = 0
                else:
                    new_image[y][x] = image[iy][ix]

            src_image[y][x] = image[y][x]
    return src_image, new_image

def calc_movement(m, start_pos_x, start_pos_y):
    new_pos_x  = (start_pos_x * m[0][0] + start_pos_y * m[0][1]) + m[0][2]
    new_pos_y  = (start_pos_x * m[1][0] + start_pos_y * m[1][1]) + m[1][2]
    #print ("New Pos: %f, %f" % (new_pos_x, new_pos_y))
    return (new_pos_x, new_pos_y)

def gen_rot_mat(center, angle, scale):
    #alpha = scale * np.cos(angle * np.pi / 180)
    #beta = scale * np.sin(angle * np.pi / 180)
    #cx = (1 - alpha) * center[0] - beta * center[1]
    #cy = beta * center[0] + (1 - alpha) * center[1]
    #rot_mat = np.zeros((2, 3))
    #rot_mat[0][0] = alpha
    #rot_mat[0][1] = beta
    #rot_mat[0][2] = cx

    #rot_mat[1][0] = -beta
    #rot_mat[1][1] = alpha
    #rot_mat[1][2] = cy

    alpha = scale * np.cos(angle * np.pi / 180)
    beta =  scale * np.sin(angle * np.pi / 180)
    cx =      (((1 - alpha) * center[0] -      beta   * center[1]))
    cy =              (beta * center[0] + (1 - alpha) * center[1])
    rot_mat = np.zeros((2, 3))
    rot_mat[0][0] = alpha
    rot_mat[0][1] = beta
    rot_mat[0][2] = cx

    rot_mat[1][0] = (-beta)
    rot_mat[1][1] = alpha
    rot_mat[1][2] = cy
    return rot_mat

def cv_rotate_image(image, angle, scale = 1.0, debug=False):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    #print ("Image Center: %s" % str(image_center))
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, scale)
    print ("CV Rotation Matrix:")
    print ("%s" % str(rot_mat))
    rm = gen_rot_mat(image_center, angle, scale)
    print ("MY Rotation Matrix:")
    print ("%s" % str(rm))

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

    parser.add_argument("-l", "--linear",
                        action="store_true",
                        help="Linear Interpolate",
                        default=False)

    parser.add_argument("-v", "--video",
                        action="store_true",
                        help="Display Video")

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    parser.add_argument("-x", "--noshow",
                        action="store_true",
                        help="Do not show image",
                        default=False)

    args = parser.parse_args()
    print ("Running Script: %s" % NAME)

    rotation = float(args.rotation[0])
    scale = float(args.scale[0])
    linear_interpolate = args.linear
    print ("Rotation: %f, Scale: %f" % (rotation, scale))


    if args.debug:
        print ("test: %s" % str(args.test[0]))

    src = cv2.imread(IMAGE_PATH)
    window_name = "Image"
    #image = cv2.rotate(src, cv2.ROTATE_90_CLOCKWISE)
    #image = cv_rotate_image(src, rotation, scale, debug = args.debug)
    height, width, channels = src.shape
    sub_image_height = height // 2
    sub_image_width = width // 2
    sub_image_start_x = sub_image_width // 2
    sub_image_start_y = sub_image_height // 2
    src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    print ("")
    print ("")
    image_center = tuple(np.array(src.shape[1::-1]) / 2)
    rm = cv2.getRotationMatrix2D(image_center, rotation, scale)
    print ("CV Rotation Matrix:")
    print ("%s" % str(rm))
    rm = gen_rot_mat(image_center, rotation, scale)
    print ("MY Rotation Matrix:")
    print ("%s" % str(rm))
    print ("")
    print ("")

    if args.video:
        for rot in range (0, 180):
            src_image, dst_image = rotate_sub_image(src,
                                     sub_image_start_x,
                                     sub_image_start_y,
                                     sub_image_width,
                                     sub_image_height,
                                     rot,
                                     scale,
                                     linear_interpolate,
                                     debug = args.debug)
            #image = add_grid_to_image(image, 20, 20)

            image = np.zeros((sub_image_height, sub_image_width * 2, 1), dtype = "uint8")
            image[:sub_image_height, :sub_image_width] = src_image
            image[:sub_image_height, sub_image_width:(sub_image_width * 2)] = dst_image
            cv2.imshow(window_name, image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        src_image, dst_image = rotate_sub_image(src,
                                 sub_image_start_x,
                                 sub_image_start_y,
                                 sub_image_width,
                                 sub_image_height,
                                 rotation,
                                 scale,
                                 linear_interpolate,
                                 debug = args.debug)
        image = np.zeros((sub_image_height, sub_image_width * 2, 1), dtype = "uint8")
        image[:sub_image_height, :sub_image_width] = src_image
        image[:sub_image_height, sub_image_width:(sub_image_width * 2)] = dst_image
        if not args.noshow:
            cv2.imshow(window_name, image)
            cv2.waitKey(0)


if __name__ == "__main__":
    main(sys.argv)


