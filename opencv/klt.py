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
import copy
import logging
from matplotlib import pyplot as plt
from matplotlib.figure import SubplotParams
from math import *

DEFAULT_START_FEATURE           = 25
#DEFAULT_ERROR_THRESHOLD         = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
DEFAULT_ERROR_THRESHOLD         = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
#DEFAULT_ERROR_THRESHOLD         = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
PATCH_SIZE                      = 7
PYRAMID_DEPTH                   = 2
MATCH_THRESHOLD                 = 0.3
CIRCLE_SIZE                     = 10
#ENERGY_THRESHOLD                = 0.1
ENERGY_THRESHOLD                = 0.0
MAX_FEATURES                    = 10
FEATURE_THRESHOLD               = 1
PYRAMID_POS                     = PYRAMID_DEPTH - 1
AFFINE_SIZE                     = 6
#MAX_ITERATION                   = 10
MAX_ITERATION                   = 20
#MAX_ITERATION                   = 30
LIGHT_INSENSITIVE               = False

INITIAL_ROTATION_ANGLE          = 0
INITIAL_TRANSLATE               = [0, 0]
INITIAL_WARP                    = [[cos(radians(INITIAL_ROTATION_ANGLE)), -sin(radians(INITIAL_ROTATION_ANGLE)), INITIAL_TRANSLATE[0]],
                                   [sin(radians(INITIAL_ROTATION_ANGLE)),  cos(radians(INITIAL_ROTATION_ANGLE)), INITIAL_TRANSLATE[1]]]

KLT_TRACKED                      =  0
KLT_NOT_FOUND                    = -1
KLT_SMALL_DET                    = -2
KLT_MAX_ITERATIONS               = -3
KLT_OOB                          = -4
KLT_LARGE_RESIDUE                = -5



class KLTException(Exception):
    pass

class KLTSmallDet(KLTException):

    def __str__(self):
        return repr("Small Determinate")

class KLTMaxIterations(KLTException):

    def __str__(self):
        return repr("Maximum iterations reached")

class KLTOOB(KLTException):
    def __init__(self, value):
       self.value = value

    def __str__(self):
        return repr("Values are out of range: %s" % self.value)

STEP_NONE = 0
STEP_FRAME = 1
STEP_FEATURE = 2
STEP_PYRAMID = 3
STEP_ITERATION = 4

class KLTState(object):
    ready = False
    first = False
    iteration_count = 0
    patch_width = 0
    patch_height = 0
    pyramid_pos = 0
    feature_pos = (0, 0)
    feature_index = 0
    template_image = None
    current_image = None
    image_diff = None

    convergence = False

    gradx = None
    grady = None

    dx = 0
    dy = 0

    axx = 0
    axy = 0
    ayx = 0
    ayy = 0

    current_dx = 0
    current_dy = 0

    current_axx = 0
    current_axy = 0
    current_ayx = 0
    current_ayy = 0

    ul_x = 0
    ul_y = 0
    ll_x = 0
    ll_y = 0
    ur_x = 0
    ur_y = 0
    lr_x = 0
    lr_y = 0

    error_dxx = 0
    error_dyx = 0
    error_dxy = 0
    error_dyy = 0
    error_dx = 0
    error_dy = 0

    error_dxx_thresh = 0
    error_dyx_thresh = 0
    error_dxy_thresh = 0
    error_dyy_thresh = 0
    error_dx_thresh = 0
    error_dy_thresh = 0

    x_offset = 0
    y_offset = 0


