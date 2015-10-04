import sys
from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon

app = QtGui.QApplication(sys.argv)
vp = Phonon.VideoPlayer()
media = Phonon.MediaSource("i.mpg")
vp.load(media)
vp.play()
vp.show()

app.exec_()
