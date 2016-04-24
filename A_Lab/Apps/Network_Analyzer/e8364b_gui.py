"""
    A_Lab.Network_Analyzer.e8364b_gui
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    GUI widgets for the E8364B.

    Authors: Alexandre Bourassa
    Date: 28/03/2016
"""

from A_Lab.Widgets.GraphWidget.GraphWidget import PyQtGraphWidget
from A_Lab.Devices.Pooled_Device import Pooled_Device
from A_Lab.Widgets.GraphWidget.Graph_Widget_Plugin import Graph_Widget_Plugin

from lantz.driver import logger

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

from threading import Timer
import traceback
import time as _t

import numpy as _np

class E8364B_GUI(PyQtGraphWidget):
    def __init__(self, parent, device, **kwargs):
        super(E8364B_GUI, self).__init__(parent)
        self.feeder = E8364B_Feeder(device=device, **kwargs)
        self.addTrace('NA', feeder=self.feeder)
        self.device = device

        # Add a fitter
        self.plugins['Data Representation'] = Data_Rep_Menu(self)

        #self.feeder.startPolling()

    def destroyEvent(self):
        self.feeder.stopPolling()
        _t.sleep(1)
        self.feeder.stopThread()

    def showEvent(self,event):
        self.feeder.startPolling()

    def hideEvent(self, event):
        self.feeder.stopPolling()

    def disable(self):
        """Stop the Feeder from poolling.  You would probably want to do this when running an experiment
        """
        self.feeder.stopPolling()

    def enable(self):
        self.feeder.startPolling()






class E8364B_Feeder(Pooled_Device):

    def __init__(self, device, period=200, **kw):
        self.device = device
        super(E8364B_Feeder, self).__init__(device, start_polling=False, **kw)


    def x_data(self):
        logger.propagate = False
        ans = self.device.x_data()
        logger.propagate = True
        return ans

    def y_data(self):
        logger.propagate = False
        ans = self.device.y_data()
        logger.propagate = True
        return ans

    def transform(self, x, y):
        """Dummy transform that will be editable by the data_rep menu
        """
        return x, _np.abs(y)

    def query_error_fallback(self, error):
        # This will stop the timer, attempt to empty the read buffer by doing a read and then start the timer again
        self.sig_stopPolling.emit()
        print("Error while querying the device, pooling stopped")
        # try:
        #     self.device.read_raw()
        # finally:
        #     traceback.print_exc()
        #     self.sig_startPolling.emit()
        return


class Data_Rep_Menu(Graph_Widget_Plugin):

    ALLOWED_DATA_REP = {'Phase': {'transform':lambda x,y: (x, _np.angle(y)),'opts':[]},
                       'Mag':{'transform':lambda x,y: (x, _np.abs(y)),'opts':[]}}
    def __init__(self, parent_graph):
        Graph_Widget_Plugin.__init__(self, parent_graph)
        self.menu = self.graph.menu

        # Build the menu
        if not 'Data Representation' in self.menu:
            self.menu['Data Representation'] = dict()
            self.menu['Data Representation']['_QMenu'] = self.menu['_QMenuBar'].addMenu('Data Representation')

        # Build a generating func
        def f(rep): return lambda: self.setDataRep(rep)

        # Add the transforms
        for rep in self.ALLOWED_DATA_REP:
            self.menu['Data Representation'][rep] = _gui.QAction(rep, self['_QMenu'] ,checkable = True)
            self['_QMenu'].addAction(self[rep])
            self[rep].triggered.connect(f(rep))

        self['Mag'].setChecked(True)



    def setDataRep(self, rep):
        if not rep in self.ALLOWED_DATA_REP: raise Exception("Data Representation not allowed")
        else:
            self.graph.feeder.transform = self.ALLOWED_DATA_REP[rep]['transform']
            for other_rep in self.ALLOWED_DATA_REP:
                self[other_rep].setChecked(False)
            self[rep].setChecked(True)

    def __getitem__(self, key):
        return self.menu['Data Representation'][key]