class KLTImage(object):

    # params for ShiTomasi corner detection
    feature_params  = dict( maxCorners      = MAX_FEATURES,
                            qualityLevel    = 0.3,
                            minDistance     = 7,
                            blockSize       = 7 )

    subpix_params   = dict( zeroZone        = (-1,-1),
                            winSize         = (10,10),
                            criteria        = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS,20,0.03))

    def __init__(   self,
                    image,
                    find_features = False,
                    is_gray = False,
                    max_features = MAX_FEATURES,
                    pyramid_depth = PYRAMID_DEPTH,
                    patch_size = PATCH_SIZE):

        self.log = logging.getLogger("klt")
        self.pyramid_depth = pyramid_depth
        self.patch_size = patch_size
        self.max_features = max_features

        #self.log.debug("Image Pyramid Depth: %d" % self.pyramid_depth)

        self.image_pyramid = []
        self.gradx_pyramid = []
        self.grady_pyramid = []
        self.feature_pyramid = []

        gimage = None

        #Save the image
        if is_gray:
            gimage = image
        else:
            gimage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #Create the pyramid
        for i in range(self.pyramid_depth):
            if i == 0:
                self.image_pyramid.append(gimage)
            else:
                self.image_pyramid.append(cv2.pyrDown(self.image_pyramid[i - 1]))

            gx, gy = self._find_image_gradiants(self.image_pyramid[i])
            self.gradx_pyramid.append(gx)
            self.grady_pyramid.append(gy)

        if find_features:
            #Create the pyramid feature list
            self._find_features()

    def _find_features(self):
        tfeatures = cv2.goodFeaturesToTrack(self.image_pyramid[0], **self.feature_params)

        cv2.cornerSubPix(self.image_pyramid[0], tfeatures, **self.subpix_params)
        self.log.info("Found %d features" % len(tfeatures))

        features = []
        for f in tfeatures:
            features.append([f[0][0], f[0][1], KLT_TRACKED])

        #We found the features on the original image, now we need to scale the features for each of the levels
        print "Features: %s" % str(features)
        for i in range(self.pyramid_depth):
            if i == 0:
                self.feature_pyramid.append(features)
            else:
                #r = (self.pyramid_depth - 1) - i
                r = i
                scale = 2.0 ** r
                print ("Scale: %d" % scale)

                pfeatures = [0] * len(features)
                for j in range(len(features)):
                    point = features[j]
                    x = float((1.0 * point[0]) / scale)
                    y = float((1.0 * point[1]) / scale)
                    pfeatures[j] = [x, y, KLT_TRACKED]

                self.feature_pyramid.append(pfeatures)

    def _find_image_gradiants(self, image):
        #Should be a 2D floating point image
        gradx = np.zeros(shape=(image.shape[0], image.shape[1]), dtype = np.float32)
        grady = np.zeros(shape=(image.shape[0], image.shape[1]), dtype = np.float32)
        for y in range(1, image.shape[0] - 1):
            for x in range(1, image.shape[1] - 1):

                gradx[y][x] = (float(image[y - 1][x + 1]) - float(image[y - 1][x - 1]) + \
                               float(image[y    ][x + 1]) - float(image[y    ][x - 1]) + \
                               float(image[y + 1][x + 1]) - float(image[y + 1][x - 1])) / 3.0

                grady[y][x] = (float(image[y + 1][x - 1]) - float(image[y - 1][x - 1]) + \
                               float(image[y + 1][x    ]) - float(image[y - 1][x    ]) + \
                               float(image[y + 1][x + 1]) - float(image[y - 1][x + 1])) / 3.0
        return gradx, grady

    def update_feature(self, index, feature_x, feature_y, status):
        self.log.debug("Update feature (%d) : %f, %f: %d" % (index, feature_x, feature_y, status))
        for i in range (self.pyramid_depth):
            r = i
            scale = 2.0 ** r
            x = None
            y = None
            if feature_x is not None and feature_y is not None:
                x = float((1.0 * feature_x) / scale)
                y = float((1.0 * feature_y) / scale)

            self.feature_pyramid[0][index] = [x, y, status]

    def get_feature(self, depth, index):
        self.log.debug("Get feature at pyramid level: %d, and index: %d" % (depth, index))
        #print "feature: %s" % str(self.feature_pyramid[depth])
        #print "Feature: %s" % str(self.feature_pyramid[depth][index])
        return self.feature_pyramid[depth][index]

    def lost_feature(self, index):
        for i in range (self.pyramid_depth):
            self.feature_pyramid[i][index] = None

    def get_feature_length(self):
        return len(self.feature_pyramid[0])

    def get_image(self, depth):
        return self.image_pyramid[depth]

    def update_image(self, current_image):
        #self.feature_pyramid = current_image.feature_pyramid
        self.log.debug("***************Update Template Image with Current Image")
        self.image_pyramid = copy.copy(current_image.image_pyramid)
        self.gradx_pyramid = copy.copy(current_image.gradx_pyramid)
        self.grady_pyramid = copy.copy(current_image.grady_pyramid)

    def get_gradiants(self, depth):
        return self.gradx_pyramid[depth], self.grady_pyramid[depth]


