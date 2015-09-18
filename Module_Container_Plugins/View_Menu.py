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

        # Add the show/hide all
        self.menu['View']['Show All'] = _gui.QAction('Show All', self['_QMenu'])
        self.menu['View']['Hide All'] = _gui.QAction('Hide All', self['_QMenu'])
        self['_QMenu'].addAction(self['Show All'])
        self['_QMenu'].addAction(self['Hide All'])
        self['Show All'].triggered.connect(lambda: self.showAll())
        self['Hide All'].triggered.connect(lambda: self.hideAll())
        
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

    def hideAll(self):
        """
        Uncheck all the modules to hide them all
        """
        for mod in self:
            self[mod].setChecked(False)
            self.toggleVisible()

    def showAll(self):
        """
        Check all the modules to show them all
        """
        for mod in self:
            self[mod].setChecked(True)
            self.toggleVisible()
    
    #By default these ignore the _QMenu entry (except for __getitem__)
    def __iter__(self):
        k = self.menu['View'].keys()
        k.remove('_QMenu')
        k.remove('Show All')
        k.remove('Hide All')
        return iter(k)
        
    def __len__(self):
        return len(self.menu['View'])-1
        
    def __getitem__(self, key):
        return self.menu['View'][key]