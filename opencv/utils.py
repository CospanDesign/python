import math

from PyQt4 import QtCore, QtGui
import numpy as np


class Arrow(QtGui.QGraphicsLineItem):

    def __init__(self, start_item, end_item, parent=None, scene=None):
        super(Arrow, self).__init__(parent, scene)
        self.arrowHead = QtGui.QPolygonF()

        self.start_item = start_item
        self.end_item = end_item
        #self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.myColor = QtCore.Qt.black
        self.setPen(QtGui.QPen(self.myColor, 2, QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

        self.start_box = None
        self.end_box = None

        try:
            self.start_box = start_item.boundingRect()
            self.start_box.moveTo(start_item.x(), start_item.y())
            '''
            print ("Start Box: X: %f Y: %f Width: %f Height: %f" % (self.start_box.x(),
                                                                    self.start_box.y(),
                                                                    self.start_box.width(),
                                                                    self.start_box.height()))
            '''
        except AttributeError:
            pass

        try:
            self.end_box = end_item.boundingRect()
            self.end_box.moveTo(end_item.x(), end_item.y())
            '''
            print ("End Box: X: %f Y: %f Width: %f Height: %f" %   (self.end_box.x(),
                                                                    self.end_box.y(),
                                                                    self.end_box.width(),
                                                                    self.end_box.height()))
            '''
        except AttributeError:
            pass

    def setColor(self, color):
        self.myColor = color

    def start_item(self):
        return self.start_item

    def end_item(self):
        return self.end_item

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        r = QtCore.QRectF(p1, QtCore.QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)
        if (r.x() < 0 or r.y() < 0):
            start_center = self.start_box.center()
            end_center = self.end_box.center()
            center_line = QtCore.QLineF(end_center, start_center)
            p1 = center_line.p1()
            p2 = center_line.p2()

        r = QtCore.QRectF(p1, QtCore.QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)


        #print "Bounding rect: %s" % str(r)
        return r

    def set_start_box(self, box):
        self.start_box = box

    def set_end_box(self, box):
        self.end_box = box
        '''
        print ("End Box: X: %f Y: %f Width: %f Height: %f" %   (self.end_box.x(),
                                                                self.end_box.y(),
                                                                self.end_box.width(),
                                                                self.end_box.height()))
        '''

    def shape(self):
        path = super(Arrow, self).shape()
        path.addPolygon(self.arrowHead)
        return path

    def updatePosition(self):
        line = QtCore.QLineF(self.mapFromItem(self.start_item, 0, 0), self.mapFromItem(self.end_item, 0, 0))
        #line = QtCore.QLineF(self.start_item.center(), self.end_item.center())
        self.setLine(line)

    def paint(self, painter, option, widget=None):
        if (self.start_box.intersects(self.end_box)):
            #print "Boxes Collide!"
            return

        myColor = self.myColor
        myPen = self.pen()
        myPen.setColor(self.myColor)
        arrowSize = 20.0
        painter.setPen(myPen)
        painter.setBrush(self.myColor)


        start_center = self.start_box.center()
        end_center = self.end_box.center()

        start_top_left = self.start_box.topLeft()
        end_top_left = self.end_box.topLeft()

        start_point = start_center
        end_point = end_center
        center_line = QtCore.QLineF(end_center, start_center)

        start_polygon   = QtGui.QPolygonF(self.start_box)
        end_polygon     = QtGui.QPolygonF(self.end_box)

        intersection_point = QtCore.QPointF()

        p1 = end_polygon.last()
        for i in start_polygon:
            p2 = i
            line = QtCore.QLineF(p1, p2)
            #Check if there is an intersection point
            intersection_type = line.intersect(center_line, intersection_point)
            if intersection_type == QtCore.QLineF.BoundedIntersection:
                break
            p1 = p2

        #center_line = QtCore.QLineF(end_center, intersection_point)
        start_point = intersection_point

        #Find Intersection with the end box
        intersection_point = QtCore.QPointF()
        p1 = end_polygon.last()
        for i in end_polygon:
            p2 = i
            line = QtCore.QLineF(p1, p2)
            #Check if there is an intersection point
            intersection_type = line.intersect(center_line, intersection_point)
            if intersection_type == QtCore.QLineF.BoundedIntersection:
                break
            p1 = p2

        end_point = intersection_point
        center_line = QtCore.QLineF(end_point, start_point)

        self.setLine(center_line)
        line = self.line()


        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = (math.pi * 2.0) - angle

        arrowP1 = line.p1() + QtCore.QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi / 3) * arrowSize)
        arrowP2 = line.p1() + QtCore.QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)

        self.arrowHead.clear()
        for point in [line.p1(), arrowP1, arrowP2]:
            self.arrowHead.append(point)

        painter.drawLine(line)
        painter.drawPolygon(self.arrowHead)
        if self.isSelected():
            painter.setPen(QtGui.QPen(myColor, 1, QtCore.Qt.DashLine))
            myLine = QtCore.QLineF(line)
            myLine.translate(0, 4.0)
            painter.drawLine(myLine)
            myLine.translate(0,-8.0)
            painter.drawLine(myLine)


def get_simple_patch(image, x, y, patch_size):
    hw = patch_size / 2
    hh = patch_size / 2
    patch = np.zeros(shape = (patch_size, patch_size), dtype=np.float32)
    for j in range(-hh, hh + 1):
        for i in range(-hw, hw + 1):
            py = j + hh
            px = i + hw

            patch[py][px] = image[int(y + j)][int(x + i)]

    return patch

def get_image_transform(image, x, y, axx, ayx, axy, ayy, patch_size):
    hw = patch_size / 2
    hh = patch_size / 2
    patch = np.zeros(shape = (patch_size, patch_size), dtype=np.float32)
    for j in range(-hh, hh + 1):
        for i in range(-hw, hw + 1):
            py = j + hh
            px = i + hw
            mi = axx * i + axy * j
            mj = ayx * i + ayy * j
            patch[py][px] = interpolate(x + mi, y + mj, image)

    return patch



def interpolate(x, y, image):
    xt = int(x)
    yt = int(y)
    ax = float(x) - float(xt)
    ay = float(y) - float(yt)

    if xt < 0:
        raise Exception("xt < 0 xt: %d" % xt)
    if yt < 0:
        raise Exception("yt < 0 yt: %d" % yt)

    if xt > image.shape[1] - 2:
        raise Exception("xt > width - 2 xt: %d width - 2" % (xt, (image.shape[1] - 2)))

    if yt > image.shape[0] - 2:
        raise Exception("yt > height - 2 xt: %d height - 2" % (yt, (image.shape[0] - 2)))

    pixel = 0

    pixel += (1 - ax) * (1 - ay) * image[yt    ][xt    ]
    pixel += (    ax) * (1 - ay) * image[yt    ][xt + 1]

    pixel += (1 - ax) * (    ay) * image[yt    ][xt    ]
    pixel += (    ax) * (    ay) * image[yt + 1][xt    ]
    return pixel

def scale_patch(patch, size):
    out_patch = np.zeros(shape=(size, size), dtype=np.float32)
    scale = int(float(size) / float(patch.shape[0]))
    for j in range(patch.shape[0]):
        for i in range (patch.shape[1]):
            for k in range(j, j + scale):
                for l in range(i, i + scale):
                    out_patch[k][l] = patch[j][i]

    return out_patch
