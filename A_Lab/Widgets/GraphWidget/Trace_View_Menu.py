# -*- coding: utf-8 -*-
"""
@author: AlexBourassa
"""

from A_Lab.Widgets.GraphWidget.Graph_Widget_Plugin import *
from PyQt4 import QtGui as _gui


class Trace_View_Menu(Graph_Widget_Plugin):
    
    def __init__(self, parent_graph):
        Graph_Widget_Plugin.__init__(self, parent_graph)
        self.menu = self.graph.menu
        
        #Build view menu
        if not 'View' in self.menu:
            self.menu['View'] = dict()
            self.menu['View']['_QMenu'] = self.menu['_QMenuBar'].addMenu('View')

        # Add the show/hide all
        self.menu['View']['Show All'] = _gui.QAction('Show All', self['_QMenu'])
        self.menu['View']['Hide All'] = _gui.QAction('Hide All', self['_QMenu'])
        self['_QMenu'].addAction(self['Show All'])
        self['_QMenu'].addAction(self['Hide All'])
        self['Show All'].triggered.connect(lambda: self.showAll())
        self['Hide All'].triggered.connect(lambda: self.hideAll())
        
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

    def hideAll(self):
        """
        Uncheck all the traces to hide them all
        """
        for trc in self:
            self[trc].setChecked(False)
            self.toggleVisible()

    def showAll(self):
        """
        Check all the traces to show them all
        """
        for trc in self:
            self[trc].setChecked(True)
            self.toggleVisible()
                
        
    
    #By default these ignore the _QMenu entry (except for __getitem__)
    def __iter__(self):
        k = list(self.menu['View'].keys())
        k.remove('_QMenu')
        k.remove('Show All')
        k.remove('Hide All')
        return iter(k)
        
    def __len__(self):
        return len(self.menu['View'])-1
        
    def __getitem__(self, key):
        return self.menu['View'][key]