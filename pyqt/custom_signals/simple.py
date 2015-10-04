#!/usr/bin/python

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

_action_instance = None

#Singleton Magic
def Actions(*args, **kw):
    global _action_instance
    if _action_instance is None:
        _action_instance = _Actions(*args, **kw)
    return _action_instance

class _Actions(QtCore.QObject):

    #Create a couple of signals
    signal1 = QtCore.pyqtSignal(name = "custom_signal")
    signal2 = QtCore.pyqtSignal(int, name = "custom_arg_signal")

    def __init__(self, parent = None):
        super (_Actions, self).__init__(parent)



#This class will emit a signal
class SignalEmitterWidget(QtGui.QPushButton):

    def __init__(self, parent):
        super (SignalEmitterWidget, self).__init__("Button", parent)
        #Get a reference to the action class
        self.actions = Actions()

    def mousePressEvent(self, event):
        print "Signal Emitted"
        self.actions.signal1.emit()
        self.actions.signal2.emit(100)
        super (SignalEmitterWidget, self).mousePressEvent(event)

#This class will receive a signal
class Example(QtGui.QWidget):
    def __init__(self):
        super(Example, self).__init__()
        #Get a reference to th Actions Class
        self.actions = Actions()
        self.initUI()

    def initUI(self):
        self.resize(250, 150)

        self.setWindowTitle("Custom Signals/Slots")
        self.layout = QtGui.QHBoxLayout()

        #Add the button
        self.layout.addWidget(SignalEmitterWidget(self))
        self.setLayout(self.layout)

        #Connect the Signal to the Slot
        self.actions.signal1.connect(self.slot_receiver)
        self.actions.signal2.connect(self.slot_receiver_num)

        self.show()

    def slot_receiver(self):
        print ("Recieved a signal")

    def slot_receiver_num(self, val):
        print ("Reading number: %d" % val)


def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()



