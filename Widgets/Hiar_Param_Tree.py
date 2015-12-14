# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

"""
import pyqtgraph.parametertree.parameterTypes as _pTypes
import pyqtgraph.parametertree as _pTree
from pyqtgraph.parametertree.Parameter import *
from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

from A_Lab.Others.Hiar_Storage import Hiar_Storage
from A_Lab.Others.File_Handler import File_Handler

class Hiar_Param_Tree(_pTree.ParameterTree):
    """
    This wraps the PyQtGraph ParameterTree Widget and adds some usefull 
    function to make it work transparently with the Hiar_Storage class.

    No support for list or dict...
    @TODO: If I ever need it, add support for list and/or dict
    """
    
    def __init__(self, file_handler = None):
        _pTree.ParameterTree.__init__(self,  parent=None, showHeader=False)
        self.root = _pTypes.GroupParameter(name = 'root')
        self.addParameters(self.root, showTop=False)
        
        if file_handler is not None:
            self.init_tree(file_handler)
        
    def init_tree(self, file_handler):
        """
        Puts in the initial values in the tree
        """
        #Define a sub function to allow recursive calls
        def _buildTree(file_handler, parent):
            headers_struct = file_handler.getHeaders()
            for key in headers_struct:
                # Get the options / or the group item
                opts = headers_struct[key]

                #Add the value if it is a leaf node
                if not headers_struct.isItemGroup(opts): 
                    # If the item arleady exist
                    if key in [str(x.name()) for x in parent.children()]:
                        parent.child(key).setOpts(**opts)
                    else:
                        # Create and add the Parameter
                        param = Parameter.create(**opts)
                        parent.addChild(param)

                #Recursivelly add the sub_groups otherwise
                else:
                    if not key in [str(x.name()) for x in parent.children()]:
                        new_parent = _pTypes.GroupParameter(name=key)
                        parent.addChild(new_parent)
                    else:
                        new_parent = parent.child(key)
                    file_handler.beginGroup(key)
                    _buildTree(file_handler, new_parent)
                    file_handler.endGroup()
                    
        #Call the recusrsive function and init the values
        _buildTree(file_handler, self.root)

    def genFileHandler(self):
        """
        This generates a file_handler Object representing all the values in the Tree
        """
        def _genHiarStorage(file_handler, cur_item):
            for item in cur_item.children():
                if type(item) == _pTypes.GroupParameter:
                    file_handler.beginGroup(item.name())
                    _genHiarStorage(file_handler, item)
                    file_handler.endGroup()
                else:
                    file_handler.getHeaders()[item.name()] = item.opts


        fh = File_Handler()
        _genHiarStorage(fh, self.root)
        return fh

    def addParam(self, path, value, **opts):
        """
        Add a simple parametter
        """
        # Create a new file_handler
        fh = File_Handler()
        h = fh.getHeaders()

        # Add the new param to the handler
        h[path] = opts
        name = h.getHiarList(path)[-1]
        h[path]['name'] = name
        h[path]['value'] = value

        if not 'type' in opts:
            # Take a guess
            h[path]['type'] = str(type(value).__name__)
        

        # Do an init tree with a file handler with single param (kind of
        # inefficient, but makes the code clearer I think)
        self.init_tree(fh)

    # def addListParam(self, path, values, **opts):


    def __setitem__(self, key, value):
        self.addParam(key, value = value)

    def __getitem__(self, key):
        hiar_list = key.split('/')
        while '' in hiar_list: hiar_list.remove('')
        current_node = self.root
        for item in hiar_list:
            current_node = current_node.child(item)
        return current_node



# @TODO: Re-write the save and load function
    def save(self, file_handler = None):
        """
        This saves the values of the Hiar_Storage structure <content> in the current
        group.

        Note, this is slightly different than a merge which would merge
        all from root.
        """
        # Check that a file_hanlder was received
        if file_handler == None or not isinstance(file_handler,File_Handler):
            print("Failed to save the Parametter_Tree since no File_Handler was passed to the save() method")

        # Generate a file_handler from the tree
        fh = self.genFileHandler()

        # Begin a group that specified that the data that follows is from a Hiar_Parm_Tree
        file_handler.beginGroup('::Hiar_Param_Tree')

        # This creates an absolute path adressed flat content dict for the 
        # Hiar_Storage out of the relative paths taken from the headers
        rel_flat_content = fh.getHeaders().flatten()
        abs_flat_content = {}
        for rel_path in rel_flat_content:
            abs_flat_content[file_handler.getHeaders().prefix + rel_path[1:]] = rel_flat_content[rel_path]
        file_handler.addHeaders(**abs_flat_content)

        # Do the same for the data
        # Note that there is currently nothing being stored in the data, so 
        # this is curently useless...  I keep it here in case I do want to put
        # put some data in at some point.
        rel_flat_content = fh.getData().flatten()
        abs_flat_content = {}
        for rel_path in rel_flat_content:
            abs_flat_content[file_handler.getData().prefix + rel_path[1:]] = rel_flat_content[rel_path]
        file_handler.addData(**abs_flat_content)

        # End ::Hiar_Param_Tree the group
        file_handler.endGroup()



    def load(self, file_handler = None):
        """
        Loads the values from the file_handler headers to the content variable
        """
        # Check that a file_hanlder was received
        if file_handler == None:
            print("Failed to load the Parametter_Tree since no File_Handler was passed to the load() method")
            return

        file_handler.beginGroup('::Hiar_Param_Tree')
        self.init_tree(file_handler)
        file_handler.endGroup()



#------------------------------------------------------------------------------
#       @TODO: Add a parameter item class for dicts
#------------------------------------------------------------------------------

# class ListParameter_Extended(_pTypes.ListParameter):
#     """
#     This expand the ListParameter class and add some functionalities.

#     Namelly:
#         - The ability clear and reset all the elements at the same time.
#         - The ability to simply add the missing elements.

#     """
#     def __init__(self, **opts):
#         _pTypes.ListParameter.__init__(self, **opts)

#     def replaceValues(self, values):
#         """
#         Replace the entire list with the <values> list
#         """
#         values = map(str,values)
#         widget = self.items.items()[0][0].widget
#         widget.clear()
#         widget.addItems(values)

#     def addMissingValues(self, values):
#         """
#         Add the missing element in values to the list
#         """
#         values = map(str,values)
#         widget = self.items.items()[0][0].widget
#         current_values = self.values()
#         for element in values:
#             if not element in current_values:
#                 widget.addItem(element)

#     def values(self):
#         """
#         Returns the complete list of values
#         """
#         widget = self.items.items()[0][0].widget
#         ans = [str(widget.itemText(i)) for i in range(widget.count())]
#         return ans

#     def __contains__(self, text):
#         text = str(text)
#         return text in self.values()

# registerParameterType('list', ListParameter_Extended, override=True) 