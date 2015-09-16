# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

"""
import pyqtgraph.parametertree.parameterTypes as _pTypes
import pyqtgraph.parametertree as _pTree
from pyqtgraph.parametertree.Parameter import *
from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

from Generic_UI.Others.Hiar_Storage import Hiar_Storage
from Generic_UI.Others.File_Handler import File_Handler

class Hiar_Param_Tree(_pTree.ParameterTree):
    """
    This wraps the PyQtGraph ParameterTree Widget and adds some usefull 
    function to make it work transparently with the Hiar_Storage class.

    Some support for list (no dict), but it's not ready for prime time...
    @TODO: If I ever need it, add support for list and/or dict
    """
    
    def __init__(self, hiar_storage = None):
        _pTree.ParameterTree.__init__(self,  parent=None, showHeader=False)
        
        # This structure should be used to add and remove parametters
        if hiar_storage == None: self.content = Hiar_Storage() 
        else: self.content = hiar_storage
        
        self.init_tree()
        
    def init_tree(self):
        """
        Puts in the initial values in the tree and link the add remove signals
        """
        #Define a sub function to allow recursive calls
        def _buildTree(storage_struct, parent):
            for key in storage_struct:
                item = storage_struct[key]
                #Add the value if it is a leaf node
                if not self.content.isItemGroup(item): 
                    self._low_addParam(key, item)
                #Recursivelly add the sub_groups otherwise
                else: 
                    new_parent = _pTypes.GroupParameter(name=key)
                    parent.addChild(new_parent)
                    _buildTree(item, new_parent)
                    
        #Call the recusrsive function and init the values
        self.root = _pTypes.GroupParameter(name = 'root')
        self.addParameters(self.root, showTop=False)
        _buildTree(self.content, self.root)
        
        #Connects the signal trigerring an add of a new value
        self.content.signal_value_added.connect(lambda path, value: self._addParam(path))

    def _low_addParam(self, key, item):
        # To avoid repeating code... This should never be called directly
        if type(item) == list or type(item) == dict:
            param = Parameter.create(name=key, type=type(item).__name__, values=item)
        else: 
            param = Parameter.create(name=key, type=type(item).__name__, value=item)
            def blockedSet(storage, path, value_fct):
                storage.blockSignal = True
                storage[path] = value_fct()
                storage.blockSignal = False
            param.sigChanged.connect(lambda: blockedSet(self.content, self.content.getPath(key), param.value))
        parent.addChild(param)

        #@TODO: Implement _removeParam and link to signal
    def _addParam(self, path):
        """
        This is meant to be called by a signal_value_added from the Hiar_Storage
        with which the Hiar_Param is associated.
        """
        hiar_list = self.content.getHiarList(path)
        value = hiar_list.pop(-1) #Special Treatement for the last one
        
        # Find the final group and create all necessary groups along the way
        current_param = self.root
        for group in hiar_list:
            #If the group doesn't exists in the current item, create it
            if not group in map(lambda x: x.name(), current_param.children()):
                current_param.addChild(_pTypes.GroupParameter(name=group))
            current_param = current_param.child(group)

        # Check if the parametter is already in the tree
        v_key = value
        v_data = self.content[path]
        if value in map(lambda x: str(x.name()),current_param.children()):
            if type(v_data) == list or type(v_data) == dict:
                current_param.child(v_key).addMissingValues(v_data)
            else: 
                current_param.child(v_key).setValue(v_data)
            return

        # Add the value to the group
        self._low_addParam(v_key, v_data)

    def save(self, file_handler = None):
        """
        This saves the values of the Hiar_Storage structure <content> in the current
        group.

        Note, this is slightly different than a merge which would merge
        all from root.
        """
        # Check that a file_hanlder was received
        if file_handler == None or type(file_handler)!=File_Handler:
            print "Failed to save the Parametter_Tree since no File_Handler was passed to the save() method"

        # This creates a absolute path adressed flat content dict for the 
        # Hiar_Storage out of the relative paths taken from self.content
        rel_flat_content = self.content.flatten()
        abs_flat_content = {}
        for rel_path in rel_flat_content:
            abs_flat_content[file_handler.getHeaders().prefix + rel_path[1:]] = rel_flat_content[rel_path]
        file_handler.addHeaders(**abs_flat_content)

    def load(self, file_handler = None):
        """
        Loads the values from the file_handler headers to the content variable
        """
        # Check that a file_hanlder was received
        if file_handler == None or type(file_handler)!=File_Handler:
            print "Failed to load the Parametter_Tree since no File_Handler was passed to the load() method"

        def _load(h):
            groups, values = h.listGroupsAndValues()
            for g in groups:
                h.beginGroup(g)
                self.content.beginGroup(g)
                _load(h)
                self.content.endGroup()
                h.endGroup()
            for v in values:
                self.content[v] = h[v]
        self.content.resetToRoot()
        _load(file_handler.getHeaders())


#------------------------------------------------------------------------------
#       @TODO: Add a parameter item class for dicts
#------------------------------------------------------------------------------

class ListParameter_Extended(_pTypes.ListParameter):
    """
    This expand the ListParameter class and add some functionalities.

    Namelly:
        - The ability clear and reset all the elements at the same time.
        - The ability to simply add the missing elements.

    """
    def __init__(self, **opts):
        _pTypes.ListParameter.__init__(self, **opts)

    def replaceValues(self, values):
        """
        Replace the entire list with the <values> list
        """
        values = map(str,values)
        widget = self.items.items()[0][0].widget
        widget.clear()
        widget.addItems(values)

    def addMissingValues(self, values):
        """
        Add the missing element in values to the list
        """
        values = map(str,values)
        widget = self.items.items()[0][0].widget
        current_values = self.values()
        for element in values:
            if not element in current_values:
                widget.addItem(element)

    def values(self):
        """
        Returns the complete list of values
        """
        widget = self.items.items()[0][0].widget
        ans = [str(widget.itemText(i)) for i in range(widget.count())]
        return ans

    def __contains__(self, text):
        text = str(text)
        return text in self.values()

registerParameterType('list', ListParameter_Extended, override=True) 