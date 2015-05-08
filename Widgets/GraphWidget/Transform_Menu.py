# -*- coding: utf-8 -*-
"""
@author: Alex
"""
from Graph_Widget_Plugin import Graph_Widget_Plugin
from PyQt4 import QtGui as _gui
import numpy as _np

#!!!  Edit this when adding or removing functions  !!!
def getAllTransfFct():
    """
    Returns a dictionary associting each fit fct with an instance of it's class
    """
    fitFct = {'NoTransform':NoTransform, 'Y_Lin2Log':Y_Lin2Log, 'Y_Log2Lin':Y_Log2Lin, 'X_YPeakCenter':X_YPeakCenter}#, 'Custom_f':Custom_f}    
    return fitFct

class Transform_Menu(Graph_Widget_Plugin):
    
    def __init__(self, parent_graph):
        Graph_Widget_Plugin.__init__(self, parent_graph)
        self.menu = self.graph.menu
        
        #Build view menu
        if not 'Transform' in self.menu:
            self.menu['Transform'] = dict()
            self.menu['Transform']['_QMenu'] = self.menu['_QMenuBar'].addMenu('Transform')
            
        #Update if modules are added or removed
        self.graph.traceAdded.connect(lambda x: self.updateViewMenu())
        self.graph.traceRemoved.connect(lambda x: self.updateViewMenu())

        self.updateViewMenu()
        
    def updateViewMenu(self):        
        #For Each traces add a submenu
        for trc in self.graph:
            if not trc in self:
                self.menu['Transform'][trc] = dict()
                self.menu['Transform'][trc]['_QMenu'] = self.menu['Transform']['_QMenu'].addMenu(trc)
                
                
                #For all sub-menu add all the functions
                fcts = getAllTransfFct()
                for fctName in fcts:
                    #action = _gui.QAction(fctName, self[trc]['_QMenu'] ,checkable = True)
                    self.menu['Transform'][trc][fctName] = fcts[fctName](self.graph[trc], self[trc]['_QMenu'], name=fctName)
                    #Connect signals and add to menu
                    self[trc][fctName].triggered.connect(self.buildLambda(trc, fctName))
                    self[trc]['_QMenu'].addAction(self[trc][fctName])
                
                #Set default
                self.setTransform(trc, 'NoTransform')
                         
        #Remove actions
        for trc in self:
            if not trc in self.graph:
                self['_QMenu'].removeAction(self[trc]['_QMenu'].menuAction())
                del self[trc]['_QMenu']
                self.menu['Transform'].pop(trc)
                
    #This is necessary to make sure trc and fctName are explicit and not variables
    def buildLambda(self, trc, fctName):
        return lambda: self.setTransform(trc, fctName)
        
    def setTransform(self, trc, fct):
        allFcts = self[trc].keys()
        allFcts.remove('_QMenu')
        for f in allFcts:
            self[trc][f].setChecked(False)
        
        self[trc][fct].setTransform()
        self[trc][fct].setChecked(True)
        
    #By default these ignore the _QMenu entry (except for __getitem__)
    def __iter__(self):
        k = self.menu['Transform'].keys()
        k.remove('_QMenu')
        return iter(k)
        
    def __len__(self):
        return len(self.menu['Transform'])-1
        
    def __getitem__(self, key):
        return self.menu['Transform'][key]
        
class Transform_Fct(_gui.QAction):
    def __init__(self, trace, parent, checkable = True, name = 'No Name', **kwargs):#, ):
        _gui.QAction.__init__(self, name, parent, checkable = checkable)
        self.triggered.connect(self.setTransform)
        self.trace = trace
        
    def setTransform(self):
        self.trace.transform = self.fct
        
    def fct(self, x, y):
        raise NotImplemented
        
class NoTransform(Transform_Fct):
    def fct(self,x,y):
        return x,y
        
class Y_Lin2Log(Transform_Fct):
    def fct(self, x, y):
        return x, 20*_np.log10(y)
        
class Y_Log2Lin(Transform_Fct):
    def fct(self, x, y):
        return x, 10**(y/20)
     
def f(x,y):
    return x,y
class Custom_f(Transform_Fct):
    def fct(self, x, y):
        return f(x,y)
        
class X_YPeakCenter(Transform_Fct):
    """
    Keeps a running "average" of the Y peak and tries to center the peak around that value
    """
    def __init__(self, trace, parent, final_update_rate = 0.001, decay_rate = 100, **kwargs):
        Transform_Fct.__init__(self, trace, parent, **kwargs)
        self.alpha = lambda t: final_update_rate + (1-final_update_rate)*_np.exp(-t/decay_rate)
        self.max_time = 10*decay_rate
        self.final_alpha = final_update_rate
        self.time = 0
        self.peak = 0
    
    def fct(self, x, y):
        i = _np.argmax(y)
        if self.time < self.max_time:
            alpha = self.alpha(self.time)
            self.time += 1
        else:
            alpha = self.final_alpha
        self.peak = self.peak*(1-alpha) + alpha * x[i]
        
        return x-self.peak, y