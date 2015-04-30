# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 09:45:07 2015

@author: Alex
"""

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

class Docked_Module(_gui.QDockWidget):
    visibilityChanged = _core.Signal(bool)
    
    def __init__(self, *args, **kwargs):
        _gui.QDockWidget.__init__(self, *args, **kwargs)
        
    def hideEvent(self, event):
        self.visibilityChanged.emit(self.isVisible())
        
    def showEvent(self, event):
        self.visibilityChanged.emit(self.isVisible())