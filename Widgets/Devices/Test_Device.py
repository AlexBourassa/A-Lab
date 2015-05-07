# -*- coding: utf-8 -*-
"""
@author: Alex
"""

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core
import numpy as _np
import time as _t

class Test_Device(_gui.QWidget):
    
    newData = _core.Signal(_np.ndarray, _np.ndarray)
    
    def __init__(self, dataSize = 100, amplitude = 0.2, center = 0, addedGaussian=True, **kw):
        _gui.QWidget.__init__(self)
        self.dataSize = dataSize
        self.amplitude = amplitude
        self.center = center
        self.addedData = 0
        self.x = _np.arange(0,self.dataSize)
        if addedGaussian: 
            self.addedData = _np.exp(-_np.power(self.x - (dataSize/2), 2.) / (2.0 * _np.power(dataSize/6., 2.)))
        
        self.last_time = _t.time()
        self.timer = _core.QTimer()
        self.timer.timeout.connect(self.genData)
        self.timer.start(20)
        
    def genData(self):
        t = self.last_time
        self.last_time = _t.time()
        #print t - self.last_time
        x = self.x
        y = (_np.random.rand(100)-0.5)*2*self.amplitude + self.center
        self.setData(x,y+self.addedData )
        
    def setData(self, x, y):
        self.newData.emit(x,y)