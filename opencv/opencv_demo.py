#! /usr/bin/env python

# Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)
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
import logging
import argparse

from PyQt4.Qt import QApplication
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *


import numpy as np
import cv2
import random
from matplotlib import pyplot as plt
from matplotlib.figure import SubplotParams
from math import *
import klt as klt_module
from klt import KLT

from utils import Arrow
from utils import get_image_transform
from utils import scale_patch
from utils import get_simple_patch

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "KLTGUIs:\n" \
         "\tSomething\n" \
         "\n"

TITLE = "KLT Debug"


VIDEO_FILE                      = "data/videoplayback.mp4"
#PYRAMID_DEPTH                   = 2
PYRAMID_DEPTH                   = 3

PAD_SIZE                        = 40


STATE_STOP  = 0
STATE_GO    = 1


RED   = (0xFF, 0x00, 0x00)
GREEN = (0x00, 0xFF, 0x00)
BLUE  = (0x00, 0x00, 0xFF)

SQUARE_SIZE = 10

SCENE_WIDTH = 1400
SCENE_HEIGHT = 800
GUI_WIDTH = SCENE_WIDTH + 200
GUI_HEIGHT = SCENE_HEIGHT + 200

IMAGE_SCALE_WIDTH               = 300.0

DRAW_PATCH_SIZE                 = 20
REF_PATH_SCALE                  = 100

CURRENT_IMAGE_PIPE_OFFSET       = 200


class KLTWorker(QObject):

    update_object = pyqtSignal([object])

    def __init__(self):
        super (KLTWorker, self).__init__()

    @pyqtSlot(object, object)
    def thread_init(self, klt, new_frame_signal):
        #print "In thread init!"
        new_frame_signal.connect(self.new_frame)

        self.klt = klt
        self.klt.set_update_callback(self.update_cb)
        self.paused = False
        self.sem = QSemaphore(1)

    @pyqtSlot(object)
    def new_frame(self, frame):
        #print "Track a frame..."
        if self.sem.available() > 0:
            self.sem.acquire()
        #print "Acquired!"
        self.klt.track(frame)
        self.sem.release()

    def is_ready(self):
        return (self.sem.available() == 1)

    def continue_step(self):
        print "Continue!"
        if self.sem.available() == 0:
            self.sem.release()

    def update_cb(self, klt_state):
        print "In Callback..."
        self.update_object.emit(klt_state)
        self.sem.acquire()

