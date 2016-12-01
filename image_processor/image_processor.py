#! /usr/bin/env python

#All Functions
import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

#Select the Image Filename

#FILENAME = 'chessboard.png'
#FILENAME = 'chessboard.jpg'
#FILENAME = 'chessboard_skew.jpg'
#FILENAME = 'checkerboard2.png'
#FILENAME ='image.jpg'
#FILENAME = "lena1.png"

class TCOLORS:
    GRAY      = '\x1b[30m'
    RED       = '\x1b[31m'
    GREEN     = '\x1b[32m'
    YELLOW    = '\x1b[33m'
    BLUE      = '\x1b[34m'
    PURPLE    = '\x1b[35m'
    CYAN      = '\x1b[36m'
    NORMAL    = '\x1b[0m'
    BOLD      = '\x1b[1m'
    UNDERLINE = '\x1b[4m'

def rgb2gray(rgb):
    '''
    Read in an RGB image and return a Grayscale image in ndarray format
    '''
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.144])

def gen_image_derivatives(gray_image):
    '''
    Pass in a grayscale image in ndarray format

    Returns tuple of image derivatives
    (image dx, image dy)
    '''
    height = len(gray_image)
    width = len(gray_image[0])
    #print "Width: %d" % width
    #print "Height: %d" % height

    #Find the derivative of an image
    image_x = np.ndarray(shape=(height, width), dtype=np.int32)
    image_y = np.ndarray(shape=(height, width), dtype=np.int32)
    for y in range(0, height - 1):
        for x in range(0, width - 1):
            #Get rid of edge cases
            if (x < 1) or (y < 1) or (x > width - 1) or (y > height - 1):
                image_x[y, x] = 0

            #X Data
            #Ros Before
            image_x[y, x]  =  gray_image[y - 1, x + 1] - gray_image[y - 1, x - 1]
            #Current Ros
            image_x[y, x] +=  gray_image[y    , x + 1] - gray_image[y    , x - 1]
            #Row After
            image_x[y, x] +=  gray_image[y + 1, x + 1] - gray_image[y + 1, x - 1]
            image_x[y, x] = int(abs(image_x[y, x]) / 3)

            #Y Data
            #Column Above
            image_y[y, x]  =  gray_image[y + 1, x - 1] - gray_image[y - 1, x - 1]
            #Current Column
            image_y[y, x] +=  gray_image[y + 1, x    ] - gray_image[y - 1, x    ]
            #Column Below
            image_y[y, x] +=  gray_image[y + 1, x + 1] - gray_image[y - 1, x + 1]
            image_y[y,x] = int (abs(image_y[y, x]) / 3)


    return (image_x, image_y)

def gen_image_sobel(gray_image):
    '''
    Pass in a grayscale image in ndarray format

    Returns tuple of image derivatives
    (image dx, image dy)
    '''
    height = len(gray_image)
    width = len(gray_image[0])
    #print "Width: %d" % width
    #print "Height: %d" % height

    #Find the derivative of an image
    image_x = np.ndarray(shape=(height, width), dtype=np.int32)
    image_y = np.ndarray(shape=(height, width), dtype=np.int32)
    for y in range(0, height - 1):
        for x in range(0, width - 1):
            #Get rid of edge cases
            if (x < 1) or (y < 1) or (x > width - 1) or (y > height - 1):
                image_x[y, x] = 0

            #X Data
            #Ros Before
            image_x[y, x]  =  gray_image[y - 1, x + 1] - gray_image[y - 1, x - 1]
            #Current Ros
            image_x[y, x] +=  (gray_image[y    , x + 1] * 2) - (gray_image[y    , x - 1] * 2)
            #Row After
            image_x[y, x] +=  gray_image[y + 1, x + 1] - gray_image[y + 1, x - 1]
            image_x[y, x] = int(abs(image_x[y, x]) / 4)

            #Y Data
            #Column Above
            image_y[y, x]  =  gray_image[y + 1, x - 1] - gray_image[y - 1, x - 1]
            #Current Column
            image_y[y, x] +=  (gray_image[y + 1, x    ] * 2) - (gray_image[y - 1, x    ] * 2)
            #Column Below
            image_y[y, x] +=  gray_image[y + 1, x + 1] - gray_image[y - 1, x + 1]
            image_y[y,x] = int (abs(image_y[y, x]) / 4)


    return (image_x, image_y)




GAUSSIAN_BITRANGE=18
GAUSSIAN_DIST=1 #Mapping from gaussian location to array position (1 = 1:1)


def gen_deviation_array(sigma, length=5):
    midpoint = int(length / 2)
    sd = []
    for i in range(length):
        d = abs((i - midpoint))
        sd.append((1 / (math.sqrt(2 * math.pi) * sigma)) * math.exp(-(d**2)/(2 * sigma**2)))

    #Normalize all the values
    #scale_value = 1 / sd[midpoint]
    #for i in range(length):
    #    sd[i] = sd[i] * scale_value
    return sd

def gen_2d_deviation_array(sigma, length=5):
    midpoint = int(length / 2)
    sd = np.ndarray(shape=(length, length), dtype=np.float)
    for y in range (length):
        for x in range(length):
            x_abs = abs((x - midpoint))
            y_abs = abs((y - midpoint))

            sd[y, x] = ((1 / (math.sqrt(2 * math.pi))) * math.exp(-(x_abs**2 + y_abs**2)/(2*sigma**2)))

    scale_value = 1 / sd[midpoint, midpoint]
    for y in range (length):
        for x in range(length):
            sd[y, x] = sd[y, x] * scale_value


    return sd



