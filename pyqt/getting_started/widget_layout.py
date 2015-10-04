import os
import sys
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Example(QtGui.QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.init_ui()
 
    def init_ui(self):
        qbtn = QtGui.QPushButton('Quit', self)
        qbtn.clicked.connect(QtCore.QCoreApplication.instance().quit)
        qbtn.resize(qbtn.sizeHint())
 
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Quit Button')
        self.show()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    scene = QGraphicsScene()
    #text_edit = scene.addWidget(QLabel("Test"))
    #push_button = scene.addWidget(QPushButton("button"))

    #layout = QGraphicsGridLayout()
    #layout.addItem(text_edit, 0, 0)
    #layout.addItem(push_button, 0, 1)

    ex = Example()
    #form = QGraphicsWidget()
    #form.setLayout(layout)
    #scene.addItem(form)
    scene.addItem(ex)
    view = QGraphicsView(scene)
    view.show()
    sys.exit(app.exec_())

