# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

This is a generic polled device feeder which can be used as a model to build other standard devices feeder
"""
from PyQt4 import QtCore as _core
import numpy as _np
import time as _t

import traceback

class Pooled_Device(_core.QObject):
    signal_newData = _core.Signal(_np.ndarray, _np.ndarray)
    sig_stopPolling = _core.Signal()
    sig_startPolling = _core.Signal(int)

    def __init__(self, device, period=200, debug=True, start_polling = True, **kw):
        _core.QObject.__init__(self)

        # Make these variables public
        self.debug = debug
        self.device = device
        self.period = period
        self.polling = False


        # Create the thread
        self.worker_thread = _core.QThread()

        #Create the timer
        self.timer = _core.QTimer()
        self.timer.timeout.connect(self.genData)
        self.sig_startPolling.connect(self.timer.start)
        self.sig_stopPolling.connect(self.timer.stop)

        self.startPolling()

        # Start the thread
        self.moveToThread(self.worker_thread)
        self.timer.moveToThread(self.worker_thread)
        self.worker_thread.start(_core.QThread.NormalPriority)

        self.last_time = _t.time()

    def stopPolling(self):
        self.sig_stopPolling.emit()
        self.polling = False

    def startPolling(self):
        self.polling = True
        self.sig_startPolling.emit(self.period)

    def stopThread(self):
        self.worker_thread.exit()

    def genData(self):
        if self.debug:
            t = self.last_time
            self.last_time = _t.time()
            if 1.1 * self.period < (t - self.last_time):
                print(("Test_Device timer was more then 10% late (" + str(t - self.last_time) + ")"))
                self.timer.stop()
        try:
            x = self.x_data()
            y = self.y_data()
            x,y = self.transform(x,y)
        except Exception as e:
            traceback.print_exc()
            self.query_error_fallback(e)
        self._setData(x, y)

    def x_data(self):
        """
            This is a dummy function that will get overwritten by the feeder subclass.
            It should always return the x data to be fed to the trace.
        """
        return _np.ndarray([])

    def query_error_fallback(self, error):
        """
            This is a dummy function that will get overwritten by the feeder subclass.
            It should handle errors that may occur when trying to get data
        """
        return

    def y_data(self):
        """
            This is a dummy function that will get overwritten by the feeder subclass.
            It should always return the y data to be fed to the trace.
        """
        return _np.ndarray([])

    def transform(self,x,y):
        """
            This is a dummy function that can be overwritten by the feeder subclass.
            It allows for direct transformation of the data right after querying
        """
        return x,y

    def _setData(self, x, y):
        self.signal_newData.emit(x,y)
        self.setData(x,y)


    def setData(self, x, y):
        """
        This is a dummy function that will get overwritten when the object is
        associated with a GraphTrace as a feeder.
        """
        return