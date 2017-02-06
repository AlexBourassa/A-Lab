# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

@brief: This class implements a widget which can display images either all at
        once or using a raster scan mode.
"""

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

import pyqtgraph as _pg
import numpy as _np

from A_Lab.Widgets.GraphWidget.Crosshair import Crosshair

class Graph2D(_gui.QWidget):
    """
    This implements the generic structure of a 2d graph widget and gives
    access to different attributes.
    """

    def __init__(self, parent=None, **kwargs):
        #super(GraphWidget, self).__init__(parent=parent)
        _gui.QWidget.__init__(self, parent=parent)

        # Initialize some variables
        self.data = _np.empty(0)
        self.rasterCursor = (0,0)
        self.plugins = dict()

        #Raise error is essential function not implemented
        essential_methods = ['setImage']
        for method in essential_methods:
            if not method in dir(self):
                raise NotImplementedError(method + " not implemented in the subclass of GraphWidget")

    def saveSettings(self, settingsObj = None, **kwargs):
        return
    
    def loadSettings(self, settingsObj = None, **kwargs):
        return
                
    def save(self, file_handler = None, transformedData = True):
        """
        @TODO
        """
        return
        
    def load(self, file_handler = None):
        """
        @TODO
        """
        return

    def addStandardPlugins(self):
        pass

    def buildMenu(self):
        """
        Build the menu for the QWidget
        """
        # Add a menu bar
        self.menu = dict()
        self.menu['_QMenuBar'] = _gui.QMenuBar()
        self.widget_layout.insertWidget(0, self.menu['_QMenuBar'])
        self.widget_layout.setContentsMargins(0, 0, 0, 0)

        # Create a File Menu
        self.menu['File'] = dict()
        self.menu['File']['_QMenu'] = self.menu['_QMenuBar'].addMenu('File')

        # Add Actions
        self.menu['File']['Hide'] = self.menu['File']['_QMenu'].addAction('Hide')
        self.menu['File']['Hide'].triggered.connect(lambda: self.parent().hide())

    def initRaster(self, col, row, init_data = None, raster_mode='1r'):
        """
        Initializes a raster image.
        @param col          number of points in x
        @param row          number of points in y
        @param init_data    initial data to be displayed
        @param raster_mode  select the direction and origin of the raster scan.
                            Should be a string 'xc' where x is an int between 
                            1 and 4 representing the scan origin and c is a
                            letter (r,l,d,u) representing the direction to 
                            start the scan. Current support for:
                                - '1r': Start top-left corner going right
                                - '1d': Start top-left corner going down
        """
        # Define the initialization data
        if init_data == None:
            init_data = _np.zeros((row, col))
        else:
            try:
                init_data = _np.array(init_data)
            except:
                print("Could not cast init_data to numpy array")
            if init_data.shape != (row,col):
                print("Invalid init_data shape... Initializing to zeros")
                init_data = _np.zeros((row, col))
        self.data = init_data

        # Select starting corner. Corners are numbered clockwise starting from
        # 1 at the top left corner
        i = int(raster_mode[0])-1
        self.rasterCursor = [(i/2)*(row-1),(i%2)*(col-1)]

        # Select fast changing cursor index
        if raster_mode[1] in ['r','l']: f = 0
        else: f =1

        # Select f_dir and f_lim
        f_lim = self.data.shape[f]
        if self.rasterCursor[f] == 0: f_dir = 1
        else: f_dir = f_lim = -1

        #Select s_dir
        s_lim = self.data.shape[(f+1)%2]
        if self.rasterCursor[(f+1)%2] == 0: s_dir = 1
        else: s_dir = s_lim = -1

        # Save cursor info
        self.cursorInfo = {'fastChanging_i':f, 'fastChanging_dir':f_dir, 'slowChanging_dir':s_dir, 'fastLimit':f_lim, 'slowLimit':s_lim}


    def addRasterData(self, data):
        for value in data:
            self.data[self.rasterCursor[0],self.rasterCursor[1]] = value
            self.stepCursor()
        self.setImage(self.data)

    def stepCursor(self):
        f = self.cursorInfo['fastChanging_i']
        s = (f+1)%2
        f_dir = self.cursorInfo['fastChanging_dir']
        s_dir = self.cursorInfo['slowChanging_dir']

        # Increase fast changing
        self.rasterCursor[f] += 1*f_dir

        # Update slow changing if we are at the end of the line (and reset fast
        # changing)
        if self.rasterCursor[f] == self.cursorInfo['fastLimit']:
            self.rasterCursor[s] += 1*s_dir
            if f_dir == 1:
                self.rasterCursor[f] = 0
            else:
                self.rasterCursor[f] = self.data.shape[f]-1
        else: return

        # Reset slow changing if we are at the end of the image
        if self.rasterCursor[s] == self.cursorInfo['slowLimit']:
            if s_dir == 1:
                self.rasterCursor[s] = 0
            else:
                self.rasterCursor[s] = self.data.shape[s]-1


class PyQtImageWidget(Graph2D):
    
    def __init__(self, parent=None, **kwargs):
        """
        This widget wraps a pyqtgraph PlotWidget (attribute <plot>), so it can 
        easilly be used as a standard QWidget.  It also add some methods to
        easilly handle multiple traces creation, deletion and update.
        """
        #Initialized
        super(PyQtImageWidget, self).__init__(parent=parent)
        
        #Create a layout on the Widget
        self.widget_layout = _gui.QVBoxLayout()
        self.setLayout(self.widget_layout)
        
        #Put a widget in the layout
        self.plot_item = _pg.PlotItem()
        self.imv = _pg.ImageView(view=self.plot_item, **kwargs)

        #self.image_item = imv.getImageItem()
        self.widget_layout.addWidget(self.imv)

        self.buildMenu()
        self.addStandardPlugins()

    def addStandardPlugins(self):
        super().addStandardPlugins()
        #Add Crosshair
        self.plugins['Crosshair'] = Crosshair(self)

    def setImage(self, im, **kwargs):
        self.data = im
        return self.imv.setImage(im, **kwargs)