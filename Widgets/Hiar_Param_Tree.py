# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

"""
import pyqtgraph.parametertree.parameterTypes as _pTypes
import pyqtgraph.parametertree as _pTree
from pyqtgraph.parametertree.Parameter import *
from PyQt4 import QtGui as _gui

from Generic_UI.Others.Hiar_Storage import Hiar_Storage

class Hiar_Param_Tree(_pTree.ParameterTree):
    
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
                    if type(item) == list or type(item) == dict: 
                        parent.addChild(Parameter.create(name=key, type=type(item).__name__, values=item))
                    else: 
                        parent.addChild(Parameter.create(name=key, type=type(item).__name__, value=item))
                #Recursivelly add the sub_groups otherwise
                else: 
                    new_parent = _pTypes.GroupParameter(name=key)
                    parent.addChild(new_parent)
                    _buildTree(item, new_parent)
                    
        #Call the recusrsive function and init the values
        root = _pTypes.GroupParameter(name = 'root')
        self.addParameters(root, showTop=False)
        _buildTree(self.content, root)
        
        #TODO: Add signals
        #self.content.signal_value_added.connect(self._addParam)
        #self
        
    def _addParam(self, path, value):
        hiar_list = self.content.getHiarList(path)
        value = hiar_list.pop(-1) #Special Treatement for the last one
        
        # Find the final group and create all necessary groups along the way
        current_param = self.child('root')
        for group in hiar_list:
            #If the group doesn't exists in the current item, create it
            if not group in map(lambda x: x.name, current_param.children()):
                current_param.addChild()
                
            
#class List_Parameter_item(_pTypes.WidgetParameterItem):
#    def makeWidget(self):
#        """
#        Return a single widget that should be placed in the second tree column.
#        The widget must be given three attributes:
#        
#        ==========  ============================================================
#        sigChanged  a signal that is emitted when the widget's value is changed
#        value       a function that returns the value
#        setValue    a function that sets the value
#        ==========  ============================================================
#            
#        This is a good function to override in subclasses.
#        """
#        opts = self.param.opts
#        if opts['type'] != 'list' or type(opts['value'])!=list: 
#            raise Exception("This class must be used with a list type value (and a type='list')")
#        w = _gui.QComboBox()
#        
#        str_list = map(str, opts['value'])
#
#        w.addItems(str_list)
#
#        w.value = lambda: str(w.currentText())
#        w.sigChanged = w.currentIndexChanged
#        w.setValue = lambda x: w.setCurrentIndex(str_list.index(str(x)))
#        return w
#
#class ListParameter(Parameter):
#    itemClass = List_Parameter_item
#    
#registerParameterType('list', ListParameter, override=True) 