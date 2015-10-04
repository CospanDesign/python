#!/usr/bin/python

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class Example(QtGui.QWidget):
  def __init__(self):
    super(Example, self).__init__()
    self.initUI()

  def initUI(self):
    qbtn = QtGui.QPushButton('Quit', self)
    qbtn.clicked.connect(QtCore.QCoreApplication.instance().quit)
    qbtn.resize(qbtn.sizeHint())

    self.setGeometry(300, 300, 250, 150)
    self.setWindowTitle('Quit Button')
    self.show()

  def closeEvent(self, event):
    reply = QtGui.QMessageBox.question( self, 
                                        'Message', 
                                        "Are you sure you want to quit?",
                                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                        QtGui.QMessageBox.No)
    if reply == QtGui.QMessageBox.Yes:
      event.accept()
    else:
      event.ignore()

def main():
  app = QtGui.QApplication(sys.argv)
  ex = Example()
  sys.exit(app.exec_())


if __name__ == "__main__":
  main()