class KLT(object):

    # Parameters for lucas kanade optical flow
    lk_params       = dict( winSize         = (15,15),
                            maxLevel        = 2,
                            criteria        = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    def __init__(   self,
                    max_features = MAX_FEATURES,
                    pyramid_depth = PYRAMID_DEPTH,
                    min_translate_displacement = 0.1,
                    max_affine_residue = 10.0,
                    min_affine_displacement = 0.02,
                    max_affine_displacement_difference = 1.5,
                    patch_size = PATCH_SIZE,
                    light_insensitive = LIGHT_INSENSITIVE,
                    debug = False):
        self.feature_threshold = FEATURE_THRESHOLD
        self.max_features = max_features
        self.pyramid_depth = pyramid_depth
        self.min_translate_displacement = min_translate_displacement
        self.max_affine_residue = max_affine_residue
        self.min_affine_displacement = min_affine_displacement
        self.max_affine_displacement_difference = max_affine_displacement_difference
        self.light_insensitive = light_insensitive
        if (patch_size % 2) == 0:
            raise KLTException("Patch size must be odd")
        if patch_size < 3:
            raise KLTException("Patch size must be at least 3")
        self.patch_size = patch_size
        self.features = []
        self.klt_template_image = None
        self.update_cb = None

        self.debug = debug

        self.log = logging.getLogger("klt")
        if debug:
            self.log.setLevel(logging.DEBUG)

        self.klt_current_image = None
        self.klt_template_image = None
        self.step_type = STEP_NONE
        self.klt_state = KLTState()
        self.ready = False

    def set_update_callback(self, cb):
        self.update_cb = cb
        self.ready = True

    def is_stepping_enabled(self):
        return self.step_type != STEP_NONE

    def set_step_none(self):
        self.step_type = STEP_NONE

    def set_step_feature(self):
        self.step_type = STEP_FEATURE

    def set_step_pyramid(self):
        self.step_type = STEP_PYRAMID

    def set_step_iteration(self):
        self.step_type = STEP_ITERATION

    def get_image_transform(self, t_image, x, y, axx, ayx, axy, ayy):
        hw = self.patch_size / 2
        hh = self.patch_size / 2
        patch = np.zeros(shape = (self.patch_size, self.patch_size), dtype=np.float32)
        for j in range(-hh, hh + 1):
            for i in range(-hw, hw + 1):
                mi = axx * i + axy * j
                mj = ayx * i + ayy * j
                patch[j][i] = self.interpolate(x + mi, y2 + mj, image)

        return patch

    def compute_intensity_difference(self, t_image, c_image, x1, y1, x2, y2, axx, ayx, axy, ayy):
        hw = self.patch_size / 2
        hh = self.patch_size / 2

        image_diff = np.zeros(shape=(self.patch_size, self.patch_size), dtype=np.float32)
        for j in range(-hh, hh + 1):
            for i in range(-hw, hw + 1):
                #Get the intesity of the first patch
                g1 = self.interpolate(x1 + i, y1 + j, t_image)

                #Transform the x and y to the space on the second image
                mi = axx * i + axy * j
                mj = ayx * i + ayy * j

                #Get the intesity from the second patch
                g2 = self.interpolate(x2 + mi, y2 + mj, c_image)
                image_diff[j + hh][i + hw] = g1 - g2
        return image_diff

    def compute_gradiant_sum(self, t_gradx, t_grady, c_gradx, c_grady, x, y, axx, ayx, axy, ayy):
        gradx = 0
        grady = 0
        hw = self.patch_size / 2
        hh = self.patch_size / 2
        for j in range (-hh, hh + 1):
            for i in range (-hw, hw + 1):
                mi = axx * i + axy + j
                mj = ayx * i + ayy + j
                gradx += self.interpolate(x + mi, y + mj)
                grady += self.interpolate(x + mi, y + mj)

        return gradx, grady

    def compute_gradiant_affine_window(self, in_gradx, in_grady, x, y, axx, ayx, axy, ayy):
        '''
        Aligns the gradiants with the affine transformed window
        '''
        hw = self.patch_size / 2
        hh = self.patch_size / 2


        out_gradx = np.zeros(shape = (self.patch_size, self.patch_size), dtype = np.float32)
        out_grady = np.zeros(shape = (self.patch_size, self.patch_size), dtype = np.float32)

        for j in range (-hh, hh + 1):
            for i in range (-hw, hw + 1):
                mi = axx * i + axy * j
                mj = ayx * i + ayy * j
                out_gradx[j + hh][i + hw] = self.interpolate(x + mi, y + mj, in_gradx)
                out_grady[j + hh][i + hw] = self.interpolate(x + mi, y + mj, in_grady)

        return (out_gradx, out_grady)

    def interpolate(self, x, y, image):
        xt = int(x)
        yt = int(y)
        ax = float(x) - float(xt)
        ay = float(y) - float(yt)

        if xt < 0:
            raise KLT_OOB("xt < 0 xt: %d" % xt)
        if yt < 0:
            raise KLT_OOB("yt < 0 yt: %d" % yt)

        if xt > image.shape[1] - 2:
            raise KLT_OOB("xt > width - 2 xt: %d width - 2" % (xt, (image.shape[1] - 2)))

        if yt > image.shape[0] - 2:
            raise KLT_OOB("yt > height - 2 xt: %d height - 2" % (yt, (image.shape[0] - 2)))

        pixel = 0

        pixel += (1 - ax) * (1 - ay) * image[yt    ][xt    ]
        pixel += (    ax) * (1 - ay) * image[yt    ][xt + 1]

        pixel += (1 - ax) * (    ay) * image[yt    ][xt    ]
        pixel += (    ax) * (    ay) * image[yt + 1][xt    ]
        return pixel

    def sum_abs_float_window(self, image_diff):
        s = 0.0
        height = self.patch_size
        width = self.patch_size

        for h in range((height - 1), (0 - 1), -1):
            for w in range (width):
                s += abs(image_diff[h][w])
        return s

    def compute_6x1_error_vector(self, image_diff, gradx, grady):
        hw = self.patch_size / 2
        hh = self.patch_size / 2

        error = np.zeros(shape=(6, 1), dtype=np.float32)

        for j in range(-hh, hh + 1):
            for i in range(-hw, hw + 1):
                diff_gradx = image_diff[j + hh][i + hw] * gradx[j + hh][i + hw]
                diff_grady = image_diff[j + hh][i + hw] * grady[j + hh][i + hw]
                error[0][0] += diff_gradx * i
                error[1][0] += diff_grady * i
                error[2][0] += diff_gradx * j
                error[3][0] += diff_grady * j
                error[4][0] += diff_gradx
                error[5][0] += diff_grady

        for i in range (6):
            error[i][0] *= 0.5

        print ("Error:\n%s" % str(error))

        return error

    def compute_6x6_gradiant_matrix(self, gradx, grady):
        hw = self.patch_size / 2
        hh = self.patch_size / 2

        mat = np.zeros(shape = (6, 6), dtype=np.float32)

        for j in range (-hh, hh + 1):
            for i in range (-hw, hw + 1):
                gx = gradx[j + hh][i + hh]
                gy = grady[j + hw][i + hw]
                gxx = gx * gx
                gxy = gx * gy
                gyy = gy * gy
                x = float (i)
                y = float (j)
                xx = x * x
                xy = x * y
                yy = y * y


                mat[0][0] += xx * gxx
                mat[0][1] += xx * gxy
                mat[0][2] += xy * gxx
                mat[0][3] += xy * gxy
                mat[0][4] += x  * gxx
                mat[0][5] += x  * gxy

                mat[1][1] += xx * gyy
                mat[1][2] += xy * gxy
                mat[1][3] += xy * gyy
                mat[1][4] += x  * gxy
                mat[1][5] += x  * gyy

                mat[2][2] += yy * gxx
                mat[2][3] += yy * gxy
                mat[2][4] += y  * gxx
                mat[2][5] += y  * gxy

                mat[3][3] += yy * gyy
                mat[3][4] += y  * gxy
                mat[3][5] += y  * gyy

                mat[4][4] += gxx
                mat[4][5] += gxy

                mat[5][5] += gyy

        #Take advantage of symetry
        for j in range (5):
            for i in range (j + 1, 6):
                mat[i][j] = mat[j][i]

        return mat

    def gauss_jordan_elimination(self, mat, row_size, error, col_size):
        c_index = [0] * row_size
        r_index = [0] * row_size
        i_piv = [0] * row_size

        row = 0
        col = 0

        lmat = mat.copy()
        lerror = error.copy()

        for i in range (row_size):
            big = 0.0
            #Go through each row
            for j in range(row_size):
                if i_piv[j] != 1:
                    for k in range (row_size):
                        #First time
                        if i_piv[k] == 0:
                            #The inverse value for this row is zero
                            if abs(lmat[j][k] >= big):
                                big = float(abs(lmat[j][k]))
                                row = j
                                col = k
                        elif i_piv[k] > 1:
                            #Inverse value is so high the entire determinant is too small
                            raise KLTSmallDet
            i_piv[col] += 1
            if row != col:
                #Because ther is a reflection around the diaganol we save some computation
                for l in range (row_size):
                    g = lmat[row][l]
                    lmat[row][l] = lmat[col][l]
                    lmat[col][l] = g
                for l in range(col_size):
                    g = lerror[row][l]
                    lerror[row][l] = lerror[col][l]
                    lerror[col][l] = g


            r_index[i] = row
            c_index[i] = col
            if lmat[col][col] == 0.0:
                #If a value along the diaganol is zero than the determinate will be very low if not zero
                raise KLTSmallDet

            #Get the inverse of the diagonal value
            pivinv = 1.0 / lmat[col][col]

            #Set that value to 1
            lmat[col][col] = 1.0
            for l in range(row_size):
                lmat[col][l] *= pivinv

            for l in range(col_size):
                lerror[col][l] *= pivinv

            for ll in range(row_size):
                if ll != col:
                    dum = lmat[ll][col]
                    lmat[ll][col] = 0.0
                    for l in range(row_size):
                        lmat[ll][l] -= lmat[col][l] * dum
                    for l in range(col_size):
                        lerror[ll][l] -= lerror[col][l] * dum

        for l in range(row_size - 1, 0 - 1, -1):
            if r_index[l] != c_index[l]:
                for p in range (row_size):
                    g = lmat[p][r_index[l]]
                    lmat[p][r_index[l]] = lmat[p][c_index[l]]

        return lmat, lerror

    def track(self, image):

        self.ready = False
        if self.klt_template_image is None:
            self.klt_template_image = KLTImage( image,
                                            pyramid_depth = self.pyramid_depth,
                                            find_features = True)
            self.ready = True
            return


        self.log.debug("New image to track")
        self.klt_current_image = KLTImage( image,
                                    pyramid_depth = self.pyramid_depth)

        '''
        We now have the following
            - image pyramid of the previous image
            - image pyramid of the current image
            - features for all levels of the previous image
            - features for all levels of the current image
        '''

        #At the highest level go through all the features and perform the current warp
        for j in range (self.klt_template_image.get_feature_length()):
            status = KLT_TRACKED
            x = None
            y = None
            for i in range(self.pyramid_depth - 1, -1, -1):
                self.log.debug("FEATURE: %d at PYRAMID LEVEL: %d" % (j, i))
                f = self.klt_template_image.get_feature(i, j)
                self.log.debug("FEATURE: %d at Pyramid Level: %d, Status: %d" % (j, i, f[2]))
                if f[2] != KLT_TRACKED:
                    f0 = self.klt_template_image.get_feature(i, 0)
                    self.log.info("FEATURE: %d is lost, last seen at: %f %f" % (j, i, f0[0], f0[1]))
                    #XXX: Pass this up for now, we'll get more features in the next version

                x, y, status = self.track_feature(i, j)
                if self.step_type == STEP_PYRAMID:
                    if self.update_cb is not None:
                        self.update_cb(self.klt_state)


                if status != KLT_TRACKED:
                    break

            '''
            if self.step_type == STEP_FEATURE:
                if self.update_cb is not None:
                    self.update_cb(self.klt_state)
            '''

            #XXX: Debug
            self.klt_template_image.update_feature(j, x, y, status)
            if status != KLT_TRACKED:
                self.log.debug("Feature %d lost" % j)

        self.klt_template_image.update_image(self.klt_current_image)
        self.ready = True

    def track_feature(  self,
                        depth,                  #Depth of pyramid
                        feature_index):         #Feature Index
        """
        Track an individual feature from one image to the next

        Arguments:
            depth: Depth within pyramid
            feature_index: Index of feature to track

        Returns:
            Tracked features if no errors

        Raises:
            KLTSmallDet Exception: Small determinate
            KLTMaxIteration: Maximum number of iterations exceeded
        """
        status = KLT_TRACKED
        convergence = False
        self.log.debug("Feature: %d" % feature_index)
        feature = self.klt_template_image.get_feature(depth, feature_index)
        t_image = self.klt_template_image.get_image(depth)
        t_gradx, t_grady = self.klt_template_image.get_gradiants(depth)
        c_image = self.klt_current_image.get_image(depth)
        c_gradx, c_grady = self.klt_current_image.get_gradiants(depth)

        self.log.debug("position of feature: %s" % str(feature))
        self.log.debug("size of template image: %s" % str(t_image.shape))

        warp = INITIAL_WARP
        self.log.debug("Initial Warp: %s" % str(warp))

        hw = self.patch_size / 2
        hh = self.patch_size / 2

        nc1 = t_image.shape[1]
        nc2 = c_image.shape[1]
        nr1 = t_image.shape[0]
        nr2 = c_image.shape[0]

        eps = 0.1

        x1 = feature[0]
        y1 = feature[1]

        x2 = x1 + warp[0][2]
        y2 = y1 + warp[1][2]

        old_x2 = x2
        old_y2 = y2

        image_diff = None
        gradx = None
        grady = None

        dx = warp[0][2]
        dy = warp[1][2]

        axx = warp[0][0]
        axy = warp[0][1]
        ayx = warp[1][0]
        ayy = warp[1][1]

        self.klt_state.dx = dx
        self.klt_state.dy = dy

        self.klt_state.axx = axx
        self.klt_state.axy = axy
        self.klt_state.ayx = ayx
        self.klt_state.ayy = ayy

        self.klt_state.x_offset = 0
        self.klt_state.y_offset = 0

        for k in range(MAX_ITERATION):
            self.log.debug("Iteration: %d" % k)

            self.klt_state.current_dx = self.klt_state.dx
            self.klt_state.current_dy = self.klt_state.dy

            self.klt_state.current_axx = self.klt_state.axx
            self.klt_state.current_axy = self.klt_state.axy
            self.klt_state.current_ayx = self.klt_state.ayx
            self.klt_state.current_ayy = self.klt_state.ayy

            ul_x =  (axx * (-hw)) + (axy *   hh ) + x2   # Upper Left Corner
            ul_y =  (ayx * (-hw)) + (ayy *   hh ) + y2
            ll_x =  (axx * (-hw)) + (axy * (-hh)) + x2   # Lower Left Corner
            ll_y =  (ayx * (-hw)) + (ayy * (-hh)) + y2
            ur_x =  (axx *   hw ) + (axy *   hh ) + x2   # Upper Right Corner
            ur_y =  (ayx *   hw ) + (ayy *   hh ) + y2
            lr_x =  (axx *   hw ) + (axy * (-hh)) + x2   # Lower Right Corner
            lr_y =  (ayx *   hw ) + (ayy * (-hh)) + y2
            self.log.debug("UL_X: %f, UL_Y: %f, LL_X: %f, LL_Y: %f, UR_X: %f, UR_Y: %f, LR_X: %f, LR_Y: %f" % (ul_x, ul_y, ll_x, ll_y, ur_x, ur_y, lr_x, lr_y))

            #If out of bounds, exit loop */
            if (x1 - hw) < 0.0 or (nc1 - (x1 + hw)) < eps:
                self.log.debug("(x1 - hw < 0.0) or ((nc1 - (x1 + hw)) < eps): x1=%f nc=%d, hw = %d" % (x1, nc1, hw))
                return  (None, None, KLT_OOB)

            if y1 - hh < 0.0 or  nr1 - (y1 + hh) < eps:
                self.log.debug("(y1 - hh < 0.0) or ((nr1 - (y1 + hh)) < eps): y1=%f nr1=%d, hh = %d" % (x1, nc1, hh))
                return  (None, None, KLT_OOB)

            if ul_x  < 0.0 or  nc2 - (ul_x ) < eps:
                self.log.debug("ul_x < 0.0 or nc2 - (ul_x) < eps: ul_x: %f nc2: %d" % (ul_x, nc2))
                return  (None, None, KLT_OOB)

            if ll_x  < 0.0 or  nc2 - (ll_x ) < eps:
                self.log.debug("ll_x < 0.0 or nc2 - (ll_x) < eps: ll_x: %f nc2: %d" % (ll_x, nc2))
                return  (None, None, KLT_OOB)

            if ur_x  < 0.0 or  nc2 - (ur_x ) < eps:
                self.log.debug("ur_x < 0.0 or nc2 - (ur_x) < eps: ur_x: %f nc2: %d" % (ur_x, nc2))
                return  (None, None, KLT_OOB)

            if lr_x  < 0.0 or  nc2 - (lr_x ) < eps:
                self.log.debug("lr_x < 0.0 or nc2 - (lr_x) < eps: lr_x: %f nc2: %d" % (lr_x, nc2))
                return  (None, None, KLT_OOB)

            if ul_y  < 0.0 or  nr2 - (ul_y ) < eps:
                self.log.debug("ul_y < 0.0 or nr2 - (ul_y) < eps: ul_y: %f nr2: %d" % (ul_y, nr2))
                return  (None, None, KLT_OOB)

            if ll_y  < 0.0 or  nr2 - (ll_y ) < eps:
                self.log.debug("ll_y < 0.0 or nr2 - (ll_y) < eps: ll_y: %f nr2: %d" % (ll_y, nr2))
                return  (None, None, KLT_OOB)

            if ur_y  < 0.0 or  nr2 - (ur_y ) < eps:
                self.log.debug("ur_y < 0.0 or nr2 - (ur_y) < eps: ur_y: %f nr2: %d" % (ur_y, nr2))
                return  (None, None, KLT_OOB)

            if lr_y  < 0.0 or  nr2 - (lr_y ) < eps:
                self.log.debug("lr_y < 0.0 or nr2 - (lr_y) < eps: lr_y: %f nr2: %d" % (lr_y, nr2))
                return  (None, None, KLT_OOB)



            #Using SSD reduce the error below a threshold

            #TODO: Light insesitive

            image_diff = self.compute_intensity_difference(t_image, c_image, x1, y1, x2, y2, axx, ayx, axy, ayy)
            #gradx, grady = self.compute_gradiant_affine_window(t_gradx, t_grady, x1, y1, axx, ayx, axy, ayy)
            gradx, grady = self.compute_gradiant_affine_window(c_gradx, c_grady, x2, y2, axx, ayx, axy, ayy)

            self.log.debug("Image Difference:\n%s\n" % str(image_diff))
            #self.log.debug("gradx:\n%s\n" % str(gradx))
            #self.log.debug("grady:\n%s\n" % str(grady))

            #Compute Error Vector
            #print ("image diff: %s" % str(image_diff))
            #print ("Gradx: %s" % str(gradx))
            #print ("Grady: %s" % str(grady))
            error = self.compute_6x1_error_vector(image_diff, gradx, grady)

            #Compute 6 x 6 gradiante matrix
            gradiant_matrix = self.compute_6x6_gradiant_matrix(gradx, grady)

            affine_mat = None
            compute_error = None
            #Find the status from the gauss jordan elimination
            try:
                affine_mat, compute_error = self.gauss_jordan_elimination(gradiant_matrix, 6, error, 1)
            except KLTSmallDet:
                return (None, None, KLT_SMALL_DET)

            print "Computed Difference: %s" % str(compute_error)

            self.klt_state.error_dxx = compute_error[0]
            self.klt_state.error_dyx = compute_error[1]
            self.klt_state.error_dxy = compute_error[2]
            self.klt_state.error_dyy = compute_error[3]
            self.klt_state.error_dx = compute_error[4]
            self.klt_state.error_dy = compute_error[5]

            self.klt_state.error_dxx_thresh = self.min_affine_displacement
            self.klt_state.error_dyx_thresh = self.min_affine_displacement
            self.klt_state.error_dxy_thresh = self.min_affine_displacement
            self.klt_state.error_dyy_thresh = self.min_affine_displacement
            self.klt_state.error_dx_thresh = self.min_translate_displacement
            self.klt_state.error_dy_thresh = self.min_translate_displacement


            if self.step_type != STEP_NONE:
                self.klt_state.feature_pos = feature
                self.klt_state.feature_index = feature_index
                self.klt_state.convergence = convergence
                self.klt_state.ready = True
                self.klt_state.iteration_count = k
                self.klt_state.patch_width = self.patch_size
                self.klt_state.patch_height = self.patch_size
                self.klt_state.pyramid_pos = depth
                self.klt_state.template_image = t_image
                self.klt_state.current_image = c_image

                self.klt_state.image_diff = image_diff

                self.klt_state.gradx = gradx
                self.klt_state.grady = grady

                self.klt_state.x_offset += self.klt_state.dx
                self.klt_state.y_offset += self.klt_state.dy

                self.klt_state.dx = dx
                self.klt_state.dx = dy

                self.klt_state.axx = axx
                self.klt_state.axy = axy
                self.klt_state.ayx = ayx
                self.klt_state.ayy = ayy

                self.klt_state.ul_x = ul_x
                self.klt_state.ul_y = ul_y
                self.klt_state.ll_x = ll_x
                self.klt_state.ll_y = ll_y
                self.klt_state.ur_x = ur_x
                self.klt_state.ur_y = ur_y
                self.klt_state.lr_x = lr_x
                self.klt_state.lr_y = lr_y

            #Update the axx, ayx, axy, ayy and dx, dy
            axx += compute_error[0]
            ayx += compute_error[1]
            axy += compute_error[2]
            ayy += compute_error[3]

            dx = compute_error[4]
            dy = compute_error[5]

            self.log.debug("Old Affine map: axx: %f, ayx: %f, axy: %f, ayy: %f" % (self.klt_state.current_axx, self.klt_state.current_ayx, self.klt_state.current_axy, self.klt_state.current_ayy))
            self.log.debug("New Affine map: axx: %f, ayx: %f, axy: %f, ayy: %f" % (axx, ayx, axy, ayy))

            x2 += dx
            y2 += dy

            self.log.debug("New Translation: dx: %f, dy: %f Added to X, Y, New X Y: (%f, %f)" % (dx, dy, x2, y2))

            # Move upper left corner to old minus the error detected
            ul_x -=  (axx * (-hw)) + (axy *   hh ) + x2   # Upper Left Corner
            ul_y -=  (ayx * (-hw)) + (ayy *   hh ) + y2
            ll_x -=  (axx * (-hw)) + (axy * (-hh)) + x2   # Lower Left Corner
            ll_y -=  (ayx * (-hw)) + (ayy * (-hh)) + y2
            ur_x -=  (axx *   hw ) + (axy *   hh ) + x2   # Upper Right Corner
            ur_y -=  (ayx *   hw ) + (ayy *   hh ) + y2
            lr_x -=  (axx *   hw ) + (axy * (-hh)) + x2   # Lower Right Corner
            lr_y -=  (ayx *   hw ) + (ayy * (-hh)) + y2
            self.log.debug("Deltas UL_X: %f, UL_Y: %f, LL_X: %f, LL_Y: %f, UR_X: %f, UR_Y: %f, LR_X: %f, LR_Y: %f" % (ul_x, ul_y, ll_x, ll_y, ur_x, ur_y, lr_x, lr_y))

            #Make adjustments to ul_x, ul_y, ll_x, ll_y, ur_x, ur_y, lr_x, lr_y
            #Determine convergance
            convergence = True
            if abs(dx) > self.min_translate_displacement:
                convergence = False
                self.log.debug("dx  > Translation Threshold!: %f > %f" % (abs(dx), self.min_translate_displacement))

            if abs(dy) > self.min_translate_displacement:
                convergence = False
                self.log.debug("dy  > Translation Threshold!: %f > %f" % (abs(dy), self.min_translate_displacement))

            if abs(ul_x) > self.min_affine_displacement:
                convergence = False
                self.log.debug("ul_x > Affine Threshold!: %f > %f" % (abs(ul_x), self.min_affine_displacement))

            if abs(ul_y) > self.min_affine_displacement:
                convergence = False
                self.log.debug("ul_y > Affine Threshold!: %f > %f" % (abs(ul_y), self.min_affine_displacement))

            if abs(ll_x) > self.min_affine_displacement:
                convergence = False
                self.log.debug("ll_x > Affine Threshold!: %f > %f" % (abs(ll_x), self.min_affine_displacement))

            if abs(ll_y) > self.min_affine_displacement:
                convergence = False
                self.log.debug("ll_y > Affine Threshold!: %f > %f" % (abs(ll_y), self.min_affine_displacement))

            if abs(ur_x) > self.min_affine_displacement:
                convergence = False
                self.log.debug("ur_x > Affine Threshold!: %f > %f" % (abs(ur_x), self.min_affine_displacement))

            if abs(ur_y) > self.min_affine_displacement:
                convergence = False
                self.log.debug("ur_y > Affine Threshold!: %f > %f" % (abs(ur_y), self.min_affine_displacement))

            if abs(lr_x) > self.min_affine_displacement:
                convergence = False
                self.log.debug("lr_x > Affine Threshold!: %f > %f" % (abs(lr_x), self.min_affine_displacement))

            if abs(lr_y) > self.min_affine_displacement:
                convergence = False
                self.log.debug("lr_y > Affine Threshold!: %f > %f" % (abs(lr_y), self.min_affine_displacement))


            if self.step_type == STEP_ITERATION:
                self.update_cb(self.klt_state)


            if convergence:
                self.log.debug("Convergence!")

                #Check if window is out of bounds
                if  (x2 - hw < 0.0) or (nc2 - (x2 + hw) < eps) or \
                    (y2 - hh < 0.0) or (nr2 - (y2 + hh) < eps):
                    #Lost this feature (Moved off screen)
                    self.log.debug("Feature: %d: Resulting feature transform that is now out of bounds", feature_index)
                    return (None, None, KLT_OOB)

                #Check if feature has moved too much during iteration
                if  (x2 - old_x2) > self.max_affine_displacement_difference or \
                    (y2 - old_y2) > self.max_affine_displacement_difference:
                    self.log.warning("Feature: %d has been displaced too far to be valid" % feature_index)
                    return (None, None, KLT_OOB)

                #Check whether residue if too large
                image_diff = self.compute_intensity_difference(t_image, c_image, x1, y1, x2, y2, axx, ayx, axy, ayy)
                if (self.sum_abs_float_window(image_diff) / (self.patch_size * self.patch_size)) > self.max_affine_residue:
                    self.log.warning("Feature: %d was tracked but the residue is too large" % feature_index)
                    return (None, None, KLT_LARGE_RESIDUE)

                '''
                if self.step_type != STEP_NONE:
                    self.klt_state.feature_pos = feature
                    self.klt_state.feature_index = feature_index
                    self.klt_state.ready = True
                    self.klt_state.iteration_count = k
                    self.klt_state.patch_width = self.patch_size
                    self.klt_state.patch_height = self.patch_size
                    self.klt_state.pyramid_pos = depth
                    self.klt_state.template_image = t_image
                    self.klt_state.current_image = c_image

                    self.klt_state.image_diff = image_diff

                    self.klt_state.gradx = gradx
                    self.klt_state.grady = grady

                    self.klt_state.dx = dx
                    self.klt_state.dx = dy

                    self.klt_state.axx = axx
                    self.klt_state.axy = axy
                    self.klt_state.ayx = ayx
                    self.klt_state.ayy = ayy

                    self.klt_state.x_offset += klt_state.dx
                    self.klt_state.y_offset += klt_state.dy

                    self.klt_state.ul_x = ul_x
                    self.klt_state.ul_y = ul_y
                    self.klt_state.ll_x = ll_x
                    self.klt_state.ll_y = ll_y
                    self.klt_state.ur_x = ur_x
                    self.klt_state.ur_y = ur_y
                    self.klt_state.lr_x = lr_x
                    self.klt_state.lr_y = lr_y
                '''

                return (feature[0] + dx, feature[1] + dy, KLT_TRACKED)

            else:
                self.log.debug("Failed to converge")
                self.log.debug("dx: %f" % dx)
                self.log.debug("dy: %f" % dy)

                self.log.debug("ul_x: %f" % ul_x)
                self.log.debug("ul_y: %f" % ul_y)
                self.log.debug("ul_x: %f" % ul_x)
                self.log.debug("ul_y: %f" % ul_y)

                self.log.debug("ll_x: %f" % ll_x)
                self.log.debug("ll_y: %f" % ll_y)
                self.log.debug("ll_x: %f" % ll_x)
                self.log.debug("ll_y: %f" % ll_y)

                self.log.debug("ur_x: %f" % ur_x)
                self.log.debug("ur_y: %f" % ur_y)
                self.log.debug("ur_x: %f" % ur_x)
                self.log.debug("ur_y: %f" % ur_y)

                self.log.debug("lr_x: %f" % lr_x)
                self.log.debug("lr_y: %f" % lr_y)
                self.log.debug("lr_x: %f" % lr_x)
                self.log.debug("lr_y: %f" % lr_y)

        self.log.error("Max Iterations for feature index: %d found at image depth: %d" % (feature_index, depth))
        raise KLTMaxIterations("Depth: %d, Feature Index: %d" % (depth, feature_index))

    def is_ready(self):
        return self.ready