class Scene(QGraphicsScene):

    def __init__(self, parent = None):
        super(Scene, self).__init__(parent = parent)
        self.setSceneRect(0, 0, SCENE_WIDTH, SCENE_HEIGHT)
        self.template_image = QPixmap()
        self.current_image = QPixmap()
        self.template_patch = QPixmap()
        self.current_patch = QPixmap()
        self.transform_patch = QPixmap()
        self.image_diff = QPixmap()
        self.affine_fb_text = QGraphicsTextItem()
        self.translate_fb_text = QGraphicsTextItem()

        #Items that are part of the scene, these can be manipulated in the scene
        self.template_image_item = None
        self.current_image_item = None
        self.template_patch_item = None

        self.template_patch_tf_item = None

        self.current_patch_item = None
        self.transform_patch_item = None
        self.image_diff_item = None

        self.reference_path_item = None
        self.warp_path_item = None

        self.ti_tp_arrow_item = None
        self.ci_cp_arrow_item = None
        self.tp_w_arrow_item = None
        self.w_t_arrow_item = None
        self.tp_rw_arrow_item = None
        self.rw_tp2_arrow_item = None

        self.feedback_arrow = None
        self.feedback_rect_item = None

        self.current_image_width = 0
        self.current_image_height = 0

        self.current_patch_width = 0
        self.current_patch_height = 0

        self.draw_lines = False
        self.draw_fb_config = False

        self.affine_feedback_txt = None
        self.translate_feedback_txt = None

    def draw_template_patch(self, klt_state):
        scene_rect = self.sceneRect()

        posx = scene_rect.x() + scene_rect.width() - self.current_image_width - PAD_SIZE - self.current_patch_width
        posy = scene_rect.y() + self.current_image_height

        #Get the patch
        #y_start = int(klt_state.feature_pos[1] - klt_state.patch_height / 2)
        #x_start = int(klt_state.feature_pos[0] - klt_state.patch_width / 2)
        #y_end = int(klt_state.feature_pos[1] + (klt_state.patch_height / 2) + 1)
        #x_end = int(klt_state.feature_pos[0] + (klt_state.patch_width / 2) + 1)

        #print "Y Range: %d:%d" % (y_start, y_end)
        #print "X Range: %d:%d" % (x_start, x_end)
        patch = get_simple_patch(klt_state.template_image, klt_state.feature_pos[0], klt_state.feature_pos[1], klt_state.patch_width)

        #patch = klt_state.template_image[y_start:(y_end), x_start:(x_end):1].astype(np.uint8)
        print "Patch: %s" % str(patch)
        #patch = klt_state.template_image[y_start:y_end:1, x_start:x_end:1]
        #patch = np.kron(patch, np.ones((self.current_patch_width, self.current_patch_height), dtype=np.float32)).astype(np.uint8)
        #patch = np.kron(patch, np.ones(shape=(self.current_patch_width, self.current_patch_height), dtype=np.float32)).astype(np.uint8)
        patch = np.kron(patch, np.ones(shape=(DRAW_PATCH_SIZE, DRAW_PATCH_SIZE), dtype=np.float32)).astype(np.uint8)
        patch = cv2.cvtColor(patch, cv2.COLOR_GRAY2RGB)

        self.template_patch.convertFromImage(QImage(patch, patch.shape[0], patch.shape[1], QImage.Format_RGB888))

        #self.template_patch = self.template_patch.scaledToWidth(100)

        if self.template_patch_item is None:
            posx = scene_rect.x() + (self.current_image_width / 2) - (patch.shape[1] / 2)
            posy = scene_rect.y() + self.current_image_height + PAD_SIZE

            self.template_patch_item = self.addPixmap(self.template_patch)
            self.template_patch_item.setPos(posx, posy)

        if self.template_patch_tf_item is None:
            posx = scene_rect.x() + (scene_rect.width() / 2) - (self.current_patch_width / 2)
            posy = scene_rect.y() + self.current_image_height + PAD_SIZE

            self.template_patch_tf_item = self.addPixmap(self.template_patch)
            self.template_patch_tf_item.setPos(posx, posy)

    def draw_current_patch(self, klt_state):
        scene_rect = self.sceneRect()

        #posx = scene_rect.x() + scene_rect.width() - (self.current_image_width / 2) - (self.current_patch_width)
        posx = scene_rect.x() + scene_rect.width() - ((self.current_image_width / 2) + (self.current_patch_width / 2))
        posy = scene_rect.y() + self.current_image_height + PAD_SIZE + CURRENT_IMAGE_PIPE_OFFSET


        #Get the patch
        #y_start = int((klt_state.feature_pos[1] + klt_state.dy) - klt_state.patch_height / 2)
        #x_start = int((klt_state.feature_pos[0] + klt_state.dx) - klt_state.patch_width / 2)
        #y_end   = int((klt_state.feature_pos[1] + klt_state.dy) + klt_state.patch_height / 2)
        #x_end   = int((klt_state.feature_pos[0] + klt_state.dx) + klt_state.patch_width / 2)
        #patch = klt_state.current_image[y_start:(y_end + 1):1, x_start:(x_end + 1):1]
        patch = get_simple_patch(klt_state.current_image, klt_state.feature_pos[0], klt_state.feature_pos[1], klt_state.patch_width)
        patch = np.kron(patch, np.ones(shape=(DRAW_PATCH_SIZE, DRAW_PATCH_SIZE), dtype=np.float32)).astype(np.uint8)
        patch = cv2.cvtColor(patch, cv2.COLOR_GRAY2RGB)
        self.current_patch.convertFromImage(QImage(patch, patch.shape[0], patch.shape[1], QImage.Format_RGB888))

        if self.current_patch_item is None:
            self.current_patch_item = self.addPixmap(self.current_patch)
            self.current_patch_item.setPos(posx, posy)

    def draw_transform_patch(self, klt_state):
        scene_rect = self.sceneRect()

        posx = scene_rect.x() + (scene_rect.width() / 2) - (self.current_patch.width() / 2)
        posy = scene_rect.y() + self.current_image_height + PAD_SIZE + CURRENT_IMAGE_PIPE_OFFSET


        patch = get_image_transform(klt_state.current_image,
                                    klt_state.feature_pos[0] + klt_state.dx,
                                    klt_state.feature_pos[1] + klt_state.dy,
                                    klt_state.axx, klt_state.ayx,
                                    klt_state.axy, klt_state.ayy,
                                    klt_state.patch_width)

        #Get the patch
        patch = np.kron(patch, np.ones((DRAW_PATCH_SIZE, DRAW_PATCH_SIZE))).astype(np.uint8)
        patch = cv2.cvtColor(patch, cv2.COLOR_GRAY2RGB)
        self.transform_patch.convertFromImage(QImage(patch, patch.shape[0], patch.shape[1], QImage.Format_RGB888))

        if self.transform_patch_item is None:
            self.transform_patch_item = self.addPixmap(self.transform_patch)
            self.transform_patch_item.setPos(posx, posy)

    def draw_image_diff(self, klt_state):
        scene_rect = self.sceneRect()
        patch = np.kron(klt_state.image_diff, np.ones((DRAW_PATCH_SIZE, DRAW_PATCH_SIZE))).astype(np.uint8)
        patch = cv2.cvtColor(patch, cv2.COLOR_GRAY2RGB)
        self.image_diff.convertFromImage(QImage( patch, patch.shape[0], patch.shape[1], QImage.Format_RGB888))

        if self.image_diff_item is None:
            self.image_diff_item = self.addPixmap(self.image_diff)
            posx = scene_rect.x() + scene_rect.width() / 2 - self.image_diff.width() / 2
            posy = scene_rect.y() + self.current_image_height + PAD_SIZE + CURRENT_IMAGE_PIPE_OFFSET + self.current_patch_height + 50
            self.image_diff_item.setPos(posx, posy)

    def draw_template_image(self, klt_state):
        template_image = cv2.cvtColor(klt_state.template_image, cv2.COLOR_GRAY2RGB)
        cv2.rectangle(  template_image,
                        (int(klt_state.feature_pos[0] - (klt_state.patch_width  / 2)),
                         int(klt_state.feature_pos[1] - (klt_state.patch_height / 2))),
                        (int(klt_state.feature_pos[0] + (klt_state.patch_width  / 2)),
                         int(klt_state.feature_pos[1] + (klt_state.patch_height / 2))),
                        GREEN, -1)
        image_height, image_width, image_channel = template_image.shape
        bytesPerLine = image_channel * image_width

        divide_factor = IMAGE_SCALE_WIDTH / float(image_width)
        template_image = cv2.resize(template_image, (0, 0), fx=divide_factor, fy=divide_factor)

        image_height, image_width, image_channel = template_image.shape
        bytesPerLine = image_channel * image_width

        self.template_image.convertFromImage(QImage(template_image.data, image_width, image_height, bytesPerLine, QImage.Format_RGB888))

        if self.template_image_item is None:
            self.template_image_item = self.addPixmap(self.template_image)
            self.template_image_item.setPos(0, 0)


        return template_image

    def draw_current_image(self, klt_state):
        scene_rect = self.sceneRect()
        current_image = cv2.cvtColor(klt_state.current_image, cv2.COLOR_GRAY2RGB)
        cv2.rectangle(  current_image,
                        (int(klt_state.feature_pos[0] + klt_state.dx - (klt_state.patch_width  / 2)),
                         int(klt_state.feature_pos[1] + klt_state.dy - (klt_state.patch_height / 2))),
                        (int(klt_state.feature_pos[0] + klt_state.dx + (klt_state.patch_width  / 2)),
                         int(klt_state.feature_pos[1] + klt_state.dy + (klt_state.patch_height / 2))),
                        GREEN, -1)
        image_height, image_width, image_channel = current_image.shape

        divide_factor = IMAGE_SCALE_WIDTH / float(image_width)
        current_image = cv2.resize(current_image, (0, 0), fx=divide_factor, fy=divide_factor)
        image_height, image_width, image_channel = current_image.shape
        bytesPerLine = image_channel * image_width
        self.current_image.convertFromImage(QImage(current_image, image_width, image_height, bytesPerLine, QImage.Format_RGB888))

        if self.current_image_item is None:
            self.current_image_item = self.addPixmap(self.current_image)
            self.current_image_item.setPos(scene_rect.x() + scene_rect.width() - image_width, 0)

        return current_image

    def draw_reference_warp_box(self, klt_state):

        scene_rect = self.sceneRect()
        posx = scene_rect.x() + self.current_patch_width + PAD_SIZE + 100
        posy = scene_rect.y() + self.current_image_height + PAD_SIZE + (self.current_patch_height / 2) - (REF_PATH_SCALE / 2)

        '''
        posx = scene_rect.x()
        posy = scene_rect.y() + self.current_image_height + PAD_SIZE
        '''

        ul = (posx, posy)
        ur = (posx + (1 * REF_PATH_SCALE), posy)
        bl = (posx, posy + (1 * REF_PATH_SCALE))
        br = (posx + (1 * REF_PATH_SCALE), posy + (1 * REF_PATH_SCALE))

        top_pen = QPen()
        top_pen.setWidth(5)
        top_pen.setColor(QColor("green"))

        right_pen = QPen()
        right_pen.setWidth(5)
        right_pen.setColor(QColor("red"))

        left_pen = QPen()
        left_pen.setWidth(5)
        left_pen.setColor(QColor("blue"))

        bottom_pen = QPen()
        bottom_pen.setWidth(5)
        bottom_pen.setColor(QColor("purple"))

        ul_point = QPointF(ul[0], ul[1])
        ur_point = QPointF(ur[0], ur[1])
        bl_point = QPointF(bl[0], bl[1])
        br_point = QPointF(br[0], br[1])

        first_draw = False
        if self.reference_path_item is None:
            first_draw = True
            self.reference_path_item = []

            self.reference_path_item.append(self.addLine(QLineF(ul[0], ul[1], ur[0], ur[1]), top_pen))
            self.reference_path_item.append(self.addLine(QLineF(ul[0], ul[1], bl[0], bl[1]), left_pen))
            self.reference_path_item.append(self.addLine(QLineF(ur[0], ur[1], br[0], br[1]), right_pen))
            self.reference_path_item.append(self.addLine(QLineF(bl[0], bl[1], br[0], br[1]), bottom_pen))

            pbr = self.find_bounding_box(self.reference_path_item)
            t = self.addText("No Transform")
            tbr = t.boundingRect()
            posx = posx + (pbr.width() / 2) - (tbr.width() / 2)
            posy = posy - tbr.height()

            t.setPos(posx, posy)
        else:

            line = self.reference_path_item[0].setLine(ul[0], ul[1], ur[0], ur[1])
            line = self.reference_path_item[1].setLine(ul[0], ul[1], bl[0], bl[1])
            line = self.reference_path_item[2].setLine(ur[0], ur[1], br[0], br[1])
            line = self.reference_path_item[3].setLine(bl[0], bl[1], br[0], br[1])

        #self.sceneRectChanged.emit(self.sceneRect())

    def draw_affine_warp_box(self, klt_state):
        image_width = len(klt_state.template_image[0])
        image_height = len(klt_state.template_image)
        divide_factor = IMAGE_SCALE_WIDTH / float(image_width)
        image_width *= divide_factor
        image_height *= divide_factor

        scene_rect = self.sceneRect()
        #posx = scene_rect.x() + scene_rect.width() - self.current_image_width -  - PAD_SIZE - (self.current_patch_width / 2)
        #posy = scene_rect.y() + self.current_image_height + PAD_SIZE + (self.current_patch_height / 2)

        posx = scene_rect.x() + scene_rect.width() - self.current_image_width - PAD_SIZE - self.current_patch_width
        #posy = scene_rect.y() + self.current_image_height + PAD_SIZE + (self.current_patch_height / 2) - (REF_PATH_SCALE / 2)
        posy = scene_rect.y() + self.current_image_height + PAD_SIZE + CURRENT_IMAGE_PIPE_OFFSET + (self.current_patch_height / 2) - (REF_PATH_SCALE / 2)

        ul = (-(REF_PATH_SCALE / 2),  -(REF_PATH_SCALE / 2))
        ur = ( (REF_PATH_SCALE / 2),  -(REF_PATH_SCALE / 2))
        bl = (-(REF_PATH_SCALE / 2),   (REF_PATH_SCALE / 2))
        br = ( (REF_PATH_SCALE / 2),   (REF_PATH_SCALE / 2))

        ul_s = [0] * 2
        ur_s = [0] * 2
        bl_s = [0] * 2
        br_s = [0] * 2

        ul_s[0] = (klt_state.axx * ul[0]) + (klt_state.axy * ul[1]) + posx + (REF_PATH_SCALE / 2)
        ul_s[1] = (klt_state.ayx * ul[0]) + (klt_state.ayy * ul[1]) + posy + (REF_PATH_SCALE / 2)

        ur_s[0] = (klt_state.axx * ur[0]) + (klt_state.axy * ur[1]) + posx + (REF_PATH_SCALE / 2)
        ur_s[1] = (klt_state.ayx * ur[0]) + (klt_state.ayy * ur[1]) + posy + (REF_PATH_SCALE / 2)

        bl_s[0] = (klt_state.axx * bl[0]) + (klt_state.axy * bl[1]) + posx + (REF_PATH_SCALE / 2)
        bl_s[1] = (klt_state.ayx * bl[0]) + (klt_state.ayy * bl[1]) + posy + (REF_PATH_SCALE / 2)

        br_s[0] = (klt_state.axx * br[0]) + (klt_state.axy * br[1]) + posx + (REF_PATH_SCALE / 2)
        br_s[1] = (klt_state.ayx * br[0]) + (klt_state.ayy * br[1]) + posy + (REF_PATH_SCALE / 2)

        ur = klt_state.axx * ur[0] + klt_state.axy

        top_pen = QPen()
        top_pen.setWidth(5)
        top_pen.setColor(QColor("green"))

        right_pen = QPen()
        right_pen.setWidth(5)
        right_pen.setColor(QColor("red"))

        left_pen = QPen()
        left_pen.setWidth(5)
        left_pen.setColor(QColor("blue"))

        bottom_pen = QPen()
        bottom_pen.setWidth(5)
        bottom_pen.setColor(QColor("purple"))

        first_draw = False
        if self.warp_path_item is None:
            first_draw = True
            self.warp_path_item = []

            self.warp_path_item.append(self.addLine(ul_s[0], ul_s[1], ur_s[0], ur_s[1], top_pen))
            self.warp_path_item.append(self.addLine(ul_s[0], ul_s[1], bl_s[0], bl_s[1], left_pen))
            self.warp_path_item.append(self.addLine(ur_s[0], ur_s[1], br_s[0], br_s[1], right_pen))
            self.warp_path_item.append(self.addLine(bl_s[0], bl_s[1], br_s[0], br_s[1], bottom_pen))

            pbr = self.find_bounding_box(self.warp_path_item)
            t = self.addText("Warp (Affine Transform)")
            tbr = t.boundingRect()
            posx = posx + (pbr.width() / 2) - (tbr.width() / 2)
            posy = posy - tbr.height()

            t.setPos(posx, posy)
        else:

            line = self.warp_path_item[0].setLine(ul_s[0], ul_s[1], ur_s[0], ur_s[1])
            line = self.warp_path_item[1].setLine(ul_s[0], ul_s[1], bl_s[0], bl_s[1])
            line = self.warp_path_item[2].setLine(ur_s[0], ur_s[1], br_s[0], br_s[1])
            line = self.warp_path_item[3].setLine(bl_s[0], bl_s[1], br_s[0], br_s[1])

    def draw_annotations(self, klt_state):
        scene_rect = self.sceneRect()

        if self.ti_tp_arrow_item is None:
            arrow = Arrow(self.template_image_item, self.template_patch_item)
            arrow.setColor(QColor("black"))
            self.ti_tp_arrow_item = self.addItem(arrow)

        if self.ci_cp_arrow_item is None:
            arrow = Arrow(self.current_image_item, self.current_patch_item)
            arrow.setColor(QColor("black"))
            self.ci_cp_arrow_item = self.addItem(arrow)

        bounding_box = self.find_bounding_box(self.reference_path_item)
        if self.tp_rw_arrow_item is None:
            arrow = Arrow(self.template_patch_item, self.reference_path_item)
            arrow.set_end_box(bounding_box)
            arrow.setColor(QColor("black"))
            self.tp_rw_arrow_item = self.addItem(arrow)
        #else:
        #    self.tp_rw_arrow_item.getItem().set_end_box(bounding_box)

        if self.rw_tp2_arrow_item is None:
            arrow = Arrow(self.reference_path_item, self.template_patch_tf_item)
            arrow.set_start_box(bounding_box)
            arrow.setColor(QColor("black"))
            self.rw_tp2_arrow_item = self.addItem(arrow)
        #else:
        #    self.rw_tp2_arrow_item.getItem().set_end_box(bounding_box)

        bounding_box = self.find_bounding_box(self.warp_path_item)
        #print "Bounding Box: %s" % str(bounding_box)
        if self.tp_w_arrow_item is None:
            arrow = Arrow(self.current_patch_item, self.warp_path_item)
            arrow.set_end_box(bounding_box)
            arrow.setColor(QColor("black"))
            self.tp_w_arrow_item = self.addItem(arrow)

        #else:
        #    self.tp_w_arrow_item.getItem().set_end_box(bounding_box)

        if self.w_t_arrow_item is None:
            arrow = Arrow(self.warp_path_item, self.transform_patch_item)
            arrow.set_start_box(bounding_box)
            arrow.setColor(QColor("black"))
            self.w_t_arrow_item = self.addItem(arrow)

        #else:
        #    self.w_t_arrow.getItem().set_end_box(bounding_box)

        if not self.draw_lines:
            x1 = scene_rect.x() + (scene_rect.width() / 2) - (self.current_patch_width / 2) - 50
            x2 = scene_rect.x() + (scene_rect.width() / 2) + (self.current_patch_width / 2) + 50
            y1 = scene_rect.y() + self.current_image_height + PAD_SIZE + CURRENT_IMAGE_PIPE_OFFSET + self.current_patch_height + 20
            y2 = scene_rect.y() + self.current_image_height + PAD_SIZE + CURRENT_IMAGE_PIPE_OFFSET + self.current_patch_height + 20
            pen = QPen()
            pen.setWidth(5)
            pen.setColor(QColor("black"))

            self.addLine(QLineF(x1, y1, x2, y2), pen)


            x1 = scene_rect.x() + (scene_rect.width() / 2) - (self.current_patch_width / 2) - 60
            x2 = scene_rect.x() + (scene_rect.width() / 2) - (self.current_patch_width / 2) - 40
            y1 = scene_rect.y() + self.current_image_height + PAD_SIZE + CURRENT_IMAGE_PIPE_OFFSET + self.current_patch_height - 20
            y2 = scene_rect.y() + self.current_image_height + PAD_SIZE + CURRENT_IMAGE_PIPE_OFFSET + self.current_patch_height - 20
            pen = QPen()
            pen.setWidth(5)
            pen.setColor(QColor("black"))

            self.addLine(QLineF(x1, y1, x2, y2), pen)

            self.draw_lines = True

    def draw_feedback(self, klt_state):
        scene_rect = self.sceneRect()
        if not self.draw_fb_config:
            #Draw the current configuration
            posx = scene_rect.x() + scene_rect.width() - self.current_image_width - PAD_SIZE - self.current_patch_width
            posy = scene_rect.y() + self.current_image_height + PAD_SIZE + CURRENT_IMAGE_PIPE_OFFSET + self.current_patch_height + 50

            pen = QPen()
            pen.setWidth(5)
            end = scene_rect.x() + scene_rect.width() - ((self.current_image_width / 2) + (self.current_patch_width / 2)) + self.current_patch_width
            width = end - posx
            pen.setColor(QColor("black"))

            brush = QBrush(QColor("gray"))
            self.feedback_rect_item = self.addRect(   posx,
                            posy,
                            width,
                            self.current_patch_height,
                            pen,
                            brush)

            #Draw where the Affine transform points to the affine block
            affine_posx = posx
            affine_posy = posy
            affine_bounding_box = QRectF(affine_posx, affine_posy, self.current_patch_width, self.current_patch_height)
            abox = self.find_bounding_box(self.warp_path_item)
            affine_bounding_box.setX(abox.x())
            affine_bounding_box.setWidth(abox.width())
            arrow = Arrow(self.feedback_rect_item, self.warp_path_item)
            arrow.set_start_box(affine_bounding_box)
            arrow.set_end_box(abox)
            self.addItem(arrow)

            translate_posx = scene_rect.x() + scene_rect.width() - ((self.current_image_width / 2) + (self.current_patch_width / 2))
            translate_posy = posy

            #translate_box = QRectF(self.current_patch_item.boundingRect())
            box = self.current_patch_item.boundingRect()
            translate_box = QRectF(translate_posx, translate_posy, box.width(), box.height())
            translate_box.setX(translate_posx)
            translate_box.setY(translate_posy)
            #translate_bounding_box = QRectF(affine_posx, affine_posy, self.current_patch_width, self.current_patch_height)
            arrow = Arrow(self.feedback_rect_item, self.current_patch_item)
            arrow.set_start_box(translate_box)
            #arrow.set_end_box(self.current_patch.boundingRect())
            self.addItem(arrow)


            self.feedback_arrow = Arrow(self.image_diff_item, self.feedback_rect_item)
            #abox.setX(affine_posx)
            #abox.setY(affine_posy)
            self.feedback_arrow.set_end_box(self.feedback_rect_item.boundingRect())
            self.addItem(self.feedback_arrow)
            #self.feedback_arrow.setVisible(False)


            self.affine_fb_text = self.addText("")
            self.affine_fb_text.setPos(QPointF(float(posx + 2), float(posy + 2)))

            self.translate_fb_text = self.addText("")
            self.translate_fb_text.setPos(QPointF(float(translate_posx + 2), float(posy + 2)))



            self.draw_fb_config = True

        if klt_state.iteration_count == 0:
            self.feedback_arrow.setVisible(False)
            self.affine_fb_text.setPlainText("Initial Warp:\n\nAXX: %4.2f AXY: %4.2f\nAYX: %4.2f AYY: %4.2f" % (klt_state.current_axx, klt_state.current_axy, klt_state.current_ayx, klt_state.current_ayy))
            self.translate_fb_text.setPlainText("Initial Translation:\n\nDX: %6.2f\nDY: %6.2f" % (klt_state.current_dx, klt_state.current_dy))
            brush = QBrush(QColor("gray"))
            self.feedback_rect_item.setBrush(brush)

        else:
            self.feedback_arrow.setVisible(True)
            self.affine_fb_text.setPlainText("Warp:\n\nAXX: %4.2f AXY: %4.2f\nAYX: %4.2f AYY: %4.2f" % (klt_state.current_axx, klt_state.current_axy, klt_state.current_ayx, klt_state.current_ayy))
            self.translate_fb_text.setPlainText("Translation:\n\nDX: %6.2f\nDY: %6.2f" % (klt_state.current_dx, klt_state.current_dy))
            brush = None
            if klt_state.convergence:
                brush = QBrush(QColor("green"))
            else:
                brush = QBrush(QColor("white"))
            self.feedback_rect_item.setBrush(brush)

    def find_bounding_box(self, line_items):
        x_start = 0
        x_end = 0
        y_start = 0
        y_end = 0

        x_start = line_items[0].line().x1()
        y_start = line_items[0].line().y1()

        x_end = line_items[0].line().x2()
        y_end = line_items[0].line().y2()

        for line_item in line_items:
            #Set the top left
            if line_item.line().x1() < x_start:
                x_start = line_item.line().x1()
            if line_item.line().y1() < y_start:
                y_start = line_item.line().y1()

            if line_item.line().x2() < x_start:
                x_start = line_item.line().x2()
            if line_item.line().y2() < y_start:
                y_start = line_item.line().y2()

            #Set the bottom right
            if line_item.line().x1() > x_end:
                x_end = line_item.line().x1()
            if line_item.line().y1() > y_end:
                y_end = line_item.line().y1()

            if line_item.line().x2() > x_end:
                x_end = line_item.line().x2()
            if line_item.line().y2() > y_end:
                y_end = line_item.line().y2()

        return QRectF(x_start, y_start, x_end - x_start, y_end - y_start)

    def update(self, klt_state):
        scene_rect = self.sceneRect()

        image_width = len(klt_state.template_image[0])
        image_height = len(klt_state.template_image)
        divide_factor = IMAGE_SCALE_WIDTH / float(image_width)
        self.current_image_width = divide_factor * image_width
        self.current_image_height = divide_factor * image_height

        self.current_patch_width  = DRAW_PATCH_SIZE * klt_state.patch_width
        self.current_patch_height = DRAW_PATCH_SIZE * klt_state.patch_height

        print "Size: %d, %d" % (scene_rect.width(), scene_rect.height())
        print "Image width: %d" % self.current_image_width
        print "Image height: %d" % self.current_image_height
        print "Current Feature: %f, %f" % (klt_state.feature_pos[0], klt_state.feature_pos[1])

        self.draw_template_image(klt_state)
        self.draw_current_image(klt_state)
        self.draw_template_patch(klt_state)
        self.draw_current_patch(klt_state)
        self.draw_transform_patch(klt_state)
        self.draw_image_diff(klt_state)
        self.draw_reference_warp_box(klt_state)
        self.draw_affine_warp_box(klt_state)
        self.draw_feedback(klt_state)

        self.draw_annotations(klt_state)

        #Tell the Scene to redraw itself
        self.invalidate(self.sceneRect())

