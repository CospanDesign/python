#! /usr/bin/python

import sys
import time

from PyQt4 import QtCore
from PyQt4 import QtGui

class WorkThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        for i in range (6):
            print ".",
            time.sleep(0.3)
            self.emit(QtCore.SIGNAL("Update(QString)"), "from worker thread " + str(i))
        return

class MyApp(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(300, 300, 280, 600)
        self.setWindowTitle("Threads")

        self.layout=  QtGui.QVBoxLayout(self)

        self.testButton = QtGui.QPushButton("test")
        self.connect(self.testButton, QtCore.SIGNAL("released()"), self.test)
        self.listwidget = QtGui.QListWidget(self)

        self.layout.addWidget(self.testButton)
        self.layout.addWidget(self.listwidget)

    def add(self, text):
        """ Add item to list widget """
        print "Add: %s" % text
        self.listwidget.addItem(text)
        self.listwidget.sortItems()

    def addBatch(self, text="test", iters=6, delay=0.3):
        """Add several items to the list widget"""
        for i in range (iters):
            #Artificial delay
            time.sleep(delay)
            self.add(text + " " + str(i))

    def test(self):
        self.listwidget.clear()
        self.addBatch("_non_thread", iters=6, delay=0.3)
        self.workThread = WorkThread()
        self.connect(self.workThread, QtCore.SIGNAL("Update(QString)"), self.add)
        self.workThread.start()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    test = MyApp()
    test.show()
    app.exec_()
