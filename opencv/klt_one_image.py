#! /usr/bin/env python

"""
Created on Sun Jul  9 16:36:26 2017

@author: amado
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt

def interp(img, x):
    xb = np.ceil(x)
    a = (xb[0] - x[0])*(xb[1] - x[1])
    b = (x[0]+1-xb[0])*(xb[1] - x[1])
    c = (xb[0] - x[0])*(x[1]+1-xb[1])
    d = (x[0]+1-xb[0])*(x[1]+1-xb[1])
    return(a*img[int(xb[1]-1),int(xb[0]-1)]+
           b*img[int(xb[1]-1),int(xb[0])]+
           c*img[int(xb[1]),  int(xb[0]-1)]+
           d*img[int(xb[1]),  int(xb[0])])

def err(img, u, w, warp, template):
    er = 0
    for x in range(-w,w):
        for y in range(-w,w):
            #print(u+np.dot(warp,np.array([x,y,1])))
            #print(u+np.array([x,y]))
            er += (interp(img,u+np.dot(warp,np.array([x,y,1])))-template[u[1]+y,u[0]+x])**2
    return(er)


if __name__ == "__main__":
    print "Hello"
    '''
    mode = 'rotate'
    #mode = 'translate'
    center = np.array((260,137))
    offset = 10         # half the patch size
    rotation = 160      # degrees
    translation = 10    # pixels
    #plt.axis([0, 360, 0, 1e5])


    cv2.namedWindow('original',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('original',822,513)
    cv2.namedWindow('warped',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('warped',822,513)

    original = cv2.imread('messi5.jpg',0)
    print('Image size: {}'.format(original.shape))
    rows, cols = original.shape
    tl = center - offset
    br = center + offset

    cv2.imshow('original',original[tl[1]:br[1],tl[0]:br[0]])

    if mode == 'rotate':
        M = cv2.getRotationMatrix2D(tuple(center),rotation,1)
        warped = cv2.warpAffine(original,M,(cols,rows))
        cv2.imshow('warped',warped[tl[1]:br[1],tl[0]:br[0]])
        cv2.waitKey(50)
        for theta in np.arange(0, 360, 1):
            M_guess = cv2.getRotationMatrix2D((0,0),theta,1)
            e = err(warped,center,offset,M_guess,original)
            plt.scatter(theta,e,color='blue')

    elif mode == 'translate':
        M = np.float32([[1,0,translation],[0,1,0]])
        warped = cv2.warpAffine(original,M,(cols,rows))
        cv2.imshow('warped',warped[tl[1]:br[1],tl[0]:br[0]])
        cv2.waitKey(50)
        for trans in np.arange(0, 2*offset, 1):
            M_guess = np.float32([[1,0,trans],[0,1,0]])
            e = err(warped,center,offset,M_guess,original)
            plt.scatter(trans,e,color='blue')

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    '''
