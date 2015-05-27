# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

"""
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import *

from Others import Hiar_Storage

class Hiar_Param_Tree(ParameterTree):
    
    def __init__(self):
        ParameterTree.ParameterTree.__init__(self,  parent=None, showHeader=False)
        
        # This structure should be used to add and remove parametters
        self.content = Hiar_Storage() 
        
    def init_tree(self):
        """
        Puts in the initial values in the tree and link the add remove signals
        """
        #Define a sub function to allow recursive calls
        def _buildTree(storage_struct, parent):
            for key in storage_struct:
                #Add the value if it is a leaf node
                if not self.isItemGroup(storage_struct[key]): parent
                #Recursivelly scan the sub_groups otherwise
                else: 
                    _buildTree(storage_struct[key], self)
