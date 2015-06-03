# -*- coding: utf-8 -*-
"""
This modules has some subclasses of the File_Handler which can deal with
different file formats.

Supported file formats are:
    1. Python Pickle

@author: Alex
"""
from File_Handler import File_Handler
import pickle as _p


def getFileFormatDict():
    return {'*.pck': Pickle_Handler}


class Pickle_Handler(File_Handler):
    """
    This File_Handler create a pickle file which serializes the python objects
    data and headers.  If you are only using Python for extracting the data,
    this is by far the easiest format to use!

    This technique should support pretty much all object types.
    """
    format_name = 'Pickled Files'
#    def __init__(self, filename):
#        super(Pickle_Handler, self).__init__(self, filename)

    def save(self, filename = None):
        """
        Saves the File_Handler Hiar_Storage structures in file <filename>.
        If <filename> is not specified uses the default Handlers filename.
        If the default filename is also not specified, raises an Exception.
        """
        if filename is None: filename = self.filename
        if filename is None: raise Exception("No filename specified")
        with open(filename, 'w') as f:
            _p.dump([self.data, self.headers], f)

    def load(self, filename = None, **kw):
        """
        Loads the File_Handler Hiar_Storage structures from file <filename>.
        If <filename> is not specified uses the default Handlers filename.
        If the default filename is also not specified, raises an Exception.

        If <loadMerge> == True, add the new data to the existing structures
        Else, overwrite the existing structures to replace them with the new data.
            (Values from the new filenae have priority)
        """
        if filename == None: filename = self.filename
        if filename == None: raise Exception("No filename specified")
        with open(filename, 'r') as f:
            ans = _p.load(f)
        # Make sure to call this one at the end of any load functions for
        # sub-class of File_Handler.  This will add some common functions like
        # loadMerge.
        self._load_complete(ans[0], ans[1], **kw) 
        