# -*- coding: utf-8 -*-
"""
This simple plugin adds save/load capapilities to the different modules by
succesivelly calling their save/load functions.

@author: AlexBourassa
"""
from Module_Container_Plugin import Module_Container_Plugin
from PyQt4 import QtGui as _gui
from Generic_UI.Others.Standard_File_Handlers import getFileFormatDict
from Generic_UI.Others.File_Handler import File_Handler

def getSupportedFormats():
    """
    This returns a dictionay of supported file format with the class which
    supports it.  If you have special file_handlers not in the Standard_File_Handler
    list, you can add them here.
    """
    return getFileFormatDict()

class Load_Save(Module_Container_Plugin):
    
    def __init__(self, parent_container, standard_menu = True):
        Module_Container_Plugin.__init__(self, parent_container)
        self.menu = self.container.menu
        
        # Add load/Save Actions to File menu
        if standard_menu:
            self.menu['File']['Save'] = self.menu['File']['_QMenu'].addAction('Save...')
            self.menu['File']['Save'].triggered.connect(lambda: self.save())
            self.menu['File']['Load'] = self.menu['File']['_QMenu'].addAction('Load...')
            self.menu['File']['Load'].triggered.connect(lambda: self.load())
        
    def save(self, modules=None):
        """
        Issues a save command for all modules in modules list.  If <modules>==None, 
        then all the modules in the container will be issued the command.

        <modules> is a list of module names (eg ['mod', 'mod5'])
        """
        # Select the filename
        allowed_formats = ''
        format_dict = getSupportedFormats()
        for format_ext in format_dict:
            allowed_formats += format_dict[format_ext].format_name + ' (' + format_ext + ');;'
        allowed_formats = allowed_formats[:-2]#Remove the 2 extra semi-collumn
        filename = _gui.QFileDialog.getSaveFileName(caption = "Select a location to save the data...", 
                                         directory = self.container.default_folder,
                                         filter = allowed_formats)
        if filename == None:#TODO: Check if this is indead what's returns when no file is selected
            print "Cancelling save..."
            return
        
        # Get the appropriate File_Handler
        ext = '*.' + filename.split('.')[-1]
        handler = format_dict[ext](default_filename = filename)

        # Set the list of modules
        if modules is None: modules = self.container.modules.keys()

        for mod_name in modules:
            if not mod_name in self.container.modules:
                print "No modules named " + mod_name
            elif hasattr(self.container.modules[mod_name], 'save'): 
                handler.beginGroup(mod_name)
                self.container.modules[mod_name].save(file_handler = handler)
                handler.endGroup()
            else: print "Failed to save data for " + mod_name
                
        handler.save()


    def _loadToHandler(self):
        # Select the filename
        allowed_formats = ''
        format_dict = getSupportedFormats()
        for format_ext in format_dict:allowed_formats += format_dict[format_ext].format_name + ' (' + format_ext + ');;'
        allowed_formats = allowed_formats[:-2]#Remove the 2 extra semi-collumn
        filenames = _gui.QFileDialog.getOpenFileNames(caption = "Select files to load...", 
                                         directory = self.container.default_folder,
                                         filter = allowed_formats)
                                         #selectedFilter = 0)
        if filenames == None:#TODO: Check if this is indead what's returns when no file is selected
            print "Cancelling loads..."
            return
        
        # Fill the file handler with the data in all files
        handler = File_Handler() #Begin with an empty file_handler
        for filename in filenames:
            ext = '*.' + filename.split('.')[-1]
            temp_handler = format_dict[ext](default_filename = filename)
            temp_handler.load()
            handler.mergeHandler(temp_handler)
        return handler

        
    def load(self, modules=None):
        """
        Issues a load command for all modules in modules list.  If <modules>==None, 
        then all the modules in the container will be issued the command.

        <modules> is a list of module names (eg ['mod', 'mod5'])
        """
        handler = self._loadToHandler()

        # Set the list of modules
        if modules is None: modules = self.container.modules.keys()
        
        # Issue the load command
        for mod_name in modules:
            if not mod_name in self.container.modules:
                print "No modules named " + mod_name
            elif hasattr(self.container.modules[mod_name], 'load'):
                handler.beginGroup(mod_name)
                #try:
                self.container.modules[mod_name].load(file_handler = handler)
                #except:
                #    print "Failed to load data from " + mod_name
                handler.endGroup()
            else: print "No load function is defined for " + mod_name

    def loadKey2Mod(self, key, mod_name, handler = None, present_in_both = True):
        """
        1. Loads a selected file into a File_Handler. If no handlers was supplied
        2. Look for all groups named <key>
        3. Call the load function of <mod> with each of those groups
        """
        if handler == None:
            handler = self._loadToHandler()
        paths = handler.findAll(key, present_in_both = present_in_both)
        for path in paths:
            hiar_list = handler.data.getHiarList(path)
            hiar_list.pop(-1)
            for group in hiar_list:
                handler.beginGroup(group)
                self.container.modules[mod_name].load(file_handler = handler)
            handler.resetToRoot()




