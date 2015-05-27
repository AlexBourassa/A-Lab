# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

@TODO: Doesn't delete entry when moduleRemoved triggers
"""

from Module_Container_Plugin import Module_Container_Plugin
from PyQt4 import QtGui as _gui


class View_Menu(Module_Container_Plugin):
    
    def __init__(self, parent_container):
        Module_Container_Plugin.__init__(self, parent_container)
        self.menu = self.container.menu
        
        #Build view menu
        self.menu['View'] = dict()
        self.menu['View']['_QMenu'] = self.menu['_QMenuBar'].addMenu('View')
        
        #Update if modules are added or removed
        self.container.moduleAdded.connect(lambda x: self.updateViewMenu())
        self.container.moduleRemoved.connect(lambda x: self.updateViewMenu())
        
        self.updateViewMenu()
        
    def toggleVisible(self):
        for m in self.container.modules:
            self.container._docked_widgets[m].setVisible(self.menu['View'][m].isChecked())
        
    def updateViewMenu(self):       
        #Add the actions
        for m in self.container.modules:
            if not m in self:
                self.menu['View'][m] = _gui.QAction(m, self['_QMenu'] ,checkable = True)
                self['_QMenu'].addAction(self[m])
                #Connect signals
                self[m].triggered.connect(lambda: self.toggleVisible())
                self.container._docked_widgets[m].visibilityChanged.connect(self.updateViewMenu)
            self[m].setChecked(self.container._docked_widgets[m].isVisible())
                         
        #Remove actions
        for m in self:
            if not m in self.container.modules.keys():
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