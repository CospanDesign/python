#! /usr/bin/env python

import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from image_processor import *


print (TCOLORS.PURPLE + "Unit Test: Applying a Gaussian Blure on an image" + TCOLORS.NORMAL)

SIGMA = 1
ENVELOPE_SIZE = 5

img = cv2.imread(FILENAME)
gray = rgb2gray(img)

width = len(gray)
height = len(gray[0])


print "Image Width: %d Image Height: %d" % (len(gray), len(gray[0]))
print "Sigma: %d" % SIGMA
print "Envelope Size: %d" % ENVELOPE_SIZE

print "Generating Gaussian Envelope...",
start_time = time.time()
gaussian_envelope = gen_deviation_array(SIGMA, ENVELOPE_SIZE)
elapsed_time = time.time() - start_time
print "Done: Elapsed Time: %.3f" % elapsed_time
print "Gaussian Envelope: %s" % str(gaussian_envelope)

print "Using Open CV to apply gaussian blur...",
start_time = time.time()
blur = cv2.GaussianBlur(gray,(SIGMA,SIGMA),0)
elapsed_time = time.time() - start_time
print "Done: Elapsed Time: %.3f" % elapsed_time

print "Using custom algorithm to apply gaussian blur...",
start_time = time.time()
gaussian_blure = two_d_gaussian_blure(gray, gaussian_envelope)
elapsed_time = time.time() - start_time
print "Done: Elapsed Time: %.3f" % elapsed_time



fig = plt.figure()
a=fig.add_subplot(1,3,1)
plt.title("Original")
plt.imshow(gray, cmap='Greys_r')

a=fig.add_subplot(1,3,2)
plt.title("Opencv Gaussian Blur")
plt.imshow(blur, cmap='Greys_r')

a=fig.add_subplot(1,3,3)
plt.title("Gaussian Blur")
plt.imshow(gaussian_blure, cmap='Greys_r')
plt.show()

