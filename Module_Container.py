# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 18:36:53 2015

@author: Alex

@TODO: Make 
"""

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core
from Docked_Module import Docked_Module

import os as _os

default_params = {'autoSave':True}

class Module_Container(_gui.QMainWindow):
    
    moduleAdded = _core.Signal(str)
    moduleRemoved = _core.Signal(str)
    
    def __init__(self, default_folder=None, **kwargs):
        """
        This is the main object that will contain all the modules.
        This class contains only the bare minimum.
        Do not change the variables :
            self.modules
            self._docked_widget
            self.menu
        As these will be used by plugins
        """
                
        #Set the default directory
        if type(default_folder)!=str:
            default_folder = _os.getcwd()
        if not _os.path.isdir(default_folder):
            default_folder = _os.getcwd()
        self.default_folder = default_folder
        
        #Initialize the windows
        _gui.QMainWindow.__init__(self)
        
        #Set some docking options
        self.setDockOptions(_gui.QMainWindow.AnimatedDocks | 
                            _gui.QMainWindow.AllowNestedDocks | 
                            _gui.QMainWindow.AllowTabbedDocks)
        
        #Initialize some variables
        self.modules = dict()
        self._docked_widgets = dict()
        for k in default_params:
            if not k in kwargs: kwargs[k] = default_params[k]
        self.params = kwargs
        
        #Build menu
        self.buildMenu()
        
        self.show()
        
    def buildMenu(self):
        """
        Build the menu for the windows.
        """
        #Add a menu bar
        self.menu = dict()
        self.menu['_QMenuBar'] = _gui.QMenuBar()
        self.setMenuBar(self.menu['_QMenuBar'])
        
        #Create a File Menu
        self.menu['File'] = dict()
        self.menu['File']['_QMenu'] = self.menu['_QMenuBar'].addMenu('File')
        
        #Add Actions
        self.menu['File']['Close'] = self.menu['File']['_QMenu'].addAction('Close')
        self.menu['File']['Close'].triggered.connect(lambda: self.close())
                
        
        
    def addModule(self, module_name, module_widget, initial_pos=None):
        """
        Add a widget to the main containner
        
        initial_pos can be either None (widget is not visible) or 
            _core.Qt.TopDockWidgetArea
            _core.Qt.BottomDockWidgetArea
            _core.Qt.LeftDockWidgetArea
            _core.Qt.RightDockWidgetArea
        """
        #Make sure no module_name is used twice
        suffix = ''
        while module_name+suffix in self.modules:
            if suffix == '':
                suffix = '2'
            else:
                suffix = str(1+int(suffix))
        module_name += suffix
            
        #Create Dock Widget
        d = Docked_Module(module_name)
        d.setWidget(module_widget)
        d.setObjectName(module_name)
        
        #Add the dock widget to the container
        if initial_pos == None:
            self.addDockWidget(_core.Qt.TopDockWidgetArea, d)
            d.hide()
        else:
            self.addDockWidget(initial_pos, d)
        
        #Add the widgets to the list
        self.modules[module_name] = module_widget
        self._docked_widgets[module_name] = d
        self.moduleAdded.emit(module_name)

         
    def closeEvent(self, event):
        """
        Save some settings under: 
            <default_folder>\settings
        """
        if self.params['autoSave']:
            self.saveUI()
        
        #Pass on the close event
        super(Module_Container, self).closeEvent(event)
        
    def saveUI(self):
        print "Saving state..."
        #Build filename and setting object
        filename = _os.path.join(self.default_folder, 'settings')
        settings = _core.QSettings(filename, _core.QSettings.IniFormat)
        
        #Save values
        settings.setValue('Module_Container/State', self.saveState())
        settings.setValue('Module_Container/Geometry', self.saveGeometry())
        
        #Close all modules
        for m in self.modules.values():
            m.close()
        
        
    def loadUISettings(self):
        #Restore the previous states
        filename = _os.path.join(self.default_folder, 'settings')
        settings = _core.QSettings(filename, _core.QSettings.IniFormat)
        
        if settings.contains('Module_Container/State') and settings.contains('Module_Container/Geometry'):
            self.restoreState(settings.value('Module_Container/State'))
            self.restoreGeometry(settings.value('Module_Container/Geometry')) 
        
    
    def __iter__(self):
        return iter(self.modules)
        
    def __len__(self):
        return len(self.modules)
        
    def __getitem__(self, key):
        return self.modules[key]
        
    def __setitem__(self, key, value):
        self.addModules(key, **value)

   