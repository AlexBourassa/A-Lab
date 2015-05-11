# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

This module handles save/load
"""
from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

class Load_Save_Widget(_gui.QWidget):
    def __init__(self, parent=None, **kwargs):
        _gui.QWidget.__init__(self, parent=parent)


class Pickle_Handler(File_Handler):
    def __init__(self, filename):
        super(Pickle_Handler, self).__init__(self, filename)


class File_Handler():
    def __init__(self, filename):
        self.filename = filename
        
    def load(self):
        raise NotImplemented
        
    def addData(self, x, y):
        raise NotImplemented
        
    def addHeaders(self, headers):
        raise NotImplemented
        
    def save(self):
        raise NotImplemented
        
