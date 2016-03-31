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

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

from threading import Timer

import numpy as _np

class E8364B_GUI(PyQtGraphWidget):
    def __init__(self, parent, device, **kwargs):
        super(E8364B_GUI, self).__init__(parent)
        self.feeder = E8364_Feeder(device=device, **kwargs)
        self.addTrace('NA', feeder=self.feeder)
        self.device = device

        # Add a fitter
        self.plugins['Data Representation'] = Data_Rep_Menu(self)


    def closeEvent(self, event):
        self.feeder.timer_thread.cancel()
        super(E8364B_GUI,self).closeEvent(event)





class E8364_Feeder(Pooled_Device):

    def __init__(self, device, period=200, debug=True, **kw):
        self.device = device
        super(E8364_Feeder, self).__init__(device, debug=debug, **kw)


    def x_data(self):
        import time as _t
        _t.sleep(1000)
        return self.device.x_data()

    def y_data(self):
        return self.transform(self.device.y_data())

    def transform(self, x):
        """Dummy transform that will be editable by the data_rep menu
        """
        return _np.abs(x)


class Data_Rep_Menu(Graph_Widget_Plugin):

    ALLOWED_DATA_REP = {'Phase': _np.angle, 'Mag': _np.abs}
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
        print(rep)
        if not rep in self.ALLOWED_DATA_REP: raise Exception("Data Representation not allowed")
        else:
            self.graph.feeder.transform = self.ALLOWED_DATA_REP[rep]
            for other_rep in self.ALLOWED_DATA_REP:
                self[other_rep].setChecked(False)
            self[rep].setChecked(True)

    def __getitem__(self, key):
        return self.menu['Data Representation'][key]
