#! /usr/bin/python
import sys
import argparse
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.phonon import Phonon


DESCRIPTION = "\n" \
"Play a video with phonon\n" \
"\n"

EPILOG = "\n" \
"Example:\n" \
"\tphonon_example /path/to/video\n" \
"\n"


class VW (Phonon.VideoWidget):


    def __init__(self):
        print "Hello!"
        super (VW, self).__init__()

    def paintEvent(self, paint_event):
        super (VW, self).paintEvent(paint_event)

    def render( self,
                qpd, 
                targetOffset =   QPoint(), 
                sourceRegion    =   QRegion(), 
                flags=QWidget.DrawWindowBackground|QWidget.DrawChildren):
        print "hi"
        super (VW, self).render(qpd, 
                                targetOffset,
                                sourceRegion, 
                                flags)
    def render( self,
                painter, 
                targetOffset=QPoint(),
                sourceRegion=QRegion(),
                flags=QWidget.DrawWindowBackground|QWidget.DrawChildren):
        print "hi"

        super (VW, self).render(painter, 
                                targetOffset=QPoint(),
                                sourceRegion=QRegion(),
                                flags=QWidget.DrawWindowBackground|QWidget.DrawChildren)




class VP (Phonon.VideoPlayer):
    def paintEvent(self, paint_event):
        print "hi"
        super (VP, self).paintEvent(paint_event)

    def render( self,
                qpd, 
                targetOffset =   QPoint(), 
                sourceRegion    =   QRegion(), 
                flags=QWidget.DrawWindowBackground|QWidget.DrawChildren):
        print "hi"
        super (VP, self).render(qpd, 
                                targetOffset,
                                sourceRegion, 
                                flags)
    def render( self,
                painter, 
                targetOffset=QPoint(),
                sourceRegion=QRegion(),
                flags=QWidget.DrawWindowBackground|QWidget.DrawChildren):
        print "hi"

        super (VP, self).render(painter, 
                                targetOffset=QPoint(),
                                sourceRegion=QRegion(),
                                flags=QWidget.DrawWindowBackground|QWidget.DrawChildren)



def main(argv):
    #Parse out the command line arguments
    parser = argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = DESCRIPTION,
            epilog = EPILOG)

    parser.add_argument("-d", "--debug",
                        action='store_true',
                        help="Output test debug information")
    parser.add_argument("media",
                        type = str, 
                        nargs=1, 
                        default="all", 
                        help = "Media to load")

    args = parser.parse_args()
    if args.debug:
        print "Debug Enabled"
        debug = True


    media_source = args.media[0]
    app = QApplication(sys.argv)
    #vp = Phonon.VideoPlayer()
    vp = VP()
    media = Phonon.MediaSource(media_source)
    vp.load(media)
    vp.play()
    #vp.VideoWidget = VW()
    vp.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv)
