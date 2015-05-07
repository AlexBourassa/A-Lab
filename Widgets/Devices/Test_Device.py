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
    
    def __init__(self, dataSize = 100, amplitude = 1, center = 0, **kw):
        _gui.QWidget.__init__(self)
        self.dataSize = dataSize
        self.amplitude = amplitude
        self.center = center
        
        self.last_time = _t.time()
        self.timer = _core.QTimer()
        self.timer.timeout.connect(self.genData)
        self.timer.start(20)
        
    def genData(self):
        t = self.last_time
        self.last_time = _t.time()
        print t - self.last_time
        x = _np.arange(0,self.dataSize)
        y = (_np.random.rand(100)-0.5)*2*self.amplitude + self.center
        self.setData(x,y)
        
    def setData(self, x, y):
        self.newData.emit(x,y)