# -*- coding: utf-8 -*-
"""
@author: AlexBourassa
"""

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core
import numpy as _np
import time as _t

class Test_Device(_gui.QWidget):
    
    signal_newData = _core.Signal(_np.ndarray, _np.ndarray)
    
    def __init__(self, dataSize = 100, amplitude = 0.2, center = 0, addedGaussian=True, period=50, debug=True, **kw):
        _gui.QWidget.__init__(self)

        # Make these variables public
        self.dataSize = dataSize
        self.amplitude = amplitude
        self.center = center
        self.period = period
        self.debug = debug

        self.addedData = 0
        self.x = _np.arange(0,self.dataSize)
        if addedGaussian: 
            self.addedData = _np.exp(-_np.power(self.x - (dataSize/2), 2.) / (2.0 * _np.power(dataSize/6., 2.)))
        
        self.last_time = _t.time()
        self.timer = _core.QTimer()
        self.timer.timeout.connect(self.genData)
        self.timer.start(period)
        
    def genData(self):
        if self.debug:
            t = self.last_time
            self.last_time = _t.time()
            if 1.1*self.period<(t - self.last_time):
                print "Test_Device timer was more then 10% late (" + str(t-self.last_time) + ")"
                self.timer.stop()
        x = self.x
        y = (_np.random.rand(100)-0.5)*2*self.amplitude + self.center
        self._setData(x,y+self.addedData)
        
    def _setData(self, x, y):
        self.signal_newData.emit(x,y)
        self.setData(x,y)
        
        
    def setData(self, x, y):
        """
        This is a dummy function that will get overwritten when the object is
        associated with a GraphTrace as a feeder.
        """
        return
        
        

class Raster_Test_Device(_gui.QWidget):
    signal_newData = _core.Signal(_np.ndarray)

    def __init__(self, imv_widget, point_rate = 5000, point_packet_size = 500, debug=True, **kw):
        """
        This function is meant to simulate a Raster_Device
        @param imv_widget Is a Graph2D widget on which to plot
        @param point_rate Approximate number of points per seconds to be generated
        @param point_packet_siza Number of points to be "buffered" betweeen redraw
        """
        _gui.QWidget.__init__(self)

        # Set variable public
        self.period = int((1000*point_packet_size)/point_rate)
        self.imv = imv_widget
        self.packet_size = point_packet_size
        self.debug = debug

        # Init the raster
        self.imv.initRaster(200,200)

        # Start a timer
        self.last_time = _t.time()
        self.timer = _core.QTimer()
        self.timer.timeout.connect(self.genData)
        self.timer.start(self.period)

    def genData(self):
        # For debugging purposes
        if self.debug:
            t = self.last_time
            self.last_time = _t.time()
            if 1.1*self.period<(t - self.last_time):
                print "Raster_Test_Device timer was more then 10% late (" + str(t-self.last_time) + ")"
                self.timer.stop()
        data = _np.random.rand(self.packet_size)
        self.imv.addRasterData(data)