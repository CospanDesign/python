import os
from PyQt4 import QtGui
from PyQt4.phonon import Phonon

if __name__ == "__main__":
    app = QtGui.QApplication([])
    app.setApplicationName("Phonon Video Player")

    file_path = "i.mpg"
    media_src = Phonon.MediaSource(file_path)
    media_obj = Phonon.MediaObject()

    media_obj.setCurrentSource(media_src)

    video_widget = Phonon.VideoWidget()
    Phonon.createPath(media_obj, video_widget)

    audio_out = Phonon.AudioOutput(Phonon.VideoCategory)
    Phonon.createPath(media_obj, audio_out)

    video_widget.show()
    media_obj.play()
    print "Play media"

    app.exec_()
