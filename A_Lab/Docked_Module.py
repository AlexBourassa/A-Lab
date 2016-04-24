# -*- coding: utf-8 -*-
"""
@author: AlexBourassa
"""

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

class Docked_Module(_gui.QDockWidget):
    visibilityChanged = _core.Signal(bool)
    requestNewModule = _core.Signal(str, _gui.QWidget, object)
    requestSelfDestroy = _core.Signal()
    
    def __init__(self, *args, **kwargs):
        _gui.QDockWidget.__init__(self, *args, **kwargs)
        
    def hideEvent(self, event):
        #self.widget().hide()
        self.visibilityChanged.emit(self.isVisible())
        
    def showEvent(self, event):
        #self.widget().show()
        self.visibilityChanged.emit(self.isVisible())
        
    def closeEvent(self, event):
        if hasattr(self.widget(),'closeEvent'):
            self.widget().closeEvent(event)
        _gui.QDockWidget.closeEvent(self, event)

    def destroyEvent(self):
        """ This will be called explicitelly by the module container before destroying a widget
        """
        if hasattr(self.widget(), 'destroyEvent'):
            self.widget().destroyEvent()
            self.widget().deleteLater()

    # def showEvent(self, event):
    #     if hasattr(self.widget(), 'showEvent'):
    #         self.widget().showEvent(event)
    #     _gui.QDockWidget.showEvent(self, event)