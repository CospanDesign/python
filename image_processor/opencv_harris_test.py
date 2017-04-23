#! /usr/bin/env python

import cv2
import numpy as np
import matplotlib.pyplot as plt
from image_processor import *


print (TCOLORS.PURPLE + "OpenCV Harris Corner Detector" + TCOLORS.NORMAL)

try:
    filename = FILENAME
except NameError:

    #filename = 'chessboard.png'
    #filename = 'chessboard.jpg'
    filename = 'chessboard_skew.jpg'
    #filename ='image.jpg'
    print ("Global filename not defined\nUsing local image filename: %s" % filename)

filename ='lena1.png'

block_size = 3
k_size = 3
k_value = 0.04

img = cv2.imread(filename)
gray = rgb2gray(img)

gray = np.float32(gray)
dst = cv2.cornerHarris(gray,
                       block_size,
                       k_size,
                       k_value)

#result is dilated for marking the corners, not important
print ("Performed Harris Corner Detect")
dst = cv2.dilate(dst,None)

img[dst>0.01*dst.max()]=[255,255,255]

#plt.imshow(dst, cmap='Greys_r')
#cv2.startWindowThread()
plt.imshow(img)
#if cv2.waitKey(0) & 0xff == 27:
#    cv2.destroyAllWindows()
plt.show()
