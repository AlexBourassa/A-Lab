# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

This implement cross-air for pyqtgraph based widgets
"""

from A_Lab.Widgets.GraphWidget.Graph_Widget_Plugin import *
from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core
from PyQt4 import uic as _uic
import os as _os
import numpy as _np
import pyqtgraph as _pg


class _Crosshair():
    def __init__(self, id, graph, legend, pen='y'):
        self.id = id
        self.graph = graph
        self.legend = legend
        self.vLine = _pg.InfiniteLine(angle=90, movable=False, pen=pen)
        self.hLine = _pg.InfiniteLine(angle=0, movable=False, pen=pen)
        self.opts = { 
            'pen': pen,
            'shadowPen': None,
            'fillLevel': None,
            'fillBrush': None,
            'brush': None,
            'symbol': '+',
            'symbolSize': 10,
            'size': 10,
            'symbolPen': pen,
            'symbolBrush': (50, 50, 150)}
        self.hLine.opts = self.opts
        self.legend.addItem(self.hLine, name='')
        self.label = self.legend.items[-1][1]

        graph.plot_item.addItem(self.vLine, ignoreBounds=True)
        graph.plot_item.addItem(self.hLine, ignoreBounds=True)
        #self.label.setParentItem(graph.plot_item.vb)

    def deleteLater(self):
        self.legend.removeItem(self.label.text)
        for o in [self.vLine, self.hLine, self.label]: o.deleteLater()

    def setVisible(self, visible):
        if visible:
            for o in [self.vLine, self.hLine, self.label]: o.show()
        else:
            for o in [self.vLine, self.hLine, self.label]: o.hide()

    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.graph.plot_item.sceneBoundingRect().contains(pos):
            mousePoint = self.graph.plot_item.vb.mapSceneToView(pos)
            self.label.setText("&nbsp;"*4 + str(self.id)+"&nbsp;"*4+"x=%.5g y=%.5g" % (mousePoint.x(), mousePoint.y()))
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    def getPos(self):
        return self.vLine.getPos()[0], self.hLine.getPos()[1]

    def __add__(self, other):
        x1,y1 = self.getPos()
        x2,y2 = other.getPos()
        return x1+x2, y1+y2

    def __sub__(self, other):
        x1,y1 = self.getPos()
        x2,y2 = other.getPos()
        return x1-x2, y1-y2

class _COLOR():
    def __init__(self, color_list=['y', 'r', 'm', 'w', 'c', 'g', 'b']):
        color_list = list(color_list)
        color_list.reverse()
        self.COLOR_LIST = color_list
        self.unused = color_list
        self.used = dict()
    def register(self, id):
        if len(self.unused)==0:
            self.unused = self.COLOR_LIST ##Reset the list
        c = self.unused.pop(-1)
        self.used[id] = c
        return c
    def unregister(self, id):
        c = self.used.pop(id)
        if c not in self.unused: self.unused.append(c)

class CrosshairsGroup():

    def __init__(self, graph):
        self.graph = graph
        self.crosshairs_list = dict()
        self.proxy = None
        self.legend = _pg.LegendItem()
        self.legend.setParentItem(self.graph.plot_item.vb)
        self._color_reg = _COLOR()
        self.current_id = 0
        self.legend.anchor((0,1),(0,1))

    def setVisible(self, id, visible):
        self[id].setVisible(visible)
            
    def addCrosshair(self):
        id = self.current_id
        self.current_id += 1
        c = _Crosshair(id, self.graph, self.legend, pen=self._color_reg.register(id))
        self.crosshairs_list[id] = c
        self.selectMoving(id)
        return id

    def removeCrosshair(self, id):
        self.crosshairs_list.pop(id).deleteLater()
        self._color_reg.unregister(id)

    def selectMoving(self, id):
        """
        id=None indicates that the all the Crosshairs are frozen
        """
        self.stopMoving()
        if not id is None:
            self.proxy = [_pg.SignalProxy(self.graph.plot_item.scene().sigMouseMoved, rateLimit=60, slot=self[id].mouseMoved),
                          _pg.SignalProxy(self.graph.plot_item.scene().sigMouseClicked, delay=0, slot=self.stopMoving)]

    def stopMoving(self):
        del self.proxy
        self.proxy = None

    def __getitem__(self, item):
        return self.crosshairs_list[item]

    def __len__(self):
        return len(self.crosshairs_list)


class Crosshair(Graph_Widget_Plugin):
    
    def __init__(self, parent_graph, **kwargs):
        """
        This plugin allows the graph to span a control pannel for fitting a Trace
        """
        Graph_Widget_Plugin.__init__(self, parent_graph)
        
        self.menu = self.graph.menu
        self.kwargs = kwargs
        self.crosshairs = CrosshairsGroup(self.graph)
        self.graph.crosshairs = self.crosshairs
        
        #Build Crosshair menu
        self.menu['Crosshair'] = dict()
        self.menu['Crosshair']['_QMenu'] = self.menu['_QMenuBar'].addMenu('Crosshair')

        self.menu['Crosshair']['Remove Crosshair'] = dict()
        self.menu['Crosshair']['Remove Crosshair']['_QMenu'] = self.menu['Crosshair']['_QMenu'].addMenu('Remove Crosshair')

        self.menu['Crosshair']['Move Crosshair'] = dict()
        self.menu['Crosshair']['Move Crosshair']['_QMenu'] = self.menu['Crosshair']['_QMenu'].addMenu('Move Crosshair')

        
        #Add the action
        self.menu['Crosshair']['Add Crosshair'] = _gui.QAction('Add Crosshair', self.menu['Crosshair']['_QMenu'])
        self.menu['Crosshair']['_QMenu'].addAction(self.menu['Crosshair']['Add Crosshair'])
        self.menu['Crosshair']['Add Crosshair'].triggered.connect(lambda: self.addCrosshair())

        
        

    def addCrosshair(self):
        id = self.crosshairs.addCrosshair()

        self.menu['Crosshair'][id] = _gui.QAction(str(id), self.menu['Crosshair']['_QMenu'], checkable=True)
        self.menu['Crosshair'][id].setChecked(True)
        self.menu['Crosshair']['_QMenu'].addAction(self.menu['Crosshair'][id])
        self.menu['Crosshair'][id].triggered.connect(lambda: self.crosshairs.setVisible(id, self.menu['Crosshair'][id].isChecked()))

        self.menu['Crosshair']['Remove Crosshair'][id] = _gui.QAction(str(id), self.menu['Crosshair']['Remove Crosshair']['_QMenu'])
        self.menu['Crosshair']['Remove Crosshair']['_QMenu'].addAction(self.menu['Crosshair']['Remove Crosshair'][id])
        self.menu['Crosshair']['Remove Crosshair'][id].triggered.connect(lambda: self.removeCrosshair(id))

        self.menu['Crosshair']['Move Crosshair'][id] = _gui.QAction(str(id), self.menu['Crosshair']['Move Crosshair']['_QMenu'])
        self.menu['Crosshair']['Move Crosshair']['_QMenu'].addAction(self.menu['Crosshair']['Move Crosshair'][id])
        self.menu['Crosshair']['Move Crosshair'][id].triggered.connect(lambda: self.moveCrosshair(id))

    def removeCrosshair(self, id):
        self.crosshairs.removeCrosshair(id)
        self.menu['Crosshair']['Remove Crosshair']['_QMenu'].removeAction(self.menu['Crosshair']['Remove Crosshair'][id])
        self.menu['Crosshair']['Move Crosshair']['_QMenu'].removeAction(self.menu['Crosshair']['Move Crosshair'][id])
        self.menu['Crosshair']['_QMenu'].removeAction(self.menu['Crosshair'][id])
        del self.menu['Crosshair']['Remove Crosshair'][id]
        del self.menu['Crosshair']['Move Crosshair'][id]
        del self.menu['Crosshair'][id]

    def moveCrosshair(self, id):
        self.crosshairs.selectMoving(id)


        



        