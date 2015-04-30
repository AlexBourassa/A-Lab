# -*- coding: utf-8 -*-
"""
@author: Alex
"""

import numpy as _np

class GraphTrace():
    """
    This class represents a Trace and the possible attributes it can contain
    """
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.xData = None
        self.yData = None
        if 'x' in kwargs:
            self.xData = kwargs.pop('x')
        if 'y' in kwargs:
            self.yData = kwargs.pop('y')
        
    def setData(self, x, y):
        self.xData = x
        self.yData = y
        
    def getData(self, transformed=True):
        if transformed:
            x,y = self.transform(self.xData, self.yData)
        else:
            x,y = self.xData, self.yData
        return _np.array([_np.array(x), _np.array(y)])
        
    def transform(self, x, y):
        return x,y