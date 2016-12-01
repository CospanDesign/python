#! /usr/bin/env python

import cv2
import numpy as np
import matplotlib.pyplot as plt
import time

from image_processor import *

print (TCOLORS.PURPLE + "Custom Corner Detector" + TCOLORS.NORMAL)

COLOR_OUT = True

#FILENAME = 'chessboard_skew.jpg'
#FILENAME = 'checkerboard2.png'
FILENAME = "lena1.png"

#Generate the Gaussian Envelope
#Constants
#SIGMA=1.6

BLOCK_SIZE = 3
#BLOCK_SIZE = 5
#BLOCK_SIZE = 7


K_VALUE = 0.04
#K_VALUE = 0.15

THRESHOLD = 2500000


SIGMA = float(BLOCK_SIZE) / 3.0
#SIGMA = float(BLOCK_SIZE) / 6.0

img = cv2.imread(FILENAME)
gray = rgb2gray(img)

cstm_out = cv2.imread(FILENAME)
ocv_out = cv2.imread(FILENAME)
diff_out = cv2.imread(FILENAME)


if not COLOR_OUT:
    cstm_out = rgb2gray(cstm_out)
    ocv_out = rgb2gray(cstm_out)

print "Image Width: %d Image Height: %d" % (len(gray[0]), len(gray))
print "Sigma: %f" % SIGMA
print "Envelope Size: %d" % BLOCK_SIZE

print "Generating Gaussian Array...",
start_time = time.time()
#gaussian_array = gen_deviation_array(sigma = SIGMA, length = BLOCK_SIZE)
gaussian_array = gen_2d_deviation_array(sigma = SIGMA, length = BLOCK_SIZE)
elapsed_time = time.time() - start_time
print "Done: Elapsed Time: %.3f" % elapsed_time
print "Gausian Distribution:\n%s" % str(gaussian_array)

print "Creating the X and Y image derivatives...",
start_time = time.time()
#image_x, image_y = gen_image_derivatives(gray)
image_x, image_y = gen_image_sobel(gray)
elapsed_time = time.time() - start_time
print "Done: Elapsed Time: %.3f" % elapsed_time

print "Generate <Ix^2*W(u,v)>,  <IxIy*W(u,v)>, <Iy^2*W(u,v)>...",
start_time = time.time()
a, bc, d = generate_matrix_values(image_x, image_y, gaussian_array)
elapsed_time = time.time() - start_time
print "Done: Elapsed Time: %.3f" % elapsed_time

print "Find the R Values:...",
start_time = time.time()
corners, det, trc = generate_mc_debug(a, bc, d, K_VALUE, THRESHOLD)

elapsed_time = time.time() - start_time
print "Done: Elapsed Time: %.3f" % elapsed_time

print "Display original image, gray image, DX Image, DY Image and Gaussian Array"

print "Apply to gray image"
height = len(gray)
width = len(gray[0])

A = np.ndarray(shape=(len(a), len(a[0])))
BC = np.ndarray(shape=(len(a), len(a[0])))
D = np.ndarray(shape=(len(a), len(a[0])))

for y in range(height):
    for x in range(width):
        A[y,x] = int(a[y,x])
        BC[y,x] = int(bc[y,x])
        D[y,x] = int(d[y,x])


ocv_gray = np.float32(gray)
ocv = cv2.cornerHarris(ocv_gray,
                       BLOCK_SIZE,
                       3,
                       K_VALUE)


if COLOR_OUT:

    corners = cv2.dilate(corners,None)
    ocv = cv2.dilate(ocv,None)
    cstm_out[corners == 255]=[0, 255, 0]
    ocv_out[ocv > (0.01 * ocv.max())]=[0, 255, 0]

    m = ocv.max()
    for y in range(len(diff_out)):
        for x in range(len(diff_out[0])):
            if (ocv[y][x] > (0.01 * m)) and (corners[y][x] == 255):
                diff_out[y][x] = [255, 255, 0]
            elif ocv[y][x] > (0.01 * ocv.max()):
                diff_out[y][x] = [255, 0, 0]
            elif corners[y][x] == 255:
                diff_out[y][x] = [0, 255, 0]


    
else:
    cstm_out[corners == 255]=[255]
    ocv_out[ocv > (0.01 * ocv.max())]=[255]


fig = plt.figure()
a=fig.add_subplot(5,3,1)
plt.title("Original")
plt.imshow(gray, cmap='Greys_r')
plt.axis('off')

a=fig.add_subplot(5,3,2)
plt.title("Gaussian")
plt.imshow(gaussian_array, cmap='Greys_r')
plt.axis('off')

a=fig.add_subplot(5,3,4)
plt.title("X Derivative")
plt.imshow(image_x, cmap='Greys_r')
plt.axis('off')

a=fig.add_subplot(5,3,5)
plt.title("Y Derivative")
plt.imshow(image_y, cmap='Greys_r')
plt.axis('off')

f=fig.add_subplot(5,3,7)
plt.title("A = <Ix^2 * w(u, v)>")
plt.imshow(A, cmap="Greys_r")
plt.axis('off')

f=fig.add_subplot(5,3,8)
plt.title("B and C = <IxIy * w(u, v)>")
plt.imshow(BC, cmap="Greys_r")
plt.axis('off')

f=fig.add_subplot(5,3,9)
plt.title("D = <Iy^2 * w(u,v)")
plt.imshow(D, cmap="Greys_r")
plt.axis('off')

f=fig.add_subplot(5,3,10)
plt.title("Determinate(M)")
plt.imshow(det, cmap="Greys_r")
plt.axis('off')

f=fig.add_subplot(5,3,11)
plt.title("k * trace(M) ^ 2")
plt.imshow(trc, cmap="Greys_r")
plt.axis('off')

if COLOR_OUT:
    f=fig.add_subplot(5,3,13)
    plt.title("Custom HCD Result")
    plt.imshow(cstm_out)
    plt.axis('off')

    f=fig.add_subplot(5,3,14)
    plt.title("Openc CV HCD Result")
    plt.imshow(ocv_out)
    plt.axis('off')

    f=fig.add_subplot(5,3,15)
    plt.title("Diff Values")
    plt.imshow(diff_out)
    plt.axis('off')



else:
    f=fig.add_subplot(5,3,13)
    plt.title("Custom HCD Result")
    #plt.imshow(corners, cmap="Greys_r")
    plt.imshow(cstm_out, cmap="Greys_r")
    plt.axis('off')

    f=fig.add_subplot(5,3,14)
    plt.title("Openc CV HCD Result")
    plt.imshow(ocv_out, cmap="Greys_r")
    plt.axis('off')

plt.show()

