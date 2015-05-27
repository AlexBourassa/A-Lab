# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

@TODO: Better method for custom functions
"""
from Graph_Widget_Plugin import Graph_Widget_Plugin
from PyQt4 import QtGui as _gui
import numpy as _np

#!!!  Edit this when adding or removing functions  !!!
def getPredefinedTransfFct():
    """
    Returns a dictionary associting each fit fct with an instance of it's class
    """
    fitFct = {'NoTransform':NoTransform, 'Y_Lin2Log':Y_Lin2Log, 'Y_Log2Lin':Y_Log2Lin, 'X_YPeakCenter':X_YPeakCenter, 'Y_TimeAverage':Y_TimeAverage}#, 'Custom':NoTransform}    
    return fitFct

class Transform_Menu(Graph_Widget_Plugin):
    """
    This class adds a menu that gives options for different live transforms to
    be applied to the data.  You can implement you're own at the bottom using
    base class Transform_Fct. (Don't forget to add it to the getAllTransFct
    for it to appear in your program).
    
    In short, this overwrites the transform fct of a specific trace.
    """
    
    def __init__(self, parent_graph):
        Graph_Widget_Plugin.__init__(self, parent_graph)
        self.menu = self.graph.menu
        
        #Build view menu
        if not 'Transform' in self.menu:
            self.menu['Transform'] = dict()
            self.menu['Transform']['_QMenu'] = self.menu['_QMenuBar'].addMenu('Transform')
            
        #Update if modules are added or removed
        self.graph.traceAdded.connect(lambda x: self.updateTransformMenu())
        self.graph.traceRemoved.connect(lambda x: self.updateTransformMenu())

        self.updateTransformMenu()
        
    def updateTransformMenu(self):

        #For Each traces add a submenu
        for trc in self.graph:
            if not trc in self:
                self.menu['Transform'][trc] = dict()
                self.menu['Transform'][trc]['_QMenu'] = self.menu['Transform']['_QMenu'].addMenu(trc)
                
                
                #For all sub-menu add all the functions
                fcts = getPredefinedTransfFct()
                for fctName in fcts:
                    self.menu['Transform'][trc][fctName] = fcts[fctName](self.graph[trc], self[trc]['_QMenu'], name=fctName)
                    #Connect signals and add to menu
                    self[trc][fctName].triggered.connect(self.buildLambda_triggered(trc, fctName))
                    self[trc]['_QMenu'].addAction(self[trc][fctName])
                
                #Set default
                self[trc]['NoTransform'].chooseTransform()
                self.graph[trc].signal_transformChanged.connect(lambda trc_name, fct_name:self.setCheck(trc_name, fct_name))
                         
        #Remove actions
        for trc in self:
            if not trc in self.graph:
                self['_QMenu'].removeAction(self[trc]['_QMenu'].menuAction())
                del self[trc]['_QMenu']
                self.menu['Transform'].pop(trc)
                
    # These build function are necessary to make sure trc and fctName are 
    # explicit and not variables
    def buildLambda_triggered(self, trc, fctName): return lambda: self[trc][fctName].chooseTransform()
        
    def setCheck(self, trc, fct, createIfNew = True):
        """
        Check the <fct> action in the <trc> submenu.
        
        If <fct> is not a predefined function, create/modified a new entry to
        add it in.
        """
        allFcts = self[trc].keys()
        allFcts.remove('_QMenu')
        for f in allFcts:
            self[trc][f].setChecked(False)
            
        #If the function isn't in the submenu create a new one
        if createIfNew and not fct in getPredefinedTransfFct():
            print str(fct) + " is being added to submenu..."#Debug
            
            #Remove from the list if it already exists
            if fct in self[trc]:
                self[trc]['_QMenu'].removeAction(self[trc][fct])
                self[trc].pop(fct)
                
            #Create the new function
            new_fct = Transform_Fct(self.graph[trc], self[trc]['_QMenu'], name=fct)
            new_fct.fct = new_fct.trace.transform #Assign the current transform function to the new function
                
            #Connect signals and add to menu
            self.menu['Transform'][trc][fct] = new_fct
            self[trc]['_QMenu'].addAction(self[trc][fct])
            self[trc][fct].triggered.connect(self.buildLambda_triggered(trc, fct))
            
        #Check the fct action in the trc submenu
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
        
        
#------------------------------------------------------------------------------
#                 Base Class for the transform fcts
#------------------------------------------------------------------------------
        
class Transform_Fct(_gui.QAction):
    def __init__(self, trace, parent, checkable = True, name = 'No Name', **kwargs):#, ):
        _gui.QAction.__init__(self, name, parent, checkable = checkable)
        self.name = name
        self.triggered.connect(self.chooseTransform)
        self.trace = trace
        
    def chooseTransform(self):
        """
        Set the this class <fct> as the trace transform function
        """
        self.trace.setTransform(self.fct, transform_name=self.name)
        
    def fct(self, x, y):
        raise NotImplemented
 

#------------------------------------------------------------------------------
#         A few transform examples (here you can implement other transforms)
#------------------------------------------------------------------------------
       
class Y_Lin2Log(Transform_Fct):
    def fct(self, x, y):
        return x, 20*_np.log10(y)
        
class Y_Log2Lin(Transform_Fct):
    def fct(self, x, y):
        return x, 10**(y/20)
     
        
class X_YPeakCenter(Transform_Fct):
    """
    Keeps a running "average" of the Y peak and tries to center the peak around that value
    """
    def __init__(self, trace, parent, final_update_rate = 0.001, decay_rate = 50, **kwargs):
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
        
class Y_TimeAverage(Transform_Fct):
    """
    Keeps a running "average" of the Y data
    """
    def __init__(self, trace, parent, final_update_rate = 0.001, decay_rate = 50, **kwargs):
        Transform_Fct.__init__(self, trace, parent, **kwargs)
        self.alpha = lambda t: final_update_rate + (1-final_update_rate)*_np.exp(-t/decay_rate)
        self.max_time = 10*decay_rate
        self.final_alpha = final_update_rate
        self.time = 0
        self.y = 0
    
    def fct(self, x, y):
        if self.time < self.max_time:
            alpha = self.alpha(self.time)
            self.time += 1
        else:
            alpha = self.final_alpha
        self.y = self.y*(1-alpha) + alpha * y
        
        return x, self.y

#------------------------------------------------------------------------------
#                      Special Transform
#------------------------------------------------------------------------------
class NoTransform(Transform_Fct):
    def fct(self,x,y):
        return x,y

class Custom_f(Transform_Fct):
    # In this case, the transform as already been set, so we overwrite set 
    # transform to do nothing
    def setTransform(self):
        self.fct = self.trace.transform
        self.trace.signal_newData.emit(self.trace.name)