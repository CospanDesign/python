#!/usr/bin/python

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

class Connection:
  """
  - fromPort
  - toPort
  """
  def __init__(self, fromPort, toPort):
    self.fromPort = fromPort
    self.pos1 = None
    self.pos2 = None
    if fromPort:
      self.pos1 = fromPort.scenePos()
      fromPort.posCallbacks.append(self.setBeginPos)

    self.toPort = toPort
    # Create arrow item:
    self.arrow = ArrowItem()
    editor.diagramScene.addItem(self.arrow)

  def setFromPort(self, fromPort):
    self.fromPort = fromPort
    if self.fromPort:
      self.pos1 = fromPort.scenePos()
      self.fromPort.posCallbacks.append(self.setBeginPos)

  def setToPort(self, toPort):
    self.toPort = toPort
    if self.toPort:
      self.pos2 = toPort.scenePos()
      self.toPort.posCallbacks.append(self.setEndPos)

  def setEndPos(self, endpos):
    self.pos2 = endpos
    self.arrow.setLine(QLineF(self.pos1, self.pos2))

  def setBeginPos(self, pos1):
    self.pos1 = pos1
    self.arrow.setLine(QLineF(self.pos1, self.pos2))

  def delete(self):
    editor.diagramScene.removeItem(self.arrow)
    # Remove position update callbacks:

class ParameterDialog(QDialog):
  def __init__(self, parent=None):
    super(ParameterDialog, self).__init__(parent)
    self.button = QPushButton('Ok', self)
    l = QVBoxLayout(self)
    l.addWidget(self.button)
    self.button.clicked.connect(self.OK)

  def OK(self):
    self.close()

class PortItem(QGraphicsEllipseItem):
  """ Represents a port to a subsystem """
  def __init__(self, name, parent=None):
    QGraphicsEllipseItem.__init__(self, QRectF(-6,-6,12.0,12.0), parent)
    self.setCursor(QCursor(QtCore.Qt.CrossCursor))
#   Properties:
    self.setBrush(QBrush(Qt.red))
#   Name:
    self.name = name
    self.posCallbacks = []
    self.setFlag(self.ItemSendsScenePositionChanges, True)

  def itemChange(self, change, value):
    if change == self.ItemScenePositionHasChanged:
      for cb in self.posCallbacks:
        cb(value)
      return value
    return super(PortItem, self).itemChange(change, value)

  def mousePressEvent(self, event):
    editor.startConnection(self)

# Block part:
class HandleItem(QGraphicsEllipseItem):
  """ A handle that can be moved by the mouse """
  def __init__(self, parent=None):
    super(HandleItem, self).__init__(QRectF(-4.0,-4.0,8.0,8.0), parent)
    self.posChangeCallbacks = []
    self.setBrush(QtGui.QBrush(Qt.white))
    self.setFlag(self.ItemIsMovable, True)
    self.setFlag(self.ItemSendsScenePositionChanges, True)
    self.setCursor(QtGui.QCursor(Qt.SizeFDiagCursor))

  def itemChange(self, change, value):
    if change == self.ItemPositionChange:
      x, y = value.x(), value.y()

      # TODO: make this a signal?
      # This cannot be a signal because this is not a QObject
      for cb in self.posChangeCallbacks:
        res = cb(x, y)
        if res:
          x, y = res
          value = QPointF(x, y)
      return value
    # Call superclass method:
    return super(HandleItem, self).itemChange(change, value)

class BlockItem(QGraphicsRectItem):
  """
  Represents a block in the diagram
  Has an x and y and width and height
  width and height can only be adjusted with a tip in the lower right corner.

  - in and output ports
  - parameters
  - description
  """
  def __init__(self, name='Untitled', parent=None):
    super(BlockItem, self).__init__(parent)
    w = 60.0
    h = 40.0
    # Properties of the rectangle:
    self.setPen(QtGui.QPen(QtCore.Qt.blue, 2))
    self.setBrush(QtGui.QBrush(QtCore.Qt.lightGray))
    self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
    self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    # Label:
    self.label = QGraphicsTextItem(name, self)
    # Create corner for resize:
    self.sizer = HandleItem(self)
    self.sizer.setPos(w, h)
    self.sizer.posChangeCallbacks.append(self.changeSize) # Connect the callback
    #self.sizer.setVisible(False)
    self.sizer.setFlag(self.sizer.ItemIsSelectable, True)

    # Inputs and outputs of the block:
    self.inputs = []
    self.inputs.append( PortItem('a', self) )
    self.inputs.append( PortItem('b', self) )
    self.inputs.append( PortItem('c', self) )
    self.outputs = []
    self.outputs.append( PortItem('y', self) )
    #   Update size:
    self.changeSize(w, h)

  def editParameters(self):
    pd = ParameterDialog(self.window())
    pd.exec_()

  def contextMenuEvent(self, event):
    menu = QMenu()
    menu.addAction('Delete')
    pa = menu.addAction('Parameters')
    pa.triggered.connect(self.editParameters)
    menu.exec_(event.screenPos())

  def changeSize(self, w, h):
    """ Resize block function """
    # Limit the block size:
    if h < 20:
      h = 20
    if w < 40:
      w = 40
    self.setRect(0.0, 0.0, w, h)
    # center label:
    rect = self.label.boundingRect()
    lw, lh = rect.width(), rect.height()
    lx = (w - lw) / 2
    ly = (h - lh) / 2
    self.label.setPos(lx, ly)
    # Update port positions:
    if len(self.inputs) == 1:
      self.inputs[0].setPos(-4, h / 2)
    elif len(self.inputs) > 1:
      y = 5
      dy = (h - 10) / (len(self.inputs) - 1)
      for inp in self.inputs:
        inp.setPos(-4, y)
        y += dy

    if len(self.outputs) == 1:
      self.outputs[0].setPos(w+4, h / 2)

    elif len(self.outputs) > 1:
      y = 5
      dy = (h - 10) / (len(self.outputs) + 0)
      for outp in self.outputs:
        outp.setPos(w+4, y)
        y += dy

    return w, h

