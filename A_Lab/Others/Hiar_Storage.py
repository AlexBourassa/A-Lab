# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

"""

import numpy as _np
from PyQt4 import QtCore as _core

class Hiar_Storage(_core.QObject):
    """
    This is a hiarchical storage for headers.  It is a very convient class to
    load and save data, but it is not optimized for performance... Might be
    slow...  But in most cases that doesn't matter.  (these operation happen
    only once...)
    """    
    # Signals when element is added or removed (parameters are the absolute
    # path of the item and the value itself)
    signal_value_added = _core.Signal(str, object)
    signal_value_removed = _core.Signal(str, object)#Not currently used...
    
    
    def __init__(self):
        #_core.QObject.__init__(self)
        super(Hiar_Storage, self).__init__()
        self.content = Hiar_Group()
        self.blockSignal = False
        self.prefix = '/'#Using UNIX convention, absolute path start with /

        
    def findAll(self, key):
        """
        Find all instances of <key> in the tree.  Return a dict of the absolute
        path with their item values (either a group or a value)
        """
        flatten_dict = self.flatten()
        path_array = _np.array(list(flatten_dict.keys()))
        possible_index = _np.array([key in path for path in path_array])
        ans = dict()
        for possible_path in path_array[possible_index]:
            #If it is the full name of a group it is between 2 '/'
            if '/' + key + '/' in possible_path:
                group_path = possible_path.split('/'+key+'/')[0] + '/' + key
                ans[group_path] = self[group_path]
            #If it is the full name of a value it terminates the path
            elif possible_path.endswith('/' + key): 
                ans[possible_path] = flatten_dict[possible_path]
        return ans
        
    def flatten(self):
        """
        Returns a single 1D dictionary of the full path associated with their
        item.
        """
        #Define a sub function to allow recursive calls
        def _flatten(storage_struct, flatten_dict, prefix):
            for key in storage_struct:
                #Add the value if it is a leaf node
                if not self.isItemGroup(storage_struct[key]): flatten_dict[prefix+key] = storage_struct[key]
                #Recursivelly scan the sub_groups otherwise
                else: 
                    flatten_dict = _flatten(storage_struct[key], flatten_dict, prefix + key + '/')
            return flatten_dict
            
        #Call the recursive function
        return _flatten(self, dict(), '/')
    
    def merge(self, new, old = None):
        """
        This merges another hiar_storage's with the current structure.
        
        If there a key conflict the new supplied storage will have priority.
        (ie it will overwrite the self entries with it's own values)
        """
        if old == None:
            old = self
        for value in new:
            #Substitute the values
            if not self.isItemGroup(new[value]): old[value] = new[value]
            #Recursivelly scan the sub_groups
            else: 
                if value in old: old[value] = self.merge(new[value], old[value])
                else: old[value] = new[value]
        return old

    def copy(self):
        """
        Builds a deep copy of the Hiar_Storage
        """
        ans = Hiar_Storage()
        ans.merge(self)
        return ans
        
    def beginGroup(self, groupName):
        """
        Enter a new group.  Make sure to always pair a beginGroup with an endGroup.
        """
        self.prefix += groupName + '/'
        
    def resetToRoot(self):
        """
        This method reset the path or group to root ('/').
        
        This is equivalent to closing all groups that have been openned
        """
        self.prefix = '/'#Using UNIX convention, absolute path start with /
        
    def add(self, **kwargs):
        """
        Simple way to add data to the structure.
        
        To use this function, you can simply do:
            Hiar_Storage.add(name1 = value1, name2 = value2)
            
        Values will be stored in the current group.
        """
        for k in kwargs:
            self[k] = kwargs[k]
        
    def endGroup(self):
        """
        Exit one group level.  Make sure to always pair a beginGroup with an endGroup.
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
        else: return self.prefix + str(key)
        
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
        if item == None: item = self[self.prefix]
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
        # TODO: Optimize for relative path using (eg by using a self.current_item
        # variable.
        
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
        
        #Triggered the add signal
        if not self.blockSignal:
            self.signal_value_added.emit(self.getPath(key), value)
        
        
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