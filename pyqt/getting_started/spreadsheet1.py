#! /usr/bin/python

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *


data = {'col1':['1', '2', '3'], 'col2':['4', '5', '6'], 'col3':['7', '8', '9']}


class MyTable(QTableWidget):
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




def main(args):
    app = QApplication(args)
    data = {}
    table = MyTable(data, 5, 3)

    table.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)
