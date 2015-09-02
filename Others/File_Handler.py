# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

This module contains the base class for all other File_Handler and the 
Hiar_Storage class which it uses to handle headers.
"""
import numpy as _np
from Generic_UI.Others.Hiar_Storage import *


class File_Handler():
    format_name = 'Supported Format'
    def __init__(self, default_filename = None):
        self.filename = default_filename
        self.data = Hiar_Storage()
        self.headers = Hiar_Storage()
        
    def mergeHandler(self, handler):
        """
        This merges another handler's data and headers with the current handler.
        
        If there a key conflict the new supplied handler will have priority.
        (ie it will overwrite the self entries with it's own values)
        """
        self.data = self.data.merge(self.data, handler.data)
        self.headers = self.headers.merge(self.headers, handler.headers)
    
#------------------------------------------------------------------------------ 
# These two functions should be implemented by all sub_classes of the File_Handler
# to deal with the specifics of how to save and load data to file
    def load(self, **kw):
        raise NotImplemented
        
    def save(self, **kw):
        raise NotImplemented
#------------------------------------------------------------------------------    
        
    def _load_complete(self, new_data, new_headers, loadMerge = True, **kw):
        """
        Add some common functionalities to load (eg loadMerge).
        
        This should thus always be called at the end of any sub-classes load
        functions with new_data and new_headers being the Hiar_Storage instance
        containing the loaded values
        """
        if loadMerge:
            self.data.merge(self.data, new_data)
            self.headers.merge(self.headers, new_headers)
        else:
            self.data = new_data
            self.headers = new_headers


    def beginGroup(self, groupName):
        """
        Enter a new group. Make sure to always pair a beginGroup with an endGroup
        """
        self.data.beginGroup(groupName)
        self.headers.beginGroup(groupName)
           
    def endGroup(self):
        """
        Exit one group level. Make sure to always pair a beginGroup with an endGroup
        """
        self.data.endGroup()
        self.headers.endGroup()
        
    def addData(self, **kwargs):
        """
        Simple way to add data to the structure.
        
        To use this function, you can simply do:
            Hiar_Storage.add(name1 = value1, name2 = value2)
            
        Values will be stored in the current group.
        """
        self.data.add(**kwargs)
        
    def addHeaders(self, **kwargs):
        """
        Simple way to add data to the structure.
        
        To use this function, you can simply do:
            Hiar_Storage.add(name1 = value1, name2 = value2)
            
        Values will be stored in the current group.
        """
        self.headers.add(**kwargs)
        
    def getData(self):
        """
        Returns the Hiar_Storage structure containing the data
        
        This can be use to either access curently stored headers, or modify
        them.
        
        All File_Handler sub_class must have support for at least 1D array and 
        2D arrays.  For other data type please check individual file handler, 
        to see what's supported.
        """
        return self.data
        
    def getHeaders(self):
        """
        Returns the Hiar_Storage structure containing the headers.
        
        This can be use to either access curently stored headers, or modify
        them.
        
        For more info, on how the structure can be used, refer to the Hiar_Storage
        class.
        
        For more info on what header types are allowed, refers to the File_Handler
        sub-class documentation.        
        """
        return self.headers
        
    def __str__(self):
#        tab = ' '*3
        s = 'File_Handler for ' + str(self.filename)
        s += '\nData:'
        s += str(self.data)
#        for group in self.data:
#            s += '\n=> ' +  group
#            for data_entry in self.data[group]:
#                s += '\n' + 2*tab + data_entry + ': shape = ' + str(self.data[group][data_entry].shape)
        s += '\nHeaders:'
        s += str(self.headers)
        return s
        
        
if __name__=='__main__':
    #For debuggin purposes only
    a = File_Handler('')
    x = _np.linspace(0,100)
    y = _np.cos(x)
    a.addData(x=x, y=y)
    h = a.getHeaders()
    
    a.beginGroup('g1')
    a.addHeaders(v1='hey', v2=1)
    a.beginGroup('g1.1')
    a.addHeaders(g1_1= ['a','b','c'])
    a.endGroup()
    a.endGroup()
    h['v0']= 132
    a.beginGroup('g2')
    h['asfdg'] = 'asfdg'
    a.endGroup()
    h['/g3/g3.1/gAlex/vHey'] = 'hey'
    
    #For debuggin purposes only
    b = File_Handler('')
    x = _np.linspace(0,100)
    y = _np.sin(x)
    y2 = _np.log(x+1)
    b.addData(y2=y2, y=y)
    h = b.getHeaders()
    
    b.beginGroup('g1')
    b.addData(x=x)
    b.addHeaders(v1='not_hey', v2=1)
    h.beginGroup('g1.1')
    b.addHeaders(g1_1= ['a','w','c'])
    b.endGroup()
    b.endGroup()
    h['v0']= 132
    b.beginGroup('g2')
    h['new_one'] = 23
    b.endGroup()
    h['/g3/g3.1/gAlex/vHey'] = 'hey'
    

