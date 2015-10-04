#! /usr/bin/python

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *


def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

token_type = enum("UNKNOWN",
                  "START",
                  "STOP",
                  "START_START",
                  "WRTIE",
                  "READ")


class I2CTable(QWidget):
    def __init__(self):
        super(I2CTable, self).__init__()
        self.l = QGridLayout()
        self.l.addWidget(I2CToken(), 0, 0)
        self.setLayout(self.l)

#class I2CToken(QWidget):
class I2CToken(QLabel):

    def __init__(self):
        super (I2CToken, self).__init__("Test")
        self.data = None
        self.i2c_type = token_type.UNKNOWN
        #self.v = QLabel("Test")
        self.setFixedSize(100, 100)
        self.setStyleSheet("QWidget {background-color:blue}")

    def set_type(self, i2c_type):
        self.i2c_type = i2c_type
        #XXX: SETUP THE VIEW TO THE TOKEN SPECIFIC VIEW
        pass

    def get_view(self):
        #Need to see if the GUI can draw a widget
        return self.v

    def as_record(self):
        return self.i2c_type, self.data



