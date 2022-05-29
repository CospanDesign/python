#%matplotlib inline
#import os
#import sys
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import imshow
#from PIL import Image
#from IPython.display import display, Markdown, clear_output
#import ipywidgets as widgets
#import numpy as np
#import cv2
#
#
#big_left_image = cv2.imread(os.path.join("./data/demo_001_l.png"))
#big_right_image = cv2.imread(os.path.join("./data/demo_001_r.png"))
#
#small_sm_left_image = cv2.imread(os.path.join("./data/sm_im_l.png"))
#small_sm_right_image = cv2.imread(os.path.join("./data/sm_im_r.png"))
#
#small_ch_left_image = cv2.imread(os.path.join("./data/sm_ch_l.png"))
#small_ch_right_image = cv2.imread(os.path.join("./data/sm_ch_r.png"))
#
#small_ch_left_image = cv2.cvtColor(np.asarray(small_ch_left_image), cv2.COLOR_BGR2GRAY)
#small_ch_right_image = cv2.cvtColor(np.asarray(small_ch_right_image), cv2.COLOR_BGR2GRAY)
#
#small_sm_left_image = cv2.cvtColor(np.asarray(small_sm_left_image), cv2.COLOR_BGR2GRAY)
#small_sm_right_image = cv2.cvtColor(np.asarray(small_sm_right_image), cv2.COLOR_BGR2GRAY)
#
#big_left_image = cv2.cvtColor(np.asarray(big_left_image), cv2.COLOR_BGR2GRAY)
#big_right_image = cv2.cvtColor(np.asarray(big_right_image), cv2.COLOR_BGR2GRAY)
#
#small_left_image = small_sm_left_image
#small_right_image = small_sm_left_image
#
#left_abs_image = small_left_image
#right_abs_image = small_right_image
#
#left_image = left_abs_image
#right_image = right_abs_image
#
#out = widgets.Output()
#
##b_style = {'description_width':'100px'}
#b_style = {}
##b_layout = {'width': '400px'}
#b_layout = {}
#
#num_disp_slider = widgets.IntSlider(
#    #value=64,
#    #value=32,
#    value=16,
#    min=16,
#    max=128,
#    step=16,
#    description='Number of Disparity:',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#block_size_slider = widgets.IntSlider(
#    #value=15,
#    #value=7,
#    value=5,
#    min=5,
#    max=50,
#    step=2,
#    description='Block Size',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#pre_filter_type = widgets.RadioButtons(
#    options = ["Sobel", "Normalized"],
#    description="Pre Filter Type",
#    disable = False,
#    style = b_style,
#    layout =b_layout
#)
#pre_filter_size_slider = widgets.IntSlider(
#    value=5,
#    min=5,
#    max=25,
#    step=2,
#    description='Pre Filter Size',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#pre_filter_cap_slider = widgets.IntSlider(
#    value=31,
#    min=5,
#    max=62,
#    step=1,
#    description='Pre Filter Cap',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#texture_threshold_slider = widgets.IntSlider(
#    value=10,
#    min=10,
#    max=100,
#    step=1,
#    description='Threshold',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#uniqueness_ratio_slider = widgets.IntSlider(
#    value=15,
#    min=15,
#    max=100,
#    step=1,
#    description='Uniqueness Ratio',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#speckle_range_slider = widgets.IntSlider(
#    value=0,
#    min=0,
#    max=100,
#    step=1,
#    description='Speckle Range',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#speckle_window_size_slider = widgets.IntSlider(
#    value=0,
#    min=0,
#    max=25,
#    step=1,
#    description='Speckle Window Size',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#disp_12_max_diff_slider = widgets.IntSlider(
#    value=0,
#    min=0,
#    max=25,
#    step=1,
#    description='Disparity 12 Max Diff',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#min_disparity_slider = widgets.IntSlider(
#    #value=5,
#    value=0,
#    min=0,
#    max=25,
#    step=1,
#    description='Minimum Disparity',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#file_select = widgets.Select (
#    options=['Check', 'Image'],
#    value = 'Check',
#    description = "File Sel"
#)
#debug_check = widgets.Checkbox(
#    value = True,
#    description='Debug'
#)
#debug_loc_x_slider = widgets.IntSlider(
#    #value=5,
#    #value=50,
#    value=45,
#    min=0,
#    max=100,
#    step=1,
#    description='DBG X Loc',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#debug_loc_x_text = widgets.BoundedIntText(
#    value=45,
#    #value=50,
#    min=0,
#    max=100,
#    step=1,
#    description='DBG X Loc'
#)
#widgets.link((debug_loc_x_slider, 'value'), (debug_loc_x_text, 'value'))
#widgets.link((debug_loc_x_slider, 'max'), (debug_loc_x_text, 'max'))
#
#debug_loc_y_slider = widgets.IntSlider(
#    #value=5,
#    value=65,
#    min=0,
#    max=100,
#    step=1,
#    description='DBG Y Loc',
#    disabled=False,
#    continuous_update=False,
#    orientation='horizontal',
#    readout=True,
#    readout_format='d',
#    style = b_style,
#    layout =b_layout
#)
#debug_loc_y_text = widgets.BoundedIntText(
#    value=65,
#    min=0,
#    max=100,
#    step=1,
#    description='DBG Y Loc'
#)
#    
#widgets.link((debug_loc_y_slider, 'value'), (debug_loc_y_text, 'value'))
#widgets.link((debug_loc_y_slider, 'max'), (debug_loc_y_text, 'max'))
#
#same_check = widgets.Checkbox(
#    value = False,
#    description='Same Image'
#)
#
#image_size_radio = widgets.RadioButtons(
#    options=['small', 'big'],
#    value = 'small',
#    description='Image Size'
#)
#
#items_layout = widgets.Layout(width = '50%')
#items = [debug_check,
#         debug_loc_x_slider,
#         debug_loc_x_text,
#         debug_loc_y_slider,
#         debug_loc_y_text,
#         file_select,
#         same_check,
#         image_size_radio,
#         num_disp_slider,
#         block_size_slider,
#         pre_filter_type,
#         pre_filter_size_slider,
#         pre_filter_cap_slider,
#         texture_threshold_slider,
#         uniqueness_ratio_slider,
#         speckle_range_slider,
#         speckle_window_size_slider,
#         disp_12_max_diff_slider,
#         min_disparity_slider]
#
#def process_file_delta(d = None):
#    global left_image
#    global right_image
#    left_image = None
#    right_image = None
#    print ("Process file delta entered")
#    if file_select.value == 'Check':
#        print ("Use Checker image")
#        small_left_image = small_ch_left_image
#        small_right_image = small_ch_right_image
#    else:
#        print ("Use Demo Image")
#        small_left_image = small_sm_left_image
#        small_right_image = small_sm_right_image
#    
#    if image_size_radio.value == 'small':
#        print ("Small Image Size")
#        left_abs_image = small_left_image
#        right_abs_image = small_right_image
#    else:
#        left_abs_image = big_left_image
#        right_abs_image = big_right_image
#        
#    debug_loc_x_slider.max = left_abs_image.shape[1]
#    debug_loc_y_slider.max = left_abs_image.shape[0]
#
#    if same_check.value:
#        print ("Same Images")
#        right_image = left_abs_image
#        left_image = left_abs_image
#    else:
#        print ("Different Images")
#        right_image = right_abs_image
#        left_image = left_abs_image
#        
# 
#
#        
#image_size_radio.observe(process_file_delta, names='value')
#same_check.observe(process_file_delta, names='value')
#file_select.observe(process_file_delta, names='value')
#
#process_file_delta(None)
#
#widgets.VBox(children = items, layout=items_layout)

