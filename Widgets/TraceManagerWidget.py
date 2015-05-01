# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 16:00:09 2015

@author: Alex
"""

from PyQt4 import QtGui as _gui
from PyQt4 import uic as _uic
import os as _os

class TraceManagerWidget(_gui.QWidget):
    
    def __init__(self, **kwargs):
        _gui.QWidget.__init__(self)
        _uic.loadUi(_os.path.join(_os.path.dirname(__file__),'TraceManagerWidget.ui'), self) 
        
    def addGraph(self, graph_name, graph_widget):
        items = _gui.QTreeWidgetItem()
        self.treeWidget.setColumnCount(1)
        for s in graph_widget.traces.keys():
            items.append(_gui.QTreeWidgetItem())
        self.treeWidget.addTopLevelItems(items)
        