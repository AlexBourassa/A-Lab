# -*- coding: utf-8 -*-
"""
@author: Alex
"""

import numpy as _np
from PyQt4 import QtCore as _core

class GraphTrace(_core.QObject):
    """
    This class represents a Trace and the possible attributes it can contain
    """
    newData = _core.Signal(str)    
    
    def __init__(self, name, *args, **kwargs):
        _core.QObject.__init__(self)
        if 'name' in kwargs:
            kwargs.pop('name')
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.xData = None
        self.yData = None
        if 'y' in kwargs:
            self.yData = _np.array(kwargs.pop('y'))
            if 'x' in kwargs:
                self.xData = _np.array(kwargs.pop('x'))
            else:
                self.xData = _np.linspace(0, len(self.yData)-1, num=len(self.yData))
            self.newData.emit(self.name)
        
    def setData(self, x, y):
        self.xData = _np.array(x)
        self.yData = _np.array(y)
        self.newData.emit(self.name)
        
        
    def getData(self, transformed=True):
        if transformed and not (self.xData==None or self.yData==None):
            x,y = self.transform(self.xData, self.yData)
        else:
            x,y = self.xData, self.yData
        return x, y
        
    def transform(self, x, y):
        return x,y