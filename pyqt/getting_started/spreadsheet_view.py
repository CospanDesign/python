#! /usr/bin/python

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *


def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

token_type = enum(   "UNKNOWN",
                    "START",
                    "STOP",
                    "START_START",
                    "WRTIE",
                    "READ")


class I2CTable(QTableView):
    def __init__(self):
        super(I2CTable, self).__init__()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.m = I2CTableModel()
        self.setModel(self.m)

        self.m.add_i2c_row()

class I2CToken(QWidget):

    def __init__(self):
        super (I2CToken, self).__init__()
        self.data = None
        self.i2c_type = token_type.UNKNOWN
        self.v = QLabel("Test")

    def set_type(self, i2c_type):
        self.i2c_type = i2c_type
        #XXX: SETUP THE VIEW TO THE TOKEN SPECIFIC VIEW
        pass

    def get_view(self):
        #Need to see if the GUI can draw a widget
        return self.v

    def as_record(self):
        return self.i2c_type, self.data


class I2CCommandRow(QObject):
    def __init__(self):
        super(I2CCommandRow, self).__init__()
        self.tokens = []
        self.tokens.append(I2CToken())

    def add_token(self):
        #This token is blank and must be set later
        self.tokens.append(I2CToken)

    def set_action(self, index, i2c_action_type):
        assert len(self.tokens) >= index
        self.tokens[index].set_type(i2c_action_type)

    def get_tokens_as_list(self):
        #Return the series of I2C Actions as a set of commands to be read by an I2C Device
        tokens_list = []
        for token in self.tokens:
            tokens_list.append(token.as_record())
        return tokens_list

    def __len__(self):
        return len(self.tokens)

    def get_token(self, column):
        assert len(self.tokens) >= column
        return self.tokens[column]


class I2CTableModel(QAbstractItemModel):
    def __init__(self):
        super (I2CTableModel, self).__init__()
        self.headers = []
        self.columns = 0
        self.i2c_rows = []

    def data(self, index, role):
        if role != Qt.DisplayRole:
            return
        node = self.nodeFromIndex(index)
        t = node.get_view()
        #print "Node Tye: %s" % str(type(t))
        return t

    def nodeFromIndex(self, index):
        assert len(self.i2c_rows) >= index.row()
        return self.i2c_rows[index.row()].get_token(index.column())

    def clear(self):
        self.i2c_rows = []
        self.reset()

    def rowCount(self, index):
        if len(self.i2c_rows) == 0:
            return 0

        return len(self.i2c_rows[index.row()])

    def columnCount(self, index):
        return len(self.i2c_rows)

    def add_i2c_row(self):
        self.i2c_rows.append(I2CCommandRow())
        self.reset()

    def index(self, row, column, parent):
        return self.createIndex(row, column, self)

    def parent(
