# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

This file contains the base class you should use as a main windows for your
application.  To create a useful application, you should then add pre-made
Modules and Plugins and if necessary, add your own. (You will probably want 
to add your own when working with specific devices)

The Module Container is also meant to be extended via Plugins.  The plugin 
structure relies on the Module Container class attributes, so you should be
careful in modifying this file.  In fact, most functionalities should be
implemented at the Plugin level.  That is, if you wish to add a feature not
currently present in the Module Container class, you should create a new
plugin.

Plugins and Modules should in theory be independents.  Note that it is possible
that some of these classes need to access and modify shared Module_Container 
resources or interact with other Plugins or Modules.  Those interactions should
however remains as minimal as possible to obtain the desired functionalities and
each individual Plugins or Modules should implement some dynamical handling of
the shared resources and react appropriately when these resources change.
"""

#@Bug: I have to load this one first or else PyQt defaults to V1...
from qtconsole.rich_jupyter_widget import RichJupyterWidget

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core
import sip as _sip
from A_Lab.Docked_Module import *

import os as _os

default_params = {'autoSave':True, 'standardPlugins':True, 'kill_kernel_pid':None}

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

        self.setWindowTitle('A_Lab Container')
        
        #Set some docking options
        self.setDockOptions(_gui.QMainWindow.AnimatedDocks | 
                            _gui.QMainWindow.AllowNestedDocks | 
                            _gui.QMainWindow.AllowTabbedDocks)
        
        #Initialize some variables
        self.modules = dict()
        self._docked_widgets = dict()
        self.plugins = dict()
        for k in default_params:
            if not k in kwargs: kwargs[k] = default_params[k]
        self.params = kwargs
        
        #Build menu
        self.buildMenu()
        
        #Add Some Plugins
        if kwargs['standardPlugins']: self.addStandardPlugins()
        
        #Don't show if show not requested
        if 'show' in kwargs and not kwargs['show']: 
            pass
        else:
            self.show()
        
    def addStandardPlugins(self):
        from A_Lab.Module_Container_Plugins.View_Menu import View_Menu
        from A_Lab.Module_Container_Plugins.Load_Save import Load_Save
        self.plugins['View_Menu'] = View_Menu(self)
        self.plugins['Load_Save'] = Load_Save(self)
        
        
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
                
    def removeModule(self, name):
        d = self._docked_widgets[name]
        d.close()
        d.destroyEvent()
        d.deleteLater()
        del self._docked_widgets[name]
        del self.modules[name]
        self.moduleRemoved.emit(name)


        
    def addModule(self, module_name, module_widget, initial_pos=_core.Qt.TopDockWidgetArea):
        """
        Add a widget to the main containner
        
        initial_pos can be either None (widget is floating) or 
            _core.Qt.TopDockWidgetArea
            _core.Qt.BottomDockWidgetArea
            _core.Qt.LeftDockWidgetArea
            _core.Qt.RightDockWidgetArea
        """
        if self.params['autoSave']: self.saveUI()
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
            d.setFloating(True)
        else:
            self.addDockWidget(initial_pos, d)
        
        #Add the widgets to the list
        self.modules[module_name] = module_widget
        self._docked_widgets[module_name] = d
        self.moduleAdded.emit(module_name)
        
        #Load the UI
        self.loadUISettings()
        d.show()        
        
        #Connect signal to allow for requests
        d.requestNewModule.connect(lambda name, widget, pos: self.addModule(module_name + ' ' + name, widget, initial_pos=pos))
        d.requestSelfDestroy.connect(lambda: self.removeModule(module_name))
         
    def closeEvent(self, event):
        """
        Save some settings under: 
            <default_folder>\settings
        """
        if self.params['autoSave']: self.saveUI()
            
        #Close all modules
        for m in list(self.modules.values()):
            m.close()

        #Pass on the close event
        super(Module_Container, self).closeEvent(event)

        #Kills the kernel
        if self.params['kill_kernel_pid']!=None:
            import signal
            _os.kill(self.params['kill_kernel_pid'], signal.SIGTERM)

        
    def saveUI(self):
        #Build filename and setting object
        filename = _os.path.join(self.default_folder, 'settings')
        settings = _core.QSettings(filename, _core.QSettings.IniFormat)
        
        #Save values
        settings.setValue('Module_Container/State', self.saveState())
        settings.setValue('Module_Container/Geometry', self.saveGeometry())
        
        # Save module's values (checks if a saveSettings function is implemented
        # if so, calls it with the QSettings object)
        settings.beginGroup('Modules')
        for mod_name in self.modules:
            if hasattr(self.modules[mod_name], 'saveSettings'): 
                settings.beginGroup(mod_name)
                try: self.modules[mod_name].saveSettings(settingsObj = settings)
                except: print(("Failed to save settings for " + mod_name))
                settings.endGroup()
                
                
        # Save plugins's values (checks if a saveSettings function is implemented
        # if so, calls it with the QSettings object)
        settings.beginGroup('Plugins')
        for plug_name in self.plugins:
            if hasattr(self.plugins[plug_name], 'saveSettings'): 
                settings.beginGroup('Plugins')
                try: self.plugins[plug_name].saveSettings(settingsObj = settings)
                except: print(("Failed to save settings for " + plug_name))
                settings.endGroup()
        
        settings.endGroup()
        
        
    def loadUISettings(self):
        #Restore the previous states
        filename = _os.path.join(self.default_folder, 'settings')
        settings = _core.QSettings(filename, _core.QSettings.IniFormat)
        
        if settings.contains('Module_Container/State') and settings.contains('Module_Container/Geometry'):
            self.restoreState(settings.value('Module_Container/State'))
            self.restoreGeometry(settings.value('Module_Container/Geometry'))
            
        # Load module's values (checks if a loadSettings function is implemented
        # if so, calls it with the QSettings object)
        settings.beginGroup('Modules')
        for mod_name in self.modules:
            if hasattr(self.modules[mod_name], 'loadSettings'): 
                settings.beginGroup(mod_name)
                try: self.modules[mod_name].loadSettings(settingsObj = settings)
                except: print(("Failed to load settings for " + mod_name))
                settings.endGroup()
        settings.endGroup()
                
        # Load plugins's values (checks if a loadSettings function is implemented
        # if so, calls it with the QSettings object)
        settings.beginGroup('Plugins')
        for plug_name in self.plugins:
            if hasattr(self.plugins[plug_name], 'loadSettings'):
                settings.beginGroup(plug_name)
                try: self.plugins[plug_name].loadSettings(settingsObj = settings)
                except: print(("Failed to load settings for " + plug_name))
                settings.endGroup()
        settings.endGroup()
        
    
    def __iter__(self):
        return iter(self.modules)
        
    def __len__(self):
        return len(self.modules)
        
    def __getitem__(self, key):
        return self.modules[key]
        
    def __setitem__(self, key, value):
        self.addModules(key, **value)
        



# DEPRECATED


# def launchApp(launch_script_main):
#     """
#     Not done yet!  Don't use this!
#
#     I plan on building a function sort of like this that makes the startup script much easier
#     """
#     # This part is a bit more involved (compared to the creation of the rest of the
#     # UI), so if you don't feel comfortable with what's happenning here, leave it
#     # alone...
#
#     #uiThread = _core.QThread()
#     app = _gui.QApplication([])
#
#     # Create and display the splash screen
#     splash_pix = _gui.QPixmap('SplashScreen.png')
#     splash = _gui.QSplashScreen(splash_pix, _core.Qt.WindowStaysOnTopHint)
#     splash.setMask(splash_pix.mask())
#     splash.show()
#     app.processEvents()
#
#
#     import inspect as _inspect
#     import IPython
#     from IPython.utils.frame import extract_module_locals
#
#     func_src = _inspect.getsourcelines(launch_script_main)[0]
#     print((_inspect.getmodule(launch_script_main)))
#
#     func_src.append('splash.finish()')
#
#     # Runs a new IPython kernel, that begins the qt event loop.
#     #
#     # Other options for the ipython kernel can be found at:
#     # https://ipython.org/ipython-doc/dev/config/options/kernel.html
#     #
#     # To connect to the kernel use the info in <...>\.ipython\profile_default\security\kernel-example.json
#     # where <...> under windows is probably C:\Users\<username>
#     (current_module, current_ns) = extract_module_locals(depth=0)
#     IPython.start_kernel(user_ns = current_ns,
#                          exec_lines=func_src,
#                          gui='qt',
#                          connection_file='kernel-example.json')

   