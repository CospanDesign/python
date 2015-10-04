#! /usr/bin/python
# editor.py

from PyQt4 import QtGui
import verilog_syntax as syntax

app = QtGui.QApplication([])
editor = QtGui.QPlainTextEdit()
highlight = syntax.VerilogHighlighter(editor.document())
editor.setTabStopWidth(2)
editor.show()

# Load syntax.py into the editor for demo purposes
#infile = open('syntax.py', 'r')
infile = open('wb_gpio.v', 'r')
editor.setPlainText(infile.read())

app.exec_()
