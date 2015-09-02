# -*- coding: utf-8 -*-
"""
This simple plugin adds save/load capapilities to the different modules by
succesivelly calling their save/load functions.

@author: AlexBourassa
"""
from Module_Container_Plugin import Module_Container_Plugin
from PyQt4 import QtGui as _gui
from Generic_UI.Others.Standard_File_Handlers import getFileFormatDict
from File_Handler import File_Handler

def getSupportedFormats():
    """
    This returns a dictionay of supported file format with the class which
    supports it.  If you have special file_handlers not in the Standard_File_Handler
    list, you can add them here.
    """
    return getFileFormatDict()

class Load_Save(Module_Container_Plugin):
    
    def __init__(self, parent_container):
        Module_Container_Plugin.__init__(self, parent_container)
        self.menu = self.container.menu
        
        #Add load/Save Actions to File menu
        self.menu['File']['Save'] = self.menu['File']['_QMenu'].addAction('Save...')
        self.menu['File']['Save'].triggered.connect(lambda: self.save())
        self.menu['File']['Load'] = self.menu['File']['_QMenu'].addAction('Load...')
        self.menu['File']['Load'].triggered.connect(lambda: self.load())
        
    def save(self):
        allowed_formats = ''
        format_dict = getSupportedFormats()
        print format_dict
        for format_ext in format_dict:
            allowed_formats += format_dict[format_ext].format_name + ' (' + format_ext + ');;'
        allowed_formats = allowed_formats[:-2]#Remove the 2 extra semi-collumn
        print allowed_formats
        filename = _gui.QFileDialog.getSaveFileName(caption = "Select a location to save the data...", 
                                         directory = self.container.default_folder,
                                         filter = allowed_formats)
        if filename == None:#TODO: Check if this is indead what's returns when no file is selected
            print "Cancelling save..."
            return
        
        ext = '*.' + filename.split('.')[-1]
        handler = format_dict[ext](default_filename = filename)
        for mod_name in self.container.modules:
            if hasattr(self.container.modules[mod_name], 'save'): 
                handler.beginGroup(mod_name)
                self.container.modules[mod_name].save(file_handler = handler)
                #except: print "Failed to save data for " + mod_name
                handler.endGroup()
        handler.save()
        
    def load(self):
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
        
        handler = File_Handler() #Begin with an empty file_handler
        for filename in filenames:
            ext = '*.' + filename.split('.')[-1]
            temp_handler = format_dict[ext](default_filename = filename)
            temp_handler.load()
            handler.mergeHandler(temp_handler)
            
        for mod_name in self.container.modules:
            if hasattr(self.container.modules[mod_name], 'load'): 
                handler.beginGroup(mod_name)
                self.container.modules[mod_name].load(file_handler = handler)
                #except: print "Failed to load data for " + mod_name
                handler.endGroup()


    