class VectorGraphicsScene(QGraphicsScene):
    def __init__(self):
        super (VectorGraphicsScene, self).__init__()
        self.setSceneRect(0, 0, 30, 30)
        self.color = Qt.black
        self.width = 2
        self.min_multiplier = 40
        self.multiplier = self.min_multiplier
        self.vpen = QPen(Qt.blue, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.brush = QBrush(QColor("gray"))
        self.pen = QPen(self.color, self.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.dx = 0.0
        self.dy = 0.0
        self.vlines = []
        self.hlines = []
        self.vector = None

    def draw_grid(self):
        scene_rect = self.sceneRect()
        start_x = int(scene_rect.left() + self.multiplier - (scene_rect.left()
            % self.multiplier))
        start_y = int(scene_rect.top() + self.multiplier - (scene_rect.top() %
            self.multiplier))


        for l in self.vlines:
            self.removeItem(l)

        for l in self.hlines:
            self.removeItem(l)

        self.vlines = []
        self.hlines = []

        for x in range(start_x, int(scene_rect.right()), self.multiplier):
            #print "X: %d, %d, %d" % (x, int(scene_rect.top()),
            #        int(scene_rect.bottom()))
            self.hlines.append(self.addLine(QLineF(  x, int(scene_rect.top()),
                                                     x, int(scene_rect.bottom()))))

        for y in range(start_y, int(scene_rect.bottom()), self.multiplier):
            self.vlines.append(self.addLine(QLineF( int(scene_rect.left()),  y,
                                                    int(scene_rect.right()), y)))

    def draw_vector(self):
        scene_rect = self.sceneRect()

        mult_width = 1
        mult_height = 1

        if scene_rect.width() > 0:
            mult_width = int(self.dx / scene_rect.width())
        if scene_rect.height() > 0:
            mult_height = int(self.dy / scene_rect.height())

        if mult_width == 0:
            mult_width = 1
        if mult_height == 0:
            mult_height = 1

        self.multiplier = int(mult_width * 1.50)
        if mult_height > mult_width:
            self.multiplier = int(mult_height * 1.50)

        if self.multiplier < self.min_multiplier:
            self.multiplier = self.min_multiplier

        x_mid = scene_rect.width() / 2
        y_mid = scene_rect.height() / 2

        #Scale the background relative to the size of the vector

        '''
        if self.dx > 0.0 or self.dy > 0.0:
            pass
        '''
        if self.vector is not None:
            self.removeItem(self.vector)

        if abs(self.dx) > 0.01 or abs(self.dy) > 0.01:
            print "Draw Vector!"
            self.vector = self.addLine(QLineF(  x_mid,
                                                y_mid,
                                                x_mid + self.dx * 1000.0,
                                                #x_mid + self.dx * self.multiplier,
                                                y_mid + self.dy * 1000.0),
                                                #y_mid + self.dy * self.multiplier),
                                        self.vpen)
            #Draw Vector

        else:
            self.vector = self.addEllipse(x_mid, y_mid, 5.0, 5.0, self.vpen, self.brush)
        


    def update(self, klt_state):
        self.dx = klt_state.x_offset
        self.dy = klt_state.y_offset
        self.draw_vector()
        self.draw_grid()
        self.invalidate(self.sceneRect())


class SidePane(QWidget):
    def __init__(self):
        super(SidePane, self).__init__()

        v_layout = QVBoxLayout()

        v_layout.addWidget(QLabel("Status"))
        self.vector_graphics_view = QGraphicsView(self)
        self.vector_graphics_scene = VectorGraphicsScene()
        self.vector_graphics_view.setScene(self.vector_graphics_scene)


        self.feature_index_label = QLabel("?? of ??")
        self.pyramid_level_label = QLabel("?? of ??")
        self.feature_status_label = QLabel("???")
        self.converged_label = QLabel("???")
        self.iteration_count_label = QLabel("???")
        self.dx_label = QLabel("???")
        self.dy_label = QLabel("???")

        self.axx_label = QLabel("???")
        self.axy_label = QLabel("???")
        self.ayx_label = QLabel("???")
        self.ayy_label = QLabel("???")

        self.dxx_err_label = QLabel("???")
        self.dyx_err_label = QLabel("???")
        self.dxy_err_label = QLabel("???")
        self.dyy_err_label = QLabel("???")
        self.dx_err_label  = QLabel("???")
        self.dy_err_label  = QLabel("???")

        self.dxx_err_thres_label = QLabel("???")
        self.dyx_err_thres_label = QLabel("???")
        self.dxy_err_thres_label = QLabel("???")
        self.dyy_err_thres_label = QLabel("???")
        self.dx_err_thres_label  = QLabel("???")
        self.dy_err_thres_label  = QLabel("???")

        #Setup the Layout
        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel("Feature"), 0, 0, 1 , 2)
        grid_layout.addWidget(self.feature_index_label, 0, 2, 1, 4)

        grid_layout.addWidget(QLabel("Pyramid"), 1, 0, 2, 2)
        grid_layout.addWidget(self.pyramid_level_label, 1, 2, 2, 4)

        #grid_layout.addWidget(QLabel("Feature Status"), 2, 0, 3, 2)
        #grid_layout.addWidget(self.feature_status_label, 2, 2, 3, 4)

        grid_layout.addWidget(QLabel("Converged"), 2, 0, 3, 2)
        grid_layout.addWidget(self.converged_label, 2, 2, 3, 4)

        grid_layout.addWidget(QLabel("Iteration"), 3, 0, 4, 2)
        grid_layout.addWidget(self.iteration_count_label, 3, 2, 4, 4)

        #grid_layout.addWidget(QLabel(""), 4, 0, 5, 4)
        #grid_layout.addWidget(QLabel(""), 5, 0, 6, 4)

        grid_layout.addWidget(QLabel("Transform"),   4,  0, 7, 4)

        #grid_layout.addWidget(QLabel(""),            7,  0, 8, 4)

        grid_layout.addWidget(QLabel("Translation"), 7,  0, 9, 4)

        grid_layout.addWidget(QLabel("DX"),          9,  0, 10, 2)
        grid_layout.addWidget(self.dx_label,         9,  2, 10, 4)
        grid_layout.addWidget(QLabel("DY"),          10, 0, 11, 2)
        grid_layout.addWidget(self.dy_label,         10, 2, 11, 4)

        #grid_layout.addWidget(QLabel(""),            11, 0, 12, 4)
        grid_layout.addWidget(QLabel("Warping"),     11, 0, 13, 4)

        grid_layout.addWidget(QLabel("AXX"),         13, 0, 14, 1)
        grid_layout.addWidget(self.axx_label,        13, 1, 14, 2)

        grid_layout.addWidget(QLabel("AXY"),         13, 2, 14, 3)
        grid_layout.addWidget(self.axy_label,        13, 3, 14, 4)

        grid_layout.addWidget(QLabel("AYX"),         15, 0, 16, 1)
        grid_layout.addWidget(self.ayx_label,        15, 1, 16, 2)

        grid_layout.addWidget(QLabel("AYY"),         15, 2, 16, 3)
        grid_layout.addWidget(self.ayy_label,        15, 3, 16, 4)


        #grid_layout.addWidget(QLabel(""),                  15, 0, 16, 4)
        #grid_layout.addWidget(QLabel(""),                  17, 0, 18, 4)
        #grid_layout.addWidget(QLabel(""),                  18, 0, 19, 4)
        grid_layout.addWidget(QLabel("Error"),             17, 0, 19, 3)
        grid_layout.addWidget(QLabel("Threshold"),         17, 3, 19, 4)

        grid_layout.addWidget(QLabel("dX*X"),               20, 0, 21, 1)
        grid_layout.addWidget(self.dxx_err_label,           20, 1, 21, 3)
        grid_layout.addWidget(self.dxx_err_thres_label,     20, 3, 21, 4)

        grid_layout.addWidget(QLabel("dY*X"),               21, 0, 22, 1)
        grid_layout.addWidget(self.dyx_err_label,           21, 1, 22, 3)
        grid_layout.addWidget(self.dyx_err_thres_label,     21, 3, 22, 4)

        grid_layout.addWidget(QLabel("dX*Y"),               22, 0, 23, 1)
        grid_layout.addWidget(self.dxy_err_label,           22, 1, 23, 3)
        grid_layout.addWidget(self.dxy_err_thres_label,     22, 3, 23, 4)

        grid_layout.addWidget(QLabel("dY*Y"),               23, 0, 24, 1)
        grid_layout.addWidget(self.dyy_err_label,           23, 1, 24, 3)
        grid_layout.addWidget(self.dyy_err_thres_label,     23, 3, 24, 4)

        grid_layout.addWidget(QLabel("dX"),                 24, 0, 25, 1)
        grid_layout.addWidget(self.dx_err_label,            24, 1, 25, 3)
        grid_layout.addWidget(self.dx_err_thres_label,      24, 3, 25, 4)

        grid_layout.addWidget(QLabel("dY"),                 25, 0, 26, 1)
        grid_layout.addWidget(self.dy_err_label,            25, 1, 26, 3)
        grid_layout.addWidget(self.dy_err_thres_label,      25, 3, 26, 4)


        grid_layout.setColumnMinimumWidth(0, 40)
        grid_layout.setColumnMinimumWidth(1, 40)
        grid_layout.setColumnMinimumWidth(2, 40)
        grid_layout.setColumnMinimumWidth(3, 40)

        v_layout.addLayout(grid_layout, 1)
        v_layout.addWidget(self.vector_graphics_view, 1)

        #self.setLayout(grid_layout)
        self.setLayout(v_layout)

    def update(self, klt_state):
        self.feature_index_label.setText(str(klt_state.feature_index))
        self.pyramid_level_label.setText(str(klt_state.pyramid_pos))
        self.feature_status_label.setText("")
        if klt_state.convergence:
            self.converged_label.setText("Converged!")
            self.converged_label.setStyleSheet("QLabel { background-color : green }")
        else:
            self.converged_label.setText("Not Converged")
            self.converged_label.setStyleSheet("QLabel { background-color : red }")
        self.iteration_count_label.setText(str(klt_state.iteration_count))
        self.dx_label.setText("%.2f" % klt_state.dx)
        self.dy_label.setText("%.2f" % klt_state.dy)

        self.axx_label.setText("%.2f" % klt_state.axx)
        self.axy_label.setText("%.2f" % klt_state.axy)
        self.ayx_label.setText("%.2f" % klt_state.ayx)
        self.ayy_label.setText("%.2f" % klt_state.ayy)

        self.update_error_entries(klt_state)

        self.dxx_err_thres_label.setText("%.2f" % klt_state.error_dxx_thresh)
        self.dyx_err_thres_label.setText("%.2f" % klt_state.error_dyx_thresh)
        self.dxy_err_thres_label.setText("%.2f" % klt_state.error_dxy_thresh)
        self.dyy_err_thres_label.setText("%.2f" % klt_state.error_dyy_thresh)
        self.dx_err_thres_label.setText("%.2f" % klt_state.error_dx_thresh)
        self.dy_err_thres_label.setText("%.2f" % klt_state.error_dy_thresh)

        s = QSizeF(self.vector_graphics_view.size())
        sr = QRectF(QPointF(0,0), s)
        self.vector_graphics_scene.setSceneRect(sr)
        self.vector_graphics_scene.update(klt_state)


    def update_error_entries(self, klt_state):
        self.dxx_err_label.setText("%.2f" % klt_state.error_dxx)
        self.dyx_err_label.setText("%.2f" % klt_state.error_dyx)
        self.dxy_err_label.setText("%.2f" % klt_state.error_dxy)
        self.dyy_err_label.setText("%.2f" % klt_state.error_dyy)
        self.dx_err_label.setText("%.2f" % klt_state.error_dx)
        self.dy_err_label.setText("%.2f" % klt_state.error_dy)

        '''
        if abs(klt_state.error_dxx) < klt_state.error_dxx_thresh:
            self.dxx_err_label.setStyleSheet("QLabel { background-color : green }")
        else:
            self.dxx_err_label.setStyleSheet("QLabel { background-color : red }")

        if abs(klt_state.error_dxy) < klt_state.error_dxy_thresh:
            self.dxy_err_label.setStyleSheet("QLabel { background-color : green }")
        else:
            self.dxy_err_label.setStyleSheet("QLabel { background-color : red }")

        if abs(klt_state.error_dyx) < klt_state.error_dyx_thresh:
            self.dyx_err_label.setStyleSheet("QLabel { background-color : green }")
        else:
            self.dyx_err_label.setStyleSheet("QLabel { background-color : red }")

        if abs(klt_state.error_dyy) < klt_state.error_dyy_thresh:
            self.dyy_err_label.setStyleSheet("QLabel { background-color : green }")
        else:
            self.dyy_err_label.setStyleSheet("QLabel { background-color : red }")

        if abs(klt_state.error_dx) < klt_state.error_dx_thresh:
            self.dx_err_label.setStyleSheet("QLabel { background-color : green }")
        else:
            self.dx_err_label.setStyleSheet("QLabel { background-color : red }")

        if abs(klt_state.error_dy) < klt_state.error_dy_thresh:
            self.dy_err_label.setStyleSheet("QLabel { background-color : green }")
        else:
            self.dy_err_label.setStyleSheet("QLabel { background-color : red }")
        '''


class KLTGUI(QWidget):

    new_frame_signal = pyqtSignal([object])

    def update_step_select(self):
        if self.radio_step_none.isChecked():
            self.log.debug("Disable Stepping")
            self.klt.set_step_none()
            return
        elif self.radio_step_feature.isChecked():
            self.log.debug("Set Feature Stepping")
            self.klt.set_step_feature()
            return
        elif self.radio_step_pyramid.isChecked():
            self.log.debug("Set Pyramid Stepping")
            self.klt.set_step_pyramid()
            return
        elif self.radio_step_iter.isChecked():
            self.log.debug("Set Iteration Stepping")
            self.klt.set_step_iteration()
            return
        raise IndexError("Unknow Step Select!")

    @pyqtSlot(object)
    def update_cb(self, klt_state):
        self.scene.update(klt_state)
        self.side_pane.update(klt_state)

    def __init__(self, video = VIDEO_FILE, pyramid_depth = PYRAMID_DEPTH, debug = False):
        super(KLTGUI, self).__init__()
        self.resize(GUI_WIDTH, GUI_HEIGHT)
        self.setWindowTitle(TITLE)
        self.state = STATE_GO
        #self.state = STATE_STOP

        #Add Logger
        self.log = logging.getLogger("klt")
        self.log.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)
        ch.setLevel(logging.INFO)

        # add ch to logger
        self.log.addHandler(ch)
        self.log.info("Started")
        if debug:
            self.log.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)

        self.klt = KLT( pyramid_depth = pyramid_depth,
                        debug = debug)

        self.klt_worker = KLTWorker()
        self.thread = QThread()
        self.thread.start()
        self.klt_worker.moveToThread(self.thread)
        self.klt_worker.update_object.connect(self.update_cb)
        self.graphics_view = QGraphicsView(self)
        self.scene = Scene()
        self.graphics_view.setScene(self.scene)

        QMetaObject.invokeMethod(self.klt_worker,
                                "thread_init",
                                Qt.QueuedConnection,
                                Q_ARG(object, self.klt),
                                Q_ARG(object, self.new_frame_signal))


        self.cap = cv2.VideoCapture(video)
        fps = self.cap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.log.debug("FPS: %s" % str(fps))
        if fps < 0.1:
            fps = 30.0

        #Setup Timer callback
        self.timer = QTimer()
        self.timer.timeout.connect(self.new_frame)
        #self.timer.start(1000.0/30)
        self.timer.start(1000.0/fps)

        #Setup the GUI
        self.side_pane = SidePane()

        #Make buttons
        self.step_button = QPushButton("Step")
        self.step_button.clicked.connect(self.step_button_clicked)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_button_clicked)

        self.radio_step_none = QRadioButton("No Step")
        self.radio_step_feature = QRadioButton("Feature")
        self.radio_step_pyramid = QRadioButton("Pyramid")
        self.radio_step_iter = QRadioButton("Iteration")

        self.radio_step_none.toggled.connect(self.update_step_select)
        self.radio_step_iter.toggled.connect(self.update_step_select)
        self.radio_step_pyramid.toggled.connect(self.update_step_select)
        self.radio_step_feature.toggled.connect(self.update_step_select)

        self.radio_step_iter.setChecked(True)
        #self.radio_step_none.setChecked(True)

        '''
        self.radio_step_none.toggled.connect(lambda:self.step_type_select(self.radio_step_none))
        self.radio_step_feature.toggled.connect(lambda:self.step_type_select(self.radio_step_feature))
        self.radio_step_iter.toggled.connect(lambda:self.step_type_select(self.radio_step_iter))
        '''

        # Step Layout
        step_layout = QHBoxLayout()
        step_layout.addWidget(self.radio_step_none)
        step_layout.addWidget(self.radio_step_feature)
        step_layout.addWidget(self.radio_step_pyramid)
        step_layout.addWidget(self.radio_step_iter)
        step_layout.addWidget(self.start_button)

        system_layout = QHBoxLayout()
        system_layout.addWidget(self.graphics_view)
        system_layout.addWidget(self.side_pane)

        #Add everything to the Layouts
        main_layout = QVBoxLayout()

        #XXX: Why isn't the arrows displaying when inside the new layout??
        #main_layout.addWidget(self.graphics_view)
        main_layout.addLayout(system_layout)
        main_layout.addLayout(step_layout)
        main_layout.addWidget(self.step_button)

        #Set the gui's layout
        self.setLayout(main_layout)
        #Show the layout
        self.show()

    def step_button_clicked(self):
        print("")
        print("Step")
        print("")
        self.klt_worker.continue_step()

    def start_button_clicked(self):
        self.log.debug("Start Clicked!")

    def new_frame(self):
        if self.state == STATE_GO:
            if self.klt_worker.is_ready():
                ret, image = self.cap.read()
                if ret:
                    self.log.debug("Track...")
                    #self.klt.track(image):
                    self.new_frame_signal.emit(image)


def main(argv):

    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )
    pyramid_depth = str(PYRAMID_DEPTH)

    parser.add_argument("-v", "--video",
                        nargs=1,
                        default=[VIDEO_FILE])

    parser.add_argument("-p", "--pyramid",
                        nargs=1,
                        default=[pyramid_depth])

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")


    args = parser.parse_args()
    video_path = None
    pyramid_depth = int(args.pyramid[0])
    if args.video is not None:
        video_path = args.video[0]

    app = QApplication(sys.argv)
    gui = KLTGUI(video = video_path, pyramid_depth = pyramid_depth, debug = args.debug)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv)