#%matplotlib inline
#import matplotlib.pyplot as plt
#
##DISPLAY_SIZE = (20, 20)
##plt.figure(figsize=DISPLAY_SIZE)
#
##columns = 2
##imgs = [left_image, right_image]
##for i, image in enumerate(imgs):
##    plt.subplot(int(len(imgs) / columns + 1), int(columns), i + 1)
##    plt.imshow(image, cmap='gray')
#    
#height, width = left_image.shape
#pbar = widgets.IntProgress(
#    value = 0,
#    min = 0,
#    max = height,
#    description='Progress',
#    orientation='horizontal'
#)
#y_pos_int_text = widgets.IntText(
#    value = 0,
#    description = "Y Pos"
#)
#texture_fail_text = widgets.IntText(
#    value = 0,
#    description = "Texture Fail"
#)
#min_disp_fail_text = widgets.IntText(
#    value = 0,
#    description = "Min Disp Fail"
#)
#sad_thresh_fail_text = widgets.IntText(
#    value = 0,
#    description = "SAD Thresh Fail"
#)
#res_text = widgets.IntText(
#    value = 0,
#    description = "Results"
#)
#status_text = widgets.Text(
#    value='Ready',
#    description='Status'
#)
#
##clear_output
#y_pos_int_text.value = 0
#texture_fail_text.value = 0
#min_disp_fail_text.value = 0
#sad_thresh_fail_text.value = 0
#res_text.value 
#widgets.VBox([pbar, status_text, y_pos_int_text, texture_fail_text, min_disp_fail_text, sad_thresh_fail_text, res_text])