def convert_gaussian_to_digital_array(gaussian_array, bitrange = GAUSSIAN_BITRANGE, dist = GAUSSIAN_DIST):
    '''
    Generate an integer representation of a guassian array distribution,
    Takes in a floating point gaussian array as well as the bitrange to map to
    and the dist array element is (usually 1 for 1 to 1 pixel mapping)
    '''
    maxvalue = (2 ** bitrange) - 1
    midpoint = int(len(gaussian_array) / 2)
    digital_array = [0] * len(gaussian_array)
    for i in range(len(gaussian_array)):
        digital_array[i] = int(maxvalue * gaussian_array[i])

        if digital_array[i] < 0:
            digital_array[i] = 0

    return digital_array

def generate_matrix_values(ix, iy, ga):
    '''
    ix = derivative of image WRT X
    iy = derivative of image WRT Y
    ga = Gaussian Array

    Generate the following arrays

    Sum_(u,v)<Ix^2 * W(u,v)>
    Sum_(u,v)<IxIy * W(u,v)>
    Sum_(u,v)<Iy^2 * W(u,v)>
    '''
    width = len(ix[0])
    height = len(ix)

    win_height = ga.shape[0]
    win_width = ga.shape[1]
    win_x_midpoint = int(win_width / 2)
    win_y_midpoint = int(win_height / 2)

    #print ("window width: %d" % win_width)
    #print ("window height: %d" % win_height)
    #print ("window midpoint x: %d" % win_x_midpoint)
    #print ("window midpoint y: %d" % win_y_midpoint)

    a_out = np.ndarray(shape=(height, width), dtype=np.int32)
    bc_out = np.ndarray(shape=(height, width), dtype=np.int32)
    d_out = np.ndarray(shape=(height, width), dtype=np.int32)

    for y in range(0, height):
        for x in range(0, width):
            #Get rid of edge cases
            a_out[y, x] = 0
            bc_out[y, x] = 0
            d_out[y, x] = 0

            if (x < win_x_midpoint) or (y < win_y_midpoint) or (x > width - win_x_midpoint - 1) or (y > height - win_y_midpoint - 1):
                continue

            for wy in range (win_height):
                for wx in range(win_width):
                    #X Values
                    #pos = win_midpoint - i
                    xpos = wx - win_x_midpoint
                    ypos = wy - win_y_midpoint
                    
                    a_out[y, x]  += float(ix[y + ypos, x + xpos] * ix[y + ypos, x + xpos] * ga[wx, wy])
                    bc_out[y, x] += float(ix[y + ypos, x + xpos] * iy[y + ypos, x + xpos] * ga[wx, wy])
                    d_out[y, x]  += float(iy[y + ypos, x + xpos] * iy[y + ypos, x + xpos] * ga[wx, wy])
                   
    return (a_out, bc_out, d_out)

def generate_mc_debug(a, bc, d, k, threshold):
    '''
    Return an array of corners that are found using the 'k' value

    Arguments:
        a: Sum_(u,v) Ix(u,v)^2 * W(u,v)
        bc: Sum_(u,v) Ix(u,v)Iy(u,v) * W(u,v)
        d: Sum_(u,v) Iy(u,v)^2 * W(u,v)
        k: Scaling value of corners to detect
        threshold: value at which a 'good' corner is detected

    Return a new image with only the corners highlighted and the intermediately
    generated images
    '''
    width = len(a[0])
    height = len(a)
    rarray = np.ndarray(shape=(height, width))
    corners = np.ndarray(shape=(height, width))
    det = np.ndarray(shape=(height, width))
    trc = np.ndarray(shape=(height, width))
    max_r = 0
    for y in range(0, height):
        for x in range(0, width):
            r = float( ((a[y, x] * d[y,x]) - (bc[y,x] * bc[y,x])) - k * ((a[y,x] + d[y,x]) ** 2))
            det[y, x] = ((a[y, x] * d[y,x]) - (bc[y,x] * bc[y,x]))
            trc[y, x] = k * ((a[y,x] + d[y,x]) ** 2)
            if r > max_r:
                max_r = r
            if r < 0:
                corners[y, x] = 0
            elif r > threshold:
                corners[y, x] = 255
            else:
                corners[y, x] = 0

    print "Max R: %d" % max_r
    return (corners, det, trc)



def generate_mc(a, bc, d, k, threshold):
    '''
    Return an array of corners that are found using the 'k' value

    Arguments:
        a: Sum_(u,v) Ix(u,v)^2 * W(u,v)
        bc: Sum_(u,v) Ix(u,v)Iy(u,v) * W(u,v)
        d: Sum_(u,v) Iy(u,v)^2 * W(u,v)
        k: Scaling value of corners to detect
        threshold: value at which a 'good' corner is detected

    Return a new image with only the corners highlighted
    '''
    width = len(a[0])
    height = len(a)
    rarray = np.ndarray(shape=(height, width))
    corners = np.ndarray(shape=(height, width))
    max_r = 0
    for y in range(0, height):
        for x in range(0, width):
            r = float( ((a[y, x] * d[y,x]) - (bc[y,x] * bc[y,x])) - k * ((a[y,x] + d[y,x]) ** 2))
            if r > max_r:
                max_r = r
            if r < 0:
                corners[y, x] = 0
            elif r > threshold:
                corners[y, x] = 255
            else:
                corners[y, x] = 0

    print "Max R: %d" % max_r
    return corners


