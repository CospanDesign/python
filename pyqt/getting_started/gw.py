#! /usr/bin/python

import os
import sys
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4.QtGui import *

class MainView(QGraphicsView):

  def __init__(self):
    QGraphicsView.__init__(self)
    self.scene = QGraphicsScene(self)
    #self.setAcceptDrops(True)
#XXX: Maybe I shouldn't have widgets, maybe this is redundant (Let the scene manage them)
    self.widgets = []
    self.widgets.append(GraphicsWidget ('widget', 0, 0, 100, 50))

    self.scene.addItem(self.widgets[0])
    self.setScene(self.scene)

  def scale_view(self, scaleFactor):
    if scaleFactor == 1.2:
      print "Larger"
    if scaleFactor == 1/1.2:
      print "Smaller"

    factor = self.transform().scale(
      scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()

    if factor > 0.05 and factor < 15:
      self.scale(scaleFactor, scaleFactor)

  def increment_color(self):
    print "Color: %d %d %d %d" % (self.widgets[0].color.getRgb())
    r = 0
    g = 0
    b = 0
    a = 0
    r, g, b, a = self.widgets[0].color.getRgb()
    self.widgets[0].color.fromRgb (r, g, b + 5)
    self.widgets[0].color.setBlue(b + 5)

  def decrement_color(self):
    print "Color: %d %d %d %d" % (self.widgets[0].color.getRgb())
    r = 0
    g = 0
    b = 0
    a = 0
    r, g, b, a = self.widgets[0].color.getRgb()
    self.widgets[0].color.setBlue(b - 5)


  def keyPressEvent(self, event):
    taskList = {
      Qt.Key_Plus:  lambda: self.scale_view(1.2),
      Qt.Key_Minus: lambda: self.scale_view(1 / 1.2),
      Qt.Key_Up:    lambda: self.increment_color(),
      Qt.Key_Down:  lambda: self.decrement_color()}

    if(event.key() in taskList):
      taskList[event.key()]()
    else:
      QWidget.keyPressEvent(self, event)


#  def mousePressEvent(self, event):
#    if event.button() == QtCore.QtLeftButton:
#      print "Canvas: Mouse on canvas"
#
#  def mouseMoveEvent(self, event):
#    print "Canvas: Mouse Move Event"
#    return
#    
#  def mouseReleaseEvent(self, event):
#    print "Canvas: Mouse Release Event"
#    return

class GraphicsWidget(QGraphicsWidget):

  def __init__(self, name, x, y, width, height, color = 'orange'):
    QGraphicsWidget.__init__(self)
    self.type = "Test"
    self.setAcceptHoverEvents(True)
    self.name = name
    #self.resize(width, height)
    self.dragging = False
    self.x = x
    self.y = y
    self.width = width
    self.height = height

    self.color = QColor(color)
    self.setGeometry(self.x, self.y, self.width, self.height)


    self.text_font = QFont('White Rabbit')
    #self.text_font = QFont('Helvetica')
    self.text_font.setPointSize(16)

    #self.addItem(self.dave_text)
    #layout = QGraphicsLinearLayout()
    #layout.addItem(self.dave_text)
    #self.setLayout(layout)
    self.setToolTip(
      "Type: %s Name: %s" % (self.type, self.name)
    )
    #self.setAcceptDrops(True)


  def set_position(self, x, y):
    self.x = x
    self.y = y
    self.setGeometry(self.x, self.y, self.width, self.height)
    
  def set_size(self, width, height):
    self.width = width
    self.height = height
    self.setGeometry(self.x, self.y, self.width, self.height)

  def hoverEnterEvent(self, event):
    self.__printGeometryDetails()

  #Drag and drop start
  def mousePressEvent(self, event):
    if event.button() == QtCore.Qt.LeftButton:

      #left mouse button
      self.setCursor(Qt.ClosedHandCursor)
      self.dragging = True
    elif event.button() == QtRightButton:
      #Right mouse button
      print "Right mouse button clicked"
    else:
      #forget the rest
      event.ignore()

  def mouseMoveEvent(self, event):
    if QLineF(  QPointF(event.screenPos()), 
                QPointF(event.buttonDownScreenPos(QtCore.Qt.LeftButton))).length() < QApplication.startDragDistance():
      return

    print "Moving"
    drag = QDrag(event.widget())
    mime = QMimeData()
    drag.setMimeData(mime)
    mime.setColorData(self.color)
    mime.setText("moving!!")
    pixmap = QPixmap(self.rect().width(), self.rect().height())
    pixmap.fill(QtCore.Qt.white)
    painter = QPainter(pixmap)
    painter.translate(1, 1)
    painter.setRenderHint(QPainter.Antialiasing)
    self.paint(painter, None, None)
    painter.end()
    pixmap.setMask(pixmap.createHeuristicMask())
    drag.setPixmap(pixmap)

    #What does a hot spot do? (It's where the grab is located (here is the center)
    drag.setHotSpot(QPoint(self.rect().width()/2, self.rect().height()/2))
    drag.exec_()
    self.setCursor(Qt.OpenHandCursor)

  def mouseReleaseEvent(self, event):
    print "Release"
    self.dragging = False
    self.setCursor(Qt.OpenHandCursor)

  #def boundingRect(self):
  #  return QtCore.QRectF(self.x, self.y, self.width, self.height)

  def paint(self, painter, option, widget):
    bgRect = self.boundingRect()
    painter.drawRects(bgRect)
    painter.fillRect(bgRect, self.color)
    #painter.drawText(0, 0, 100, 100, 0x24, QString("Hello"))
    
    painter.setFont(self.text_font)
    painter.drawText(0, 0, 100, 100, 0x24, QString(self.name))

  def __printGeometryDetails(self):
    print self.name
    print '\tpos (%.0f, %0.0f)' % (self.pos().x(), self.pos().y())
    print '\tboundingRect (%.0f, %0.0f, %.0f, %0.0f)' % (self.boundingRect().x(), self.boundingRect().y(), self.boundingRect().width(), self.boundingRect().height())
    print '\tgeometry (%.0f, %0.0f, %.0f, %0.0f)' % (self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height())
    print '\trect (%.0f, %0.0f, %.0f, %0.0f)' % (self.rect().x(), self.rect().y(), self.rect().width(), self.rect().height())

if __name__ == '__main__':
  app = QApplication(sys.argv)
  view = MainView()
  view.setGeometry(600, 100, 400, 370)
  view.show()
  sys.exit(app.exec_())