#%matplotlib inline
#
#import os
#import sys
#import matplotlib.pyplot as plt
#import numpy as np
#import cv2
#
#from collections import OrderedDict
#
#from sad_block_matching import normalize_image
#from sad_block_matching import local_sobel
#from sad_block_matching import sad_compare
#
#images = OrderedDict()
#
#def custom_sbm():
#    status_text.value = 'Start'
#    filter_cap = pre_filter_cap_slider.value
#    global images
#    images["Original Image"] = (left_image, right_image)
#    pbar.max = left_image.shape[0]
#
#    #Pre-Filter, only support SOBEL for now
#    status_text.value = 'Pre-Filter'
#    lsobel = local_sobel(left_image, pre_filter_size_slider.value)
#    rsobel = local_sobel(right_image, pre_filter_size_slider.value)
#
#    #if debug_check.value: images["Sobel Image"] = (lsobel, rsobel)
#    images["Sobel Image"] = (lsobel, rsobel)
#
#    #Clip the pre-filter output
#    status_text.value = 'Pre-Filter Clip'
#    lsobel_clipped = np.clip(lsobel, -filter_cap, filter_cap)
#    rsobel_clipped = np.clip(rsobel, -filter_cap, filter_cap)
#
#    #if debug_check.value: images["Clipped Sobel Image"] = (lsobel_clipped, rsobel_clipped)
#    images["Clipped Sobel Image"] = (lsobel_clipped, rsobel_clipped)
#
#    TEST = False
#    #TEST = True
#
#    if TEST:
#        status_text.value = 'Get Test Images'
#        test_image = normalize_image(np.zeros((height, width), dtype=np.short))
#        test_image = np.zeros((height, width), dtype=np.uint8)
#        #if debug_check.value: images["Test"] = test_image
#        images["Test"] = test_image
#    else:
#        status_text.value = 'SAD Analysis'
#        loc = None
#        if debug_check.value:
#            loc = (debug_loc_x_slider.value, debug_loc_y_slider.value)
#            print ("Debug Location: %d, %d" % (loc[0], loc[1]))
#            
#        block_size = block_size_slider.value
#            
#        sc_images = sad_compare(
#                                lsobel_clipped,
#                                rsobel_clipped,
#                                block_size,
#                                num_disp_slider.value,
#                                min_disparity_slider.value,
#                                texture_threshold_slider.value,
#                                uniqueness_ratio_slider.value,
#                                gui = (pbar, y_pos_int_text, min_disp_fail_text, res_text, sad_thresh_fail_text),
#                                debug_loc = loc)
#
#        for key in sc_images:
#            images[key] = sc_images[key]
#        cv2.imwrite("sad_image.png", images["Raw SAD Result"])
#        cv2.imwrite("result.png", images["Result"])
#        debug_values = []
#        debug_lowest_index = []
#        if debug_check.value:
#            dbs = images["Debug Block Sum"]
#            rslt = images["Result"]
#            for x in range(dbs.shape[1]):
#                debug_values.append(dbs[0, x])
#                debug_lowest_index.append(rslt[loc[1] - (block_size // 2), loc[0] + (block_size // 2) + x])
#            
#            for x in range (len(debug_values)):
#                print ("Image[%2d] = Val: %d : Disp: %d" % (x, debug_values[x], debug_lowest_index[x]))
#                
#
#    status_text.value = 'Finished'
#
#
#
#custom_sbm()
#
#rows = len(images)
#columns = 3
#DISPLAY_SIZE = (20, rows * 6)
#DPI=100
#plt.figure(figsize=DISPLAY_SIZE, dpi=DPI)
#
#i = 0
#for key in images:
#    if isinstance(images[key], np.ndarray):
#        plt.subplot(rows, columns, (i * columns) + 2)
#        if len(images[key].shape) == 2:
#            plt.imshow(images[key], cmap='gray')
#        else:
#            plt.imshow(images[key])
#        plt.title(key)
#        ax = plt.gca()
#        ax.axes.xaxis.set_visible(False)
#        ax.axes.yaxis.set_visible(False)
#        
#    if isinstance(images[key], tuple) and len(images[key]) == 2:
#        plt.subplot(rows, columns, (i * columns) + 1)
#        plt.imshow(images[key][0], cmap='gray')
#        plt.title("Right %s" % key)
#        ax = plt.gca()
#        ax.axes.xaxis.set_visible(False)
#        ax.axes.yaxis.set_visible(False)
#        plt.subplot(rows, columns, (i * columns) + 3)
#        plt.imshow(images[key][1], cmap='gray')
#        plt.title("Left %s" % key)
#        ax = plt.gca()
#        ax.axes.xaxis.set_visible(False)
#        ax.axes.yaxis.set_visible(False)
#    i += 1%matplotlib inline
#
#import os
#import sys
#import matplotlib.pyplot as plt
#import numpy as np
#import cv2
#
#from collections import OrderedDict
#
#from sad_block_matching import normalize_image
#from sad_block_matching import local_sobel
#from sad_block_matching import sad_compare
#
#images = OrderedDict()
#
#def custom_sbm():
#    status_text.value = 'Start'
#    filter_cap = pre_filter_cap_slider.value
#    global images
#    images["Original Image"] = (left_image, right_image)
#    pbar.max = left_image.shape[0]
#
#    #Pre-Filter, only support SOBEL for now
#    status_text.value = 'Pre-Filter'
#    lsobel = local_sobel(left_image, pre_filter_size_slider.value)
#    rsobel = local_sobel(right_image, pre_filter_size_slider.value)
#
#    #if debug_check.value: images["Sobel Image"] = (lsobel, rsobel)
#    images["Sobel Image"] = (lsobel, rsobel)
#
#    #Clip the pre-filter output
#    status_text.value = 'Pre-Filter Clip'
#    lsobel_clipped = np.clip(lsobel, -filter_cap, filter_cap)
#    rsobel_clipped = np.clip(rsobel, -filter_cap, filter_cap)
#
#    #if debug_check.value: images["Clipped Sobel Image"] = (lsobel_clipped, rsobel_clipped)
#    images["Clipped Sobel Image"] = (lsobel_clipped, rsobel_clipped)
#
#    TEST = False
#    #TEST = True
#
#    if TEST:
#        status_text.value = 'Get Test Images'
#        test_image = normalize_image(np.zeros((height, width), dtype=np.short))
#        test_image = np.zeros((height, width), dtype=np.uint8)
#        #if debug_check.value: images["Test"] = test_image
#        images["Test"] = test_image
#    else:
#        status_text.value = 'SAD Analysis'
#        loc = None
#        if debug_check.value:
#            loc = (debug_loc_x_slider.value, debug_loc_y_slider.value)
#            print ("Debug Location: %d, %d" % (loc[0], loc[1]))
#            
#        block_size = block_size_slider.value
#            
#        sc_images = sad_compare(
#                                lsobel_clipped,
#                                rsobel_clipped,
#                                block_size,
#                                num_disp_slider.value,
#                                min_disparity_slider.value,
#                                texture_threshold_slider.value,
#                                uniqueness_ratio_slider.value,
#                                gui = (pbar, y_pos_int_text, min_disp_fail_text, res_text, sad_thresh_fail_text),
#                                debug_loc = loc)
#
#        for key in sc_images:
#            images[key] = sc_images[key]
#        cv2.imwrite("sad_image.png", images["Raw SAD Result"])
#        cv2.imwrite("result.png", images["Result"])
#        debug_values = []
#        debug_lowest_index = []
#        if debug_check.value:
#            dbs = images["Debug Block Sum"]
#            rslt = images["Result"]
#            for x in range(dbs.shape[1]):
#                debug_values.append(dbs[0, x])
#                debug_lowest_index.append(rslt[loc[1] - (block_size // 2), loc[0] + (block_size // 2) + x])
#            
#            for x in range (len(debug_values)):
#                print ("Image[%2d] = Val: %d : Disp: %d" % (x, debug_values[x], debug_lowest_index[x]))
#                
#
#    status_text.value = 'Finished'
#
#
#
#custom_sbm()
#
#rows = len(images)
#columns = 3
#DISPLAY_SIZE = (20, rows * 6)
#DPI=100
#plt.figure(figsize=DISPLAY_SIZE, dpi=DPI)
#
#i = 0
#for key in images:
#    if isinstance(images[key], np.ndarray):
#        plt.subplot(rows, columns, (i * columns) + 2)
#        if len(images[key].shape) == 2:
#            plt.imshow(images[key], cmap='gray')
#        else:
#            plt.imshow(images[key])
#        plt.title(key)
#        ax = plt.gca()
#        ax.axes.xaxis.set_visible(False)
#        ax.axes.yaxis.set_visible(False)
#        
#    if isinstance(images[key], tuple) and len(images[key]) == 2:
#        plt.subplot(rows, columns, (i * columns) + 1)
#        plt.imshow(images[key][0], cmap='gray')
#        plt.title("Right %s" % key)
#        ax = plt.gca()
#        ax.axes.xaxis.set_visible(False)
#        ax.axes.yaxis.set_visible(False)
#        plt.subplot(rows, columns, (i * columns) + 3)
#        plt.imshow(images[key][1], cmap='gray')
#        plt.title("Left %s" % key)
#        ax = plt.gca()
#        ax.axes.xaxis.set_visible(False)
#        ax.axes.yaxis.set_visible(False)
#    i += 1
