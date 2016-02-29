# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

This module handles save/load
"""
from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core
import numpy as _np

class Load_Save_Widget(_gui.QWidget):
    def __init__(self, parent=None, **kwargs):
        _gui.QWidget.__init__(self, parent=parent)


class File_Handler():
    def __init__(self, filename):
        self.filename = filename
        self.data = dict()
        self.headers = Hiar_Storage()
        
    def load(self):
        raise NotImplemented
        
        
    def addData(self, groupName='default', **kwData):
        """
        Adds data to <groupName> group.  Data entry will be given the name by
        which they are specified in the kwData dictionary.
        
        To add data, simply use:
            file_handler.addData('myGroup', x=myXdata, y1=myYdata1, other_y=myYdata2)
                where myXdata, myYdata1, myYdata2 are the arrays you want to store
        
        All File_Handler sub_class must have support for at least 1D array and 
        2D arrays.  For other data type please check individual file handler, 
        to see what's supported.
        """
        if not groupName in self.data: self.data[groupName] = dict()
        for k in kwData:
            self.data[groupName][k] = _np.array(kwData[k])
        
    def getHeaders(self):
        """
        Returns the Hiar_Storage structure containing the headers.
        
        This can be use to either access curently stored headers, or modify
        them.
        
        For more info, on how the structure can be used, refer to the Hiar_Storage
        class.
        """
        return self.headers
        
    def save(self):
        raise NotImplemented
        
    def __str__(self):
        tab = ' '*3
        s = 'File_Handler for ' + self.filename
        s += '\nData:'
        for group in self.data:
            s += '\n=> ' +  group
            for data_entry in self.data[group]:
                s += '\n' + 2*tab + data_entry + ': shape = ' + str(self.data[group][data_entry].shape)
        s += '\nHeaders:'
        s += '\n=>TODO...'
        return s
        
        
class Pickle_Handler(File_Handler):
    def __init__(self, filename):
        super(Pickle_Handler, self).__init__(self, filename)
        
    
class Hiar_Storage():
    """
    This is a hiarchical storage for headers.  It is a very convient class to
    load and save data, but it is not optimized for performance... Might be
    slow...  But in most cases that doesn't matter.  (these operation happen
    only once...)
    """    
    
    def __init__(self):
        self.content = Hiar_Group()
        self.prefix = '/'#Using UNIX convention, absolute path start with /
        
    def beginGroup(self, groupName):
        """
        Enter a new group.
        """
        self.prefix += groupName + '/'
        
        
    def endGroup(self):
        """
        Exit one group level.
        """
        hiar_list = self.getHiarList(self.prefix)
        if len(hiar_list)==0: return
        hiar_list.pop(-1)#Remove the last element
        self.prefix = '/'
        for s in hiar_list: self.prefix += s +'/'
        
    def getPath(self, key):
        """
        Get the absolute path, from either a relative path or a direct absolute path
        """
        if key[0] == '/': return key
        else: return self.prefix + key
        
    def getHiarList(self, key):
        """
        Returns a list of nodes name to traversre in order to reach <key>
        """
        hiar_list = self.getPath(key).split('/')
        while '' in hiar_list: hiar_list.remove('')
        return hiar_list
        
    def isPathGroup(self, key):
        """
        Return True if the item at path <key> is a group
        """
        return type(self[key]) == Hiar_Group
        
    def isItemGroup(self, item):
        return type(item) == Hiar_Group
        
    def getCurrentNode(self):
        """
        Returns the current node 
        """
        return self[self.prefix]
        
    def listGroupsAndValues(self, item=None):
        """
        Generate a list of groups and values at item.  For item==None, lists
        groups and values from the current node.
        
        Return format is:
            return group_list, value_list
        
        Raises an Exception if the specified node is a value node
        """
        current_node = item
        if not self.isItemGroup(current_node): raise Exception("Cannot search a value node for subgroups")
        ans_groups = list()
        ans_values = list()
        for item in current_node:
            if self.isItemGroup(current_node[item]): ans_groups.append(item)
            else: ans_values.append(item)
        return ans_groups, ans_values
    
        
    def __contains__(self, key):
        """
        Check if a key is contained in the content dictionary, returns true
        """
        hiar_list = self.getHiarList(key)
        
        current_node = self.content
        for current_key in hiar_list:
            if current_key in current_node: current_node=current_node[current_key]
            else: return False
        return True
        
    def __getitem__(self, key):
        """
        Gets part of the content dictonary.  If the key doesn't exist raises KeyError
        """        
        #Get the groups
        hiar_list = self.getHiarList(key)
        
        #Get the value in the content dict
        current_node = self.content
        for current_key in hiar_list: current_node = current_node[current_key]
        return current_node
         
    def __setitem__(self, key, value):
        """
        Set a new item.  If the item already exist it will be overwritten
        """
        #Get the groups
        hiar_list = self.getHiarList(key)
        last_key = hiar_list.pop(-1)#Special treatement for last key
        
        #Add all previous keys if they exists
        current_node = self.content
        for current_key in hiar_list:
            if not current_key in current_node: current_node[current_key] = Hiar_Group()
            current_node = current_node[current_key]
            
        #Set the final value
        current_node[last_key] = value
        
    def __str__(self, item=None, prefix_to_line=''):
        """
        Generate a str of the sub tree starting at node item.
        
        If item == None, generate a tree of the full tree.
        
        <prefix_to_line> is there mainly for recursion purposes
        """
        if item==None: item = self['/']
        if not self.isItemGroup(item): return '\n' + prefix_to_line + str(item)
        groups, values = self.listGroupsAndValues(item=item)
        s = ''
        for v in values: s += '\n' + prefix_to_line + v + ' = ' + str(item[v])
        for g in groups: 
            s += '\n' + prefix_to_line + '=>' + g
            s += self.__str__(item=item[g], prefix_to_line=prefix_to_line+' '*3)
        return s
        
    def __iter__(self):
        ans = self[self.prefix]
        return iter(ans)
        
 
# This allows for differentiation between dictionaries and groups in Hiar_Storage   
class Hiar_Group(dict):
    pass
        
        
if __name__=='__main__':
    #For debuggin purposes only
    a = File_Handler('')
    x = _np.linspace(0,100)
    y = _np.cos(x)
    a.addData(x=x, y=y)
    h = a.getHeaders()
    
    h.beginGroup('g1')
    h['v1'] = 'hey'
    h['v2'] = 1
    h.beginGroup('g1.1')
    h['v1.1'] = ['a','b','c']
    h.endGroup()
    h.endGroup()
    h['v0']= 132
    h.beginGroup('g2')
    h['asfdg'] = 'asfdg'
    h.endGroup()
    h['/g3/g3.1/gAlex/vHey'] = 'hey'
    
        
    
            
        