class ArrowItem(QGraphicsLineItem):
  def __init__(self):
    super(ArrowItem, self).__init__(None)
    self.setPen(QtGui.QPen(QtCore.Qt.red,2))
    self.setFlag(self.ItemIsSelectable, True)

  def x(self):
    pass

class EditorGraphicsView(QGraphicsView):
  def __init__(self, scene, parent=None):
    QGraphicsView.__init__(self, scene, parent)

  def dragEnterEvent(self, event):
    if event.mimeData().hasFormat('component/name'):
      event.accept()

  def dragMoveEvent(self, event):
    if event.mimeData().hasFormat('component/name'):
      event.accept()

  def dropEvent(self, event):
    if event.mimeData().hasFormat('component/name'):
      name = str(event.mimeData().data('component/name'))
      b1 = BlockItem(name)
      b1.setPos(self.mapToScene(event.pos()))
      self.scene().addItem(b1)

class LibraryModel(QStandardItemModel):

  def __init__(self, parent=None):
    QStandardItemModel.__init__(self, parent)

  def mimeTypes(self):
    return ['component/name']

  def mimeData(self, idxs):
    mimedata = QMimeData()
    for idx in idxs:
      if idx.isValid():
        txt = self.data(idx, Qt.DisplayRole)
        mimedata.setData('component/name', txt)

    return mimedata

class DiagramScene(QGraphicsScene):

  def __init__(self, parent=None):
    super(DiagramScene, self).__init__(parent)

  def mouseMoveEvent(self, mouseEvent):
    editor.sceneMouseMoveEvent(mouseEvent)
    super(DiagramScene, self).mouseMoveEvent(mouseEvent)

  def mouseReleaseEvent(self, mouseEvent):
    editor.sceneMouseReleaseEvent(mouseEvent)
    super(DiagramScene, self).mouseReleaseEvent(mouseEvent)

class DiagramEditor(QWidget):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.setWindowTitle("Diagram editor")

    # Widget layout and child widgets:
    self.horizontalLayout = QtGui.QHBoxLayout(self)
    self.libraryBrowserView = QtGui.QListView(self)
    self.libraryModel = LibraryModel(self)
    self.libraryModel.setColumnCount(1)
    # Create an icon with an icon:
    pixmap = QPixmap(60, 60)
    pixmap.fill()
    painter = QPainter(pixmap)
    painter.fillRect(10, 10, 40, 40, Qt.blue)
    painter.setBrush(Qt.red)
    painter.drawEllipse(36, 2, 20, 20)
    painter.setBrush(Qt.yellow)
    painter.drawEllipse(20, 20, 20, 20)
    painter.end()

    self.libItems = []
    self.libItems.append( QtGui.QStandardItem(QIcon(pixmap), 'Block') )
    self.libItems.append( QtGui.QStandardItem(QIcon(pixmap), 'Uber Unit') )
    self.libItems.append( QtGui.QStandardItem(QIcon(pixmap), 'Device') )
    for i in self.libItems:
      self.libraryModel.appendRow(i)

    self.libraryBrowserView.setModel(self.libraryModel)
    self.libraryBrowserView.setViewMode(self.libraryBrowserView.IconMode)
    self.libraryBrowserView.setDragDropMode(self.libraryBrowserView.DragOnly)

    self.diagramScene = DiagramScene(self)
    self.diagramView = EditorGraphicsView(self.diagramScene, self)
    self.horizontalLayout.addWidget(self.libraryBrowserView)
    self.horizontalLayout.addWidget(self.diagramView)

    # Populate the diagram scene:
    b1 = BlockItem('SubSystem1')
    b1.setPos(50,100)
    self.diagramScene.addItem(b1)
    b2 = BlockItem('Unit2')
    b2.setPos(-250,0)
    self.diagramScene.addItem(b2)

    self.startedConnection = None

  def startConnection(self, port):
    self.startedConnection = Connection(port, None)

  def sceneMouseMoveEvent(self, event):
    if self.startedConnection:
      pos = event.scenePos()
      self.startedConnection.setEndPos(pos)

  def sceneMouseReleaseEvent(self, event):
    # Clear the actual connection:
    if self.startedConnection:
      pos = event.scenePos()
      items = self.diagramScene.items(pos)
      for item in items:
        if type(item) is PortItem:
          self.startedConnection.setToPort(item)
      if self.startedConnection.toPort == None:
        self.startedConnection.delete()
    self.startedConnection = None

if __name__ == '__main__':
  app = QtGui.QApplication(sys.argv)
  global editor
  editor = DiagramEditor()
  editor.show()
  editor.resize(700, 800)
  app.exec_()
