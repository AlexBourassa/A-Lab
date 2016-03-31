# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

This is a generic polled device feeder which can be used as a model to build other standard devices feeder
"""
from PyQt4 import QtCore as _core
import numpy as _np
import time as _t

from threading import Timer

class Pooled_Device(_core.QObject):
    signal_newData = _core.Signal(_np.ndarray, _np.ndarray)

    def __init__(self, device, period=200, debug=True, **kw):
        _core.QObject.__init__(self)

        # Make these variables public
        self.debug = debug
        self.device = device
        self.period = period


        self.timer_thread = Timer(1100, self.genData, args=[self])
        #self.timer_thread.start()

        self.last_time = _t.time()


    def genData(self):
        if self.debug:
            t = self.last_time
            self.last_time = _t.time()
            if 1.1 * self.period < (t - self.last_time):
                print(("Test_Device timer was more then 10% late (" + str(t - self.last_time) + ")"))
                self.timer.stop()
        print("genData")
        x = self.x_data()
        y = self.y_data()
        self._setData(x, y)

    def x_data(self):
        """
            This is a dummy function that will get overwritten by the feeder subclass.
            It should always return the x data to be fed to the trace.
        """
        return _np.ndarray([])

    def y_data(self):
        """
            This is a dummy function that will get overwritten by the feeder subclass.
            It should always return the y data to be fed to the trace.
        """
        return _np.ndarray([])

    def _setData(self, x, y):
        self.signal_newData.emit(x,y)
        self.setData(x,y)


    def setData(self, x, y):
        """
        This is a dummy function that will get overwritten when the object is
        associated with a GraphTrace as a feeder.
        """
        return