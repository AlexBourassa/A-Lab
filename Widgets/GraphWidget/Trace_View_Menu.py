# -*- coding: utf-8 -*-
"""
@author: Alex
"""

from Graph_Widget_Plugin import *
from PyQt4 import QtGui as _gui


class Trace_View_Menu(Graph_Widget_Plugin):
    
    def __init__(self, parent_graph):
        Graph_Widget_Plugin.__init__(self, parent_graph)
        self.menu = self.graph.menu
        self.graph = parent_graph
        
        #Build view menu
        if not 'View' in self.menu:
            self.menu['View'] = dict()
            self.menu['View']['_QMenu'] = self.menu['_QMenuBar'].addMenu('View')
        
        #Update if modules are added or removed
        self.graph.traceAdded.connect(lambda x: self.updateViewMenu())
        self.graph.traceRemoved.connect(lambda x: self.updateViewMenu())
        
        self.updateViewMenu()
        
    def toggleVisible(self):
        for m in self.graph:
            self.graph.setTraceVisible(m, self.menu['View'][m].isChecked())
        
    def updateViewMenu(self):        
        #Add the actions
        for m in self.graph:
            if not m in self:
                self.menu['View'][m] = _gui.QAction(m, self['_QMenu'] ,checkable = True)
                self['_QMenu'].addAction(self[m])
                #Connect signals
                self[m].triggered.connect(lambda: self.toggleVisible())
            self[m].setChecked(True)
                         
        #Remove actions
        for m in self:
            if not m in self.graph:
                self['_QMenu'].removeAction(self[m])
                del self.menu['View'][m]
                
        
    
    #By default these ignore the _QMenu entry (except for __getitem__)
    def __iter__(self):
        k = self.menu['View'].keys()
        k.remove('_QMenu')
        return iter(k)
        
    def __len__(self):
        return len(self.menu['View'])-1
        
    def __getitem__(self, key):
        return self.menu['View'][key]