#!/usr/bin/env python

#Distributed under the MIT licesnse.
#Copyright (c) 2013 Cospan Design (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import os
import sys
import json
import copy

from PyQt4.QtCore import *
from PyQt4.QtGui import *

"""
This code was inspired by
    hipersayanx.blogspot.com

On this post:

http://stackoverflow.com/questions/182197/how-do-i-watch-a-file-for-changes-using-python


"""

#@QtCore.pyqtSlot(str)
#def directory_changed(path):
#    print('Directory Changed!!!')
#
#@QtCore.pyqtSlot(str)
#def file_changed(path):
#    print('File Changed!!!')
#
#fs_watcher = QtCore.QFileSystemWatcher(['/path/to/files_1', '/path/to/files_2', '/path/to/files_3'])
#fs_watcher.connect(fs_watcher, QtCore.SIGNAL('directoryChanged(QString)'), directory_changed)
#fs_watcher.connect(fs_watcher, QtCore.SIGNAL('fileChanged(QString)'), file_changed)

class FileWatcherError(Exception):
    """File Watcher Error

    Errors associated with watching files:
        File list is empty.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class FileWatcher (QObject):

    def __init__(self):
        super(FileWatcher, self).__init__()
        self.file_paths = []
        self.file_watcher = None

    def watch_files (self,
                     file_list,
                     directory_change_cb,
                     file_change_cb):
        """
        sets up the callbacks to get notified when the files in file list has
        changed. The user sets up callbacks to be notified when either the
        files within the list has changed or the diretory containing the files
        have changed. The function will receive a string identifying which
        file or directory has changed, the format of the functions are as
        follows:

        Directory change callback:
            directory_change_cb(path_of_change)

        Function change callback:
            file_change_cb(path_of_change)

        If the user calls this function a second time the previous files and
        directory that were watched are overwritten

        Args:
            file_list (list of strings): A list of files to watch
            directory_change_cb (function): a function to call when the
                directory changes
            file_change_cb (function): a function to call when one of the
                file changes

        Returns:
            Nothing

        Raises:
            Nothing
        """
        if len(file_list) == 0:
            raise FileWatcherError("File List cannot be empty!")

        self.file_watcher = QFileSystemWatcher(file_list)
        self.file_watcher.connect(self.file_watcher,
                                  SIGNAL("directoryChanged(QString)"),
                                  directory_change_cb)
        self.file_watcher.connect(self.file_watcher,
                                  SIGNAL("fileChanged(QString)"),
                                  file_change_cb)


