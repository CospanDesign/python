#! /usr/bin/python

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import *



@QtCore.pyqtSlot(str)
def directory_changed(path):
    print('Directory %s Changed!!!' % path)

@QtCore.pyqtSlot(str)
def file_changed(path):
    print('File %s Changed!!!' % path)

def main():
    app = QtGui.QApplication(sys.argv)
 
    w = QtGui.QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple')
    w.show()

    fsw = QtCore.QFileSystemWatcher(['/home/cospan/sandbox/ft.txt', '/home/cospan/sandbox'])
    fsw.connect(fsw, QtCore.SIGNAL('directoryChanged(QString)'), directory_changed)
    fsw.connect(fsw, QtCore.SIGNAL('fileChanged(QString)'), file_changed)

    sys.exit(app.exec_())

if __name__=="__main__":
    main()
