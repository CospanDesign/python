import os
import sys
import numpy as np
import cv2
from collections import OrderedDict


def normalize_image(input_image):
    info = np.iinfo(input_image.dtype)
    data = input_image.astype(np.float64)
    data = 255 * data
    output_image = data.astype(np.uint8)
    return output_image

def local_sobel(input_image, pre_filter):

    filter_size = pre_filter
    ddepth = cv2.CV_16S
    scale = 1
    delta = 0

    #XXX: CHANGE THIS TO A CUSTOM SOBEL IMPLEMENTATION!!
    return cv2.Sobel(input_image, ddepth, 1, 0, ksize=filter_size, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)

def sad_compare(left_image, right_image, block_size, disparity, minimum_disparity, texture_threshold, unique_threshold, gui, debug_loc = None): # :(

    images = OrderedDict()
    height, width = left_image.shape
    texture_image = np.zeros((height, width), dtype=np.ushort)
    sad_result_image = np.zeros((height, width), dtype = np.ushort)
    out_image = np.zeros((height, width), dtype=np.ushort)
    #out_image.fill(disparity + 1)
    debug_out_image = np.zeros((height, width), dtype=np.uint8)
    debug_out_image = cv2.cvtColor(debug_out_image, cv2.COLOR_GRAY2BGR)
    #debug_out_image.fill((0, 0, 255))
    if debug_loc is not None:
        debug_row_window = np.zeros((block_size, disparity + (block_size - 1)), dtype=np.ushort)
        debug_block_sum = np.zeros((1, disparity), dtype=np.ushort)

    rows_window = np.zeros((block_size, disparity + (block_size - 1)), dtype=np.ushort)
    RESULT_MULT_VAL = 256 / disparity

    pbar = gui[0]
    ypos = gui[1]
    disp_fail = gui[2]
    res_text = gui[3]
    sad_thresh = gui[4]

    texture_fail = 0
    min_disp_fail = 0
    sad_thresh_fail = 0
    res_val = 0
    sad_array = [0] * disparity
    block_sum = [0] * disparity

    #print ("Range: %d - %d" % (-(block_size // 2), (block_size // 2) + 1))

    # Go through the entire image
    for y in range(height):
        for x in range(width):
            # Check if we are out of bounds of the disparity window, if so set the value to 0 (should this be 255?)
            if  y < (block_size // 2) or \
                y > (height - ((block_size // 2) + 1)) or \
                x > (width - disparity - (block_size - 1)):
                if x == 0:
                    for d in range (disparity + (block_size - 1)):
                        for h in range (-(block_size // 2), (block_size // 2) + 1):
                            rows_window[h][d] = 0
                    for d in range (disparity):
                        block_sum[d] = 0

                # We're done here, the value at that position will be set to 0
                out_image[y, x] = disparity + 1
                debug_out_image[y, x] = (0, 0, 255)
                continue


            rows_window = np.roll(rows_window, -1, axis=0) # Shift things down

            for d in range (disparity + (block_size - 1)):
                rows_window[-1][d] = 0
                for h in range (-(block_size // 2), (block_size // 2) + 1):
                    rows_window[-1][d] += np.abs(left_image[y + h, x] - right_image[y + h, x - (block_size // 2) + d])

            if debug_loc is not None and debug_loc[0] == (x + (block_size // 2)) and debug_loc[1] == (y - (block_size // 2)):
                debug_row_window = rows_window.copy()

            #if x < (block_size - 1):
            if x < (block_size // 2):
                out_image[y - (block_size // 2), x + (block_size // 2)] = disparity + 1
                debug_out_image[y - (block_size // 2), x + (block_size // 2)] = (0, 255, 255)
                #out_image[y, x] = disparity + 1
                #debug_out_image[y, x] = (0, 255, 255)
                continue

            ###########################################################################################################
            # CHECK TEXTURE QUAILITY, Should we even analyze this?! Do a texture check
            ###########################################################################################################
            #XXX: This will propbably need to be changed to incorporate the entire block instead of just a column
            texture_sum = 0
            #for h in range (-(block_size // 2), (block_size // 2) + 1):
            #    texture_sum += np.abs(left_image[y + h, x])
            #texture_sum = np.abs(np.sum(left_image[int(y + (block_size // 2)):int(y + (block_size // 2) * 3), int(x + (block_size // 2)) : int((x + (block_size // 2) * 3))]))
            texture_sum = np.abs(np.sum(left_image[(y - block_size):y, x:(x + block_size)]))
            #texture_sum = np.abs(np.sum(left_image[int(y - (block_size // 2)):int(y + (block_size // 2)), int(x - (block_size // 2)) : int((x + (block_size // 2)))]))

            texture_image[y - (block_size // 2), x + (block_size // 2)] = texture_sum
            if texture_sum < texture_threshold:
                # We're done here by default the value in this position is set to 0
                texture_fail += 1
                out_image[y - (block_size // 2), x + (block_size // 2)] = disparity + 1
                debug_out_image[y - (block_size // 2), x + (block_size // 2)] = (0, 255, 0)
                continue

            ###########################################################################################################
            # SAD
            # The result of this check will be two values, the index of the lowest SAD result and the actual SAD result
            # at that value
            ###########################################################################################################
            ### Perform the SAD analysis
            lowest_index = 0
            for d in range(disparity):
                block_sum[d] = 0
                for h in range(block_size):
                    block_sum[d] += rows_window[h][((block_size - 1) - h) + d]
                if d > 0:
                    if block_sum[d] < block_sum[d - 1]:
                        lowest_index = d

                if debug_loc is not None and debug_loc[0] == (x + (block_size // 2)) and debug_loc[1] == (y - (block_size // 2)):
                    debug_block_sum[0, d] = block_sum[d].copy()

            sad_result = block_sum[lowest_index]
            sad_result_image[y - (block_size // 2), x + (block_size // 2)] = sad_result
            # We now have the index of the lowest SAD result, check if that result is lower than the threshold checker

            #XXX: Is this right??
            #if sad_reult < minimum_disparity:
            if lowest_index < minimum_disparity:
                # We're done our disparity was not greater than the minimum required disparity
                min_disp_fail += 1
                out_image[y - (block_size // 2), x + (block_size // 2)] = disparity + 1
                debug_out_image[y - (block_size // 2), x + (block_size // 2)] = (255, 255, 0)
                #out_image[y, x] = disparity + 1
                #debug_out_image[y, x] = (255, 255, 0)
                continue

            if sad_result > unique_threshold:
                sad_thresh_fail += 1
                out_image[y - (block_size // 2), x + (block_size // 2)] = disparity + 1
                debug_out_image[y - (block_size // 2), x + (block_size // 2)] = (255, 215, 0)
                #out_image[y, x] = disparity + 1
                #debug_out_image[y, x] = (255, 216, 0)
                continue
            

            #XXX: We have not taken into consideration the 'speckle ratio'
            #XXX: We have not taken into consideration the 'speckle window'
            #XXX: We have not taken into consideration the 'Disparity 12 Max Diff'
            res_val += 1
            #out_image[y, x] = RESULT_MULT_VAL * lowest_index
            out_image[y - (block_size // 2), x + (block_size // 2)] = lowest_index


        pbar.value = y
        ypos.value = y
        #texture_fail_text.value = texture_fail
        sad_thresh.value = sad_thresh_fail
        disp_fail.value = min_disp_fail
        res_text.value = res_val

    images["Texture Sum"] = texture_image
    images["Raw SAD Result"] = sad_result_image
    images["Result"] = out_image
    if debug_loc is not None:
        px = debug_loc[0] + (block_size // 2)
        py = debug_loc[1] - (block_size // 2)

        #FULL_IMAGE = True
        #debug_out_image = None

        #if FULL_IMAGE:
        #    debug_out_image = out_image.copy()
        #else:
        #    sx = debug_loc[0] - block_size
        #    sy = debug_loc[1] - block_size

        #    ex = px + block_size + disparity
        #    ey = py + block_size

        #    if sx < 0:
        #        px += sx
        #        sx = 0
        #    if sy < 0:
        #        py += sy
        #        sy = 0
        #    if ex > out_image.shape[1] - 1:
        #        ex = out_image.shape[1] - 1
        #    if ey > out_image.shape[0] - 1:
        #        ey = out_image.shape[0] - 1

        #    px -= sx
        #    py -= sy
        #    debug_out_image = out_image[sy:ey, sx:ex]

        #debug_out_image = cv2.cvtColor(debug_out_image, cv2.COLOR_GRAY2BGR)
        #m = np.amax(debug_out_image)
        #m + 10
        #if m > 255:
        #    m = 255
        #debug_out_image *= (255 // m)
        #print ("M: %s" % str(m))
        cv2.rectangle(debug_out_image, (px - 1, py - 1), (px + disparity + 1, py + 1), (255, 0, 0), 1)
        #cv2.rectangle(debug_out_image, (px - 1, py - 1), (px + disparity + 1, py + 1), (m, 0, 0), 1)
        #debug_out_image[py:py+1, px:px+disparity, 0] = 255

        images["Debug Row Window"] = debug_row_window
        images["Debug Block Sum"] = debug_block_sum
        images["Debug Out Image Window"] = debug_out_image

    return images

