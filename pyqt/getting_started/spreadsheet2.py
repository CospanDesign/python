#! /usr/bin/python

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *



class MyTable(QTableView):
    def __init__(self, data, *args):
        super(MyTable, self).__init__(*args)
        #data = {'col1':['1', '2', QWidget()], 'col2':['4', '5', '6'], 'col3':['7', '8', '9']}
        self.data = data
        self.setmydata()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()


    def setmydata(self):
        horHeaders = []
        for n, key in enumerate(sorted(self.data.keys())):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(item)
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)



class I2CToken(QWidget):
    i2c_types = [ "UNKNOWN",
                  "START",
                  "WRITE",
                  "READ",
                  "END",
                  "RESTART"]

    def __init__(self):
        super (I2CToken, self).__init__()

    def set_type(self, i2c_type):
        pass



class I2CCommandRow(QObject):
    def __init__(self):
        super(I2CCommandRow, self).__init__()
        self.tokens = []

    def add_action(self):
        #Add an action to he list of I2C Commands
        #This action is blank and must be set later
        pass

    def set_action(self, index, i2c_action_type):
        pass

    def get_action_list(self):
        #Return the series of I2C Actions as a set of commands to be read by an I2C Device
        pass

    def __len__(self):
        return len(self.tokens)

class TableModel(QAbstractItemModel):
    def __init__(self):
        super (TableModel, self).__init__()
        self.headers = []
        self.columns = 0
        self.i2c_rows = []

    def data(self, 

def main(args):
    app = QApplication(args)
    data = {}
    table = MyTable(data, 5, 3)

    table.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)
