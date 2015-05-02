# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 14:37:38 2015

@author: Alex
"""
#import os as _os
#_os.environ['QT_API'] = 'pyside'# 'pyqt' for PyQt4 / 'pyside' for PySide
#
#from QtVariant import QtGui as _gui
#from QtVariant import QtCore as _core

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

import pyqtgraph as _pg
from GraphTrace import GraphTrace


class GraphWidget(_gui.QWidget):
    """
    This implements the generic structure of a graph widget and gives access to
    different attributes (menus, ect...)
    
    TO DO
    """
    
    #Explicit Signal List
    hide_signal = _core.Signal()
    
    
    def __init__(self, parent=None, **kwargs):
        #super(GraphWidget, self).__init__(parent=parent)
        _gui.QWidget.__init__(self, parent=parent)
        
        #This variable will contain all the generic traces
        self.traces = dict()

        #Raise error is essential function not implemented
        essential_methods = ['__iter__', '__len__', '__getitem__', '__setitem__',
                             'addTrace', 'removeTrace', '_setTraceData']
        for method in essential_methods:
            if not method in dir(self):
                raise Exception(method + " not implemented in the subclass of GraphWidget")
         
                
        
    def buildMenu(self):
        """
        Build the menu for the QWidget
        """        
        #Add a menu bar
        self.menu = dict()
        self.menu['_QMenuBar'] = _gui.QMenuBar()
        self.widget_layout.insertWidget(0, self.menu['_QMenuBar'])
        self.widget_layout.setContentsMargins(0,0,0,0)
        
        #Create a File Menu
        self.menu['File'] = dict()
        self.menu['File']['_QMenu'] = self.menu['_QMenuBar'].addMenu('File')
        
        #Add Actions
        self.menu['File']['Hide'] = self.menu['File']['_QMenu'].addAction('Hide')
        self.menu['File']['Hide'].triggered.connect(lambda: self.hide_signal.emit())
        
    def copyTrace(self, trace):
        """
        This takes in a GraphTrace object and uses it to create a new trace
        """
        x,y= trace.getData()
        return self.addTrace(trace.name, x=x, y=y, **trace.kwargs)
        
    def __iter__(self):
        return iter(self.traces)
        
    def __len__(self):
        return len(self.traces)
        
    def __getitem__(self, key):
        return self.traces[key]
        
    def __setitem__(self, key, value):
        self.addTrace(key, **value)
		

class PyQtGraphWidget(GraphWidget):
    
    def __init__(self, parent=None, **kwargs):
        """
        This widget wraps a pyqtgraph PlotWidget (attribute <plot>), so it can 
        easilly be used as a standard QWidget.  It also add some methods to
        easilly handle multiple traces creation, deletion and update.
        """
        #Initialized
        super(PyQtGraphWidget, self).__init__(parent=parent)
        
        #Create a layout on the Widget
        self.widget_layout = _gui.QVBoxLayout()
        self.setLayout(self.widget_layout)
        
        #Put a widget in the layout
        pw = _pg.PlotWidget(**kwargs)
        self.plot_item = pw.getPlotItem()
        self.widget_layout.addWidget(pw)
        
        #This variable contains the PlotDataItem from PyQtGraph
        self.pyqt_traces = dict()
        
        #Build Menu
        self.buildMenu()
        
        #Do some additional init
        self.legend = self.plot_item.addLegend()
        
    def addTrace(self, name, **kwargs):
        """
        Create a new trace with name ID <name>.
        
        Check out 
        http://www.pyqtgraph.org/documentation/graphicsItems/plotdataitem.html#pyqtgraph.PlotDataItem.__init__
        for more info about kwargs
        
        eg:
            self.addTrace('trace1', x=_np.linspace(0,100), y=_np.linspace(0,100))
        """
        #Make sure no module_name is used twice
        suffix = ''
        while name+suffix in self.traces:
            if suffix == '':
                suffix = '2'
            else:
                suffix = str(1+int(suffix))
        name += suffix
        self.pyqt_traces[name] = self.plot_item.plot(name=name)
        self.traces[name] = GraphTrace(name, **kwargs)
        self.traces[name].newData.connect(self._setTraceData)
        self.traces[name].newData.emit(name)#SetData once in case data was passed through kwargs
        return self.traces[name]
        
        
        
    def removeTrace(self, name):
        """
        Remove a trace with name id <name>.
        """
        self.legend.removeItem(name)
        self.plot_item.removeItem(self.pyqt_traces[name])
        del self.pyqt_traces[name]
        del self.traces[name]
        
    def _setTraceData(self, name):
        """
        Sets new data on the pyqtGraph widget.  This should not be call 
        externally, but will be called every time a newData signal is emitted
        by the GraphTrace Object.
        """
        x, y = self.traces[name].getData(transformed=True)
        self.pyqt_traces[name].setData(x=x, y=y, **self.traces[name].kwargs)
    

