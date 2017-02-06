# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

@TODO: Add remote plotting to plot from a different process
"""
#import os as _os
#_os.environ['QT_API'] = 'pyside'# 'pyqt' for PyQt4 / 'pyside' for PySide
#
#from QtVariant import QtGui as _gui
#from QtVariant import QtCore as _core

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

import pyqtgraph as _pg
from A_Lab.Widgets.GraphWidget.GraphTrace import GraphTrace
from A_Lab.Widgets.GraphWidget.Trace_View_Menu import Trace_View_Menu
from A_Lab.Widgets.GraphWidget.Transform_Menu import Transform_Menu
from A_Lab.Widgets.GraphWidget.Fitter import Fitter
from A_Lab.Widgets.GraphWidget.Crosshair import Crosshair
import numpy as _np

class GraphWidget(_gui.QWidget):
    """
    This implements the generic structure of a graph widget and gives access to
    different attributes (menus, ect...)
    """
    
    #Explicit Signal List
    traceAdded   = _core.Signal(str)
    traceRemoved = _core.Signal(str)
    
    
    def __init__(self, parent=None, **kwargs):
        #super(GraphWidget, self).__init__(parent=parent)
        _gui.QWidget.__init__(self, parent=parent)

        #This variable will contain all the generic traces
        self.traces = dict()
        self.plugins = dict()

        #Raise error is essential function not implemented
        essential_methods = ['__iter__', '__len__', '__getitem__', '__setitem__',
                             'addTrace', 'removeTrace', '_setTraceData', 'setTraceVisible']
        for method in essential_methods:
            if not method in dir(self):
                raise NotImplementedError(method + " not implemented in the subclass of GraphWidget")
         
                
        
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
        self.menu['File']['Hide'].triggered.connect(lambda: self.parent().hide())
        
    def addStandardPlugins(self):
        #Add View Menu
        self.plugins['View'] = Trace_View_Menu(self)
        
        #Add the transform menu
        self.plugins['Transform_Menu'] = Transform_Menu(self)
        
        #Add a fitter
        self.plugins['Fitter'] = Fitter(self, pen='g')
        
    def copyTrace(self, trace):
        """
        This takes in a GraphTrace object and uses it to create a new trace
        """
        x,y= trace.getData()
        trc = self.addTrace(trace.name, x=x, y=y, **trace.kwargs)
        trc.setTransform(trace.transform, transform_name = trace.transform_name)
        return trc
        
    def getRegionData(self, trace_name, verbose=True, **kw):
        x,y = self.traces[trace_name].getData(**kw)
        if verbose:
            print("No getRegionData() function defined for this GraphWidget.  Returning all data...")
        return x,y
        
    def saveSettings(self, settingsObj = None, **kwargs):
        if type(settingsObj) != _core.QSettings:
            print("No QSetting object was provided")
        else:
            for plug_name in self.plugins:
                settingsObj.beginGroup(plug_name)
                self.plugins[plug_name].saveSettings(settingsObj)
                settingsObj.endGroup()
    
    def loadSettings(self, settingsObj = None, **kwargs):
        if type(settingsObj) != _core.QSettings:
            print("No QSetting object was provided")
        else:
            for plug_name in self.plugins:
                settingsObj.beginGroup(plug_name)
                self.plugins[plug_name].loadSettings(settingsObj)
                settingsObj.endGroup()    
                
    def save(self, file_handler = None, transformedData = True):
        if file_handler == None: return None
        file_handler.beginGroup('::TraceData')        
        for trace_name in self.traces:
            file_handler.beginGroup(trace_name)
            self.traces[trace_name].save(file_handler, transformedData=transformedData)
            file_handler.endGroup()
        file_handler.endGroup()
        
    def load(self, file_handler = None):
        if file_handler == None: return None

        #Create function aliases for shortcuts
        headers, data = file_handler.getHeaders, file_handler.getData            
            
        #Begin by loading the structures
        file_handler.beginGroup('::TraceData')
        data_g, data_v = data().listGroupsAndValues()
        headers_g, headers_v = headers().listGroupsAndValues()
        
        #Trace by trace, load the data
        for trace_name in data_g:
            file_handler.beginGroup(trace_name)
            
            #Check if the strucutre has trace metadata for this trace
            if trace_name in headers_g: hasMetadata = True
            else: hasMetadata = False
            
            #Get the data if it exist
            g, v = data().listGroupsAndValues()
            if 'x' in v and 'y' in v:
                x = data()['x']
                y = data()['y']
                trc_kw = {}
                if hasMetadata:
                    trc_kw = headers()['kwargs']
                #create a new trace
                self.addTrace(trace_name, x=x, y=y, **trc_kw)

            file_handler.endGroup()
        file_handler.endGroup()
        
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
        easily be used as a standard QWidget.  It also add some methods to
        easily handle multiple traces creation, deletion and update.
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
        self.lr = _pg.LinearRegionItem([0,10])
        self.plot_item.addItem(self.lr)
        self.lr.setVisible(False)
        self.legend = self.plot_item.addLegend()
        #self.buildCrosshair()
        self.addStandardPlugins()

    def addStandardPlugins(self):
        super().addStandardPlugins()
        #Add Crosshair
        self.plugins['Crosshair'] = Crosshair(self)
        
    def buildMenu(self):
        super(PyQtGraphWidget, self).buildMenu()
        #Create Actions
        self.menu['File']['Show Linear Region'] = _gui.QAction('Show Linear Region', 
                                                          self.menu['File']['_QMenu'],
                                                          checkable = True)
        self.menu['File']['Show Crosshair'] = _gui.QAction('Show Crosshair',
                                                               self.menu['File']['_QMenu'],
                                                               checkable=True)
        #Add actions
        self.menu['File']['_QMenu'].addAction(self.menu['File']['Show Crosshair'])
        self.menu['File']['_QMenu'].addAction(self.menu['File']['Show Linear Region'])

        #Connect signals
        self.menu['File']['Show Linear Region'].triggered.connect(lambda: self.lr.setVisible(self.menu['File']['Show Linear Region'].isChecked()))
        self.menu['File']['Show Crosshair'].triggered.connect(
            lambda: self.crosshairs.setVisible(self.menu['File']['Show Crosshair'].isChecked()))


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
        self.traces[name].signal_newData.connect(self._setTraceData)
        self.traces[name].signal_newData.emit(name)#SetData once in case data was passed through kwargs
        self.pyqt_traces[name].visible = True
        
        self.traceAdded.emit(name)
        return self.traces[name]

    # def buildCrosshair(self):

    #     graph = self
    #     class Crosshair():
    #         def __init__(self):
    #             self.vLine = _pg.InfiniteLine(angle=90, movable=False)
    #             self.hLine = _pg.InfiniteLine(angle=0, movable=False)
    #             self.label = _pg.TextItem()#justify='right')

    #             graph.plot_item.addItem(self.vLine, ignoreBounds=True)
    #             graph.plot_item.addItem(self.hLine, ignoreBounds=True)
    #             self.label.setParentItem(graph.plot_item.vb)

    #         def deleteLater(self):
    #             for o in [self.vLine, self.hLine, self.label]: o.deleteLater()


    #         def setVisible(self, visible):
    #             if visible:
    #                 for o in [self.vLine, self.hLine, self.label]: o.show()
    #             else:
    #                 for o in [self.vLine, self.hLine, self.label]: o.hide()

    #         def mouseMoved(self, evt):
    #             pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    #             if graph.plot_item.sceneBoundingRect().contains(pos):
    #                 mousePoint = graph.plot_item.vb.mapSceneToView(pos)
    #                 self.label.setText("x=%.5g\ty=%.5g" % (mousePoint.x(), mousePoint.y()))
    #                 #label.setText()
    #                 self.vLine.setPos(mousePoint.x())
    #                 self.hLine.setPos(mousePoint.y())

    #     class CrosshairsGroup():
    #         def __init__(self):
    #             self.crosshairs_list = list()
    #         def setVisible(self, visible):
    #             if visible: self.addCrosshair()
    #             else:
    #                 for c in self.crosshairs_list: c.deleteLater()
    #                 del self.proxy
    #         def addCrosshair(self):
    #             c = Crosshair()
    #             self.crosshairs_list.append(c)
    #             self.proxy = _pg.SignalProxy(graph.plot_item.scene().sigMouseMoved, rateLimit=60, slot=self[-1].mouseMoved)
    #         def __getitem__(self, item):
    #             return self.crosshairs_list[item]


    #     self.crosshairs = CrosshairsGroup()



        
    def getRegionData(self, trace_name, **kw):
        x,y = self.traces[trace_name].getData(**kw)
        if not self.lr.isVisible():
            return x, y
        region = self.lr.getRegion()
        #Get the cropping array
        crop = _np.logical_and(x >= region[0], x <= region[1])
        
        if len(crop)>1:            
            return x[crop], y[crop]
        else:
            #If none of the curve is in the region.  Append an empty array
            return _np.ndarray([0]), _np.ndarray([0])
        
    def removeTrace(self, name):
        """
        Remove a trace with name id <name>.
        """
        self.legend.removeItem(name)
        self.plot_item.removeItem(self.pyqt_traces[name])
        del self.pyqt_traces[name]
        del self.traces[name]
        self.traceRemoved.emit(name)
        
    def setTraceVisible(self, name, visible=True):
        """
        Show/Hide a trace by removing the items from the plot.  This should not
        be called externally as it might results in multiple traces or an error.
        Instead use setVisible on the Trace.
        """
        if self.pyqt_traces[name].visible == visible:
            return
        if visible:
            self.plot_item.addItem(self.pyqt_traces[name])
            #self.legend.addItem(self.pyqt_traces[name], name)
        else:
            self.legend.removeItem(self.pyqt_traces[name])
            self.legend.removeItem(name)
            self.plot_item.removeItem(self.pyqt_traces[name])
        self.pyqt_traces[name].visible = visible
            
        
    def _setTraceData(self, name):
        """
        Sets new data on the pyqtGraph widget.  This should not be call 
        externally, but will be called every time a signal_newData signal is emitted
        by the GraphTrace Object.
        """
        x, y = self.traces[name].getData(transformed=True)
        self.pyqt_traces[name].setData(x=x, y=y, **self.traces[name].kwargs)




