# -*- coding: utf-8 -*-
"""
@author: AlexBourassa
"""

import numpy as _np
from PyQt4 import QtCore as _core

class GraphTrace(_core.QObject):
    """
    This class represents a Trace and the possible attributes it can contain
    """
    signal_newData = _core.Signal(str) #str: name of the trace
    signal_transformChanged = _core.Signal(str, str) #str: name of the trace
                                                     #str: name of the transform
    
    def __init__(self, name, *args, **kwargs):
        _core.QObject.__init__(self)
        if 'name' in kwargs:
            kwargs.pop('name')
        self.name = name
        self.transform_name = 'NoTransform'
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
            self.signal_newData.emit(self.name)
            
        if 'feeder' in kwargs: self.setNewFeeder(kwargs['feeder'])
        
    def setData(self, x, y):
        self.xData = _np.array(x)
        self.yData = _np.array(y)
        self.signal_newData.emit(self.name)
        
    def setNewFeeder(self, feeder):
        #Reset the set data of the feeder
        if 'feeder' in self.kwargs: 
            try:
                self.kwargs['feeder'].setData = type(self.kwargs['feeder']).setData#reconnect to previous function
            except:
                self.kwargs['feeder'].setData = lambda: 0#Do nothing
        feeder.setData = self.setData
        self.kwargs['feeder'] = feeder
        return
        
        
    def getData(self, transformed=True):
        """
        Returns the current trace data, 
        """
        if transformed and not (self.xData is None or self.yData is None):
            x,y = self.transform(self.xData, self.yData)
        else:
            x,y = self.xData, self.yData
        return x, y
        
    def setTransform(self, f, transform_name='Custom'):
        """
        Sets a new transform to the trace.
        
        Function <f> must be of the form:
            def f(x,y):
                ...
                return new_x, new_y
        
        TODO: Make explicit cheks that the function is valid (for now I'll
        assume everyone is being responsible...)
        """
        self.transform_name = transform_name
        self.transform = f
        self.signal_transformChanged.emit(self.name, transform_name)
        self.signal_newData.emit(self.name)
        
    
    def transform(self, x, y):
        """
        This is a function coresponding to an applied transformed on the data.
        It is meant to be overwritten by setTransform
        """
        return x,y
        
    def save(self, file_handler, transformedData = True):
        """
        Save the trace info in the current group.
        
        This will create new entries: 
            x & y in data
            kwargs in headers
        """
        x,y= self.getData(transformed=transformedData)
        file_handler.addData(x=x, y=y)
        kwargs=dict(self.kwargs)
        if 'feeder' in kwargs: kwargs.pop('feeder') #Cannot keep the feeder instance
        file_handler.addHeaders(kwargs=kwargs)

# This is a very simple class that allows for the feeder source to be independant
# from the Trace object.  Another way to do this is to simply use the 
class Generic_TraceFeeder(_core.QObject):       
    def __init__(self, *args, **kwargs):
        _core.QObject.__init__(self, **kwargs)
        
    def setData(self, x, y):
        raise NotImplemented("The TraceFeeder.setData(x,y) needs to be associated with a specific trace to do something...From a GraphTrace use setFeeder.")