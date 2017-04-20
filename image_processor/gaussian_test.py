#! /usr/bin/env python

import cv2
import numpy as np
import matplotlib.pyplot as plt
from image_processor import *

print (TCOLORS.PURPLE + "Unit Test: Generate a standard guassian Array and digital representation of a guassian array" + TCOLORS.NORMAL)

#Constants
gaussian_sigma=1.2
gaussian_bitrange=18 #This is the number of bits that will be used to multiply values in the FPGA
gaussian_width = 5

print (TCOLORS.RED + "Gaussian Array" + TCOLORS.NORMAL)
print ("\tSigma: %f" % gaussian_sigma)
print ("\tBitrange: %d (Max Value) %d" % (gaussian_bitrange, ((2 ** gaussian_bitrange) - 1)))
print ("\tArray Length: %d" % gaussian_width)

gaussian_array = gen_deviation_array(sigma = gaussian_sigma, length = gaussian_width)
digital_array = convert_gaussian_to_digital_array(gaussian_array, gaussian_bitrange)


fig = plt.figure()
a=fig.add_subplot(1,2,1)
plt.bar(range( 0, len(gaussian_array)), gaussian_array)
plt.title("Normalized Gaussian Envelope")
plt.ylabel("Weight")
plt.xlabel("Envelope Position")
plt.xticks(range( 0, len(gaussian_array)), range(0 * int(gaussian_width / 2), len(gaussian_array)))

a=fig.add_subplot(1,2,2)
plt.bar(range( 0, len(digital_array)), digital_array)
plt.title("Mapped to %d bits" % gaussian_bitrange)
plt.ylabel("Weight")
plt.xlabel("Envelope Position")
plt.xticks(range( 0, len(digital_array)), range(-1 * int(gaussian_width / 2), len(digital_array)))
plt.ylim([0, (2 ** gaussian_bitrange) - 1])

plt.show()
