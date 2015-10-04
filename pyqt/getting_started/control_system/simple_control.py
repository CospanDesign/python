#!/usr/bin/python

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import time
import functools

PLANT_RESPONSE = 2
CONTROLLER_RESPONSE = 2



_controller_action_instance = None

#Singleton Magic
def ControllerActions(*args, **kw):
    global _controller_action_instance
    if _controller_action_instance is None:
        _controller_action_instance = _ControllerActions(*args, **kw)
    return _controller_action_instance

class _ControllerActions(QtCore.QObject):

    control_out_change = QtCore.pyqtSignal(int, name = "control_output_change")
    plant_out_change = QtCore.pyqtSignal(int, name = "plant_output_change")
    terminate_threads = QtCore.pyqtSignal(name = "terminate_all_threads")



    def __init__(self, parent = None):
        super (_ControllerActions, self).__init__(parent)
        print "Started"

class Plant(QtCore.QObject):
    def __init__(self):
        super (Plant, self).__init__()

    def terminate_plant(self):
        if self.terminate_flag is not None:
            self.terminate_flag = True

    def control_output_changed(self, control_output):
        if self.control_output is not None:
            self.control_output = control_output

    def process(self, mutex):
        self.ca = ControllerActions()
        self.mutex = mutex
        self.terminate_flag = False
        self.out = 0.0
        self.controller_output = 0.0
        while not self.terminate_flag:
            QtCore.QThread.yieldCurrentThread()
            QtCore.QThread.sleep(PLANT_RESPONSE)
            self.mutex.lock()
            self.ca.plant_out_change.emit(self.calculate_output())
            self.mutex.unlock()

    def calculate_output(self):
        diff = self.controller_output - self.out
        print "Plant calculating output...%d" % diff
        return diff

class Controller(QtCore.QObject):
    def __init__(self):
        super (Controller, self).__init__()

    def terminate_controller(self):
        if self.termiante_flag is not None:
            self.terminate_flag = True

    def plant_output_changed(self, plant_output):
        if self.plant_output is not None:
            self.plant_output = plant_output

    def process(self, mutex):
        self.ca = ControllerActions()
        self.mutex = mutex
        self.ref_input = 0.0
        self.plant_output = 0.0
        self.control_output = 0.0

        self.terminate_flag = False

        while not self.terminate_flag:
            QtCore.QThread.yieldCurrentThread()
            QtCore.QThread.sleep(CONTROLLER_RESPONSE)
            self.mutex.lock()
            self.ca.control_out_change.emit(self.calculate_output())
            self.mutex.unlock()

    def calculate_output(self):
        diff = self.ref_input - self.plant_output
        print "Controller calculating output...%d" % diff
        return diff


class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(250, 150)
        self.layout = QtGui.QVBoxLayout()
        button = QtGui.QPushButton("Exit")
        button.pressed.connect(self.quit)
        self.layout.addWidget(button)
        
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        self.setup_control_system()
        self.setWindowTitle('Center')
        self.show()
        print "Setup GUI"

    def setup_control_system(self):
        self.mutex = QtCore.QMutex()

        self.plant = Plant()
        self.controller = Controller()

        self.control_thread = QtCore.QThread(self)
        self.plant_thread = QtCore.QThread(self)
        self.controller.moveToThread(self.control_thread)
        self.plant_thread.moveToThread(self.plant_thread)

        self.control_thread.started.connect(functools.partial(self.controller.process, self.mutex))
        self.plant_thread.started.connect(functools.partial(self.plant.process, self.mutex))

        self.control_thread.start()
        self.plant_thread.start()
        print "Started both threads..."


    def quit():
        self.cleanup()

    def cleanup(self):
        self.plant.termiate_plant()
        self.controller.terminate_controller()

        self.plant_thread.join()
        self.control_thread.join()


def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
  main()

