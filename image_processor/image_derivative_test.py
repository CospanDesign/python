#! /usr/bin/env python

import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from image_processor import *

print (TCOLORS.PURPLE + "Unit Test: Finding the derivatives of an image" + TCOLORS.NORMAL)


img = cv2.imread(FILENAME)
image = rgb2gray(img)

print "Generating X and Y derivative of image...",
start_time = time.time()
image_x, image_y = gen_image_derivatives(image)
elapsed_time = time.time() - start_time
print "Done: Elapsed Time: %.3f" % elapsed_time

fig = plt.figure()
a=fig.add_subplot(1,3,1)
plt.title("Original")
plt.imshow(image, cmap='Greys_r')

a=fig.add_subplot(1,3,2)
plt.title("X Derivative")
plt.imshow(image_x, cmap='Greys_r')

a=fig.add_subplot(1,3,3)
plt.title("Y Derivative")
plt.imshow(image_y, cmap='Greys_r')
plt.show()
