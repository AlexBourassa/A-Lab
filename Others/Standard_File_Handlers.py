# -*- coding: utf-8 -*-
"""
This modules has some subclasses of the File_Handler which can deal with
different file formats.

Supported file formats are:
    1. Python Pickle

@author: Alex
"""
from A_Lab.Others.File_Handler import File_Handler
import pickle as _p
import json as _json
import numpy as _np
from A_Lab.Others.Hiar_Storage import *


def getFileFormatDict():
    return {'*.json':JSON_Handler} # '*.pck': Pickle_Handler


class Pickle_Handler(File_Handler):
    """
    This File_Handler create a pickle file which serializes the python objects
    data and headers.  If you are only using Python for extracting the data,
    this is by far the easiest format to use!

    This technique should support pretty much all object types.

    However it is not a time proof solution (ie if the pickle code changes data might be unreadable)
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
            #Store the content only since the full object QObject cannot be dumped
            _p.dump([self.data.content, self.headers.content], f)

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

        # Convert the info in the ans in a Hiar_Storage format
        hs_data = Hiar_Storage()
        hs_headers = Hiar_Storage()

        # Replace the content
        hs_data.content = ans[0]
        hs_headers.content = ans[1]

        # Make sure to call this one at the end of any load functions for
        # sub-class of File_Handler.  This will add some common functions like
        # loadMerge.
        self._load_complete(hs_data, hs_headers, **kw) 
        


class JSON_Handler(File_Handler):
    """
    This File Handler will attempt to save the Hiar_Storage structures in a
    standard JSON format.

    This currently support the following data types:

    This uses the following special keywords:
        - @numpy!
        - @dict!
    """
    format_name = 'JSON'

    def save(self, filename = None):
        """
        Saves the File_Handler Hiar_Storage structures in file <filename>.
        If <filename> is not specified uses the default Handlers filename.
        If the default filename is also not specified, raises an Exception.
        """
        if filename is None: filename = self.filename
        if filename is None: raise Exception("No filename specified")

        # Copy the structure to make the modification only on copies
        temp_fh = self.copy()
        temp_fh.data = self._encode_to_JSON(temp_fh.data)
        temp_fh.headers = self._encode_to_JSON(temp_fh.headers)

        # Save to JSON
        with open(filename, 'w') as f:
            _json.dump([temp_fh.data.content, temp_fh.headers.content], f)

    def load(self, filename = None, py27=False, **kw):
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
            ans = _json.load(f)

        # @py27 This is no longer usefull in Python 3, but should be used in Python 2
        if py27:
            ans = self._byteify(ans)


        # Make sure to call this one at the end of any load functions for
        # sub-class of File_Handler.  This will add some common functions like
        # loadMerge.
        self._load_complete(self._decode_from_JSON(ans[0]),
                            self._decode_from_JSON(ans[1]),
                            **kw)

    def _encode_to_JSON(self, hs):
        """
        Input a Hiar_Storage and this function will change:
            - Numpy array to an array list (and store them as {'@numpy!':array})
            - Dict to {'@dict!':dict}
        """
        hs_dict = hs.flatten()

        for key in hs_dict:
            if type(hs_dict[key])==_np.ndarray:
                hs[key] = {"@numpy!":hs[key].tolist()}
            elif type(hs_dict[key])==dict:
                hs[key] = {"@dict!":hs[key]}

        return hs

    def _decode_from_JSON(self, full_d):
        """
        Input a dict to this function and it will decode it back to a Hiar_Storage.  This function supports:
            - Numpy array (encoded as {'@numpy!':array})
            - Dict (encoded as {'@dict!':dict})
        """
        def _recurs_decode(d):
            # Decode special types
            if '@dict!' in d:
                return d['@dict!']
            elif '@numpy!' in d:
                return _np.array(d['@numpy!'])

            # Decode standard types (int, float, string, list) and recusivelly
            # decode the dictionary into Hiar_Group
            for key in d:
                if type(d[key])==dict:
                    # If we get a dict, transform it into Hiar_Group
                    d[key] = _recurs_decode(Hiar_Group(d[key]))
                else:
                    # Else just return the value and hope it is one of the standard ones (int, float, string, list)
                    d[key] = d[key]
                    # This else is utterly useless, but explains the logic

            return d

        ans = _recurs_decode(full_d)
        return ans

    def _byteify(self, input):
        """
        This functions should be called on the results of _json.load().

        This ensure that unicode str are converted to Python str type

        This was used in the Python 2.7 version of this code, but in Python 3,
        string handling has changed making this irrelevant (ie this is 
        )
        """
        if isinstance(input, dict):
            return {self._byteify(key):self._byteify(value) for key,value in list(input.items())}
        elif isinstance(input, list):
            return [self._byteify(element) for element in input]
        elif isinstance(input, str):
            return input.encode('utf-8')
        elif isinstance(input, bytes):
            return input.decode('utf-8')
        else:
            return input


if __name__=='__main__':
    #For debuggin purposes only
    a = JSON_Handler('test.json')
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

    x = _np.linspace(0,100)
    y = _np.sin(x)
    y2 = _np.log(x+1)
    a.addData(y2=y2, y=y)
    h = a.getHeaders()
    
    a.beginGroup('g1')
    a.addData(x=x)
    a.addHeaders(v1='not_hey', v2=1)
    h.beginGroup('g1.1')
    a.addHeaders(g1_1= ['a','w','c'])
    a.endGroup()
    a.endGroup()
    h['v0']= 132
    a.beginGroup('g2')
    h['new_one'] = 23
    a.endGroup()
    h['/g3/g3.1/gAlex/vHey'] = 'hey'
    