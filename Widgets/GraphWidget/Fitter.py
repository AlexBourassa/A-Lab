# -*- coding: utf-8 -*-
"""
@author: Alex

This is based on old code. It works, but may not be optimal or simple...
"""

from Graph_Widget_Plugin import *
from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core
from PyQt4 import uic as _uic
import os as _os

import Fitter_Eq as fit
import numpy as _np


class Fitter(Graph_Widget_Plugin):
    
    def __init__(self, parent_graph, **kwargs):
        """
        This plugin allows the graph to span a control pannel for fitting a Trace
        """
        Graph_Widget_Plugin.__init__(self, parent_graph)
        
        self.menu = self.graph.menu
        self.graph = parent_graph
        self.kwargs = kwargs
        
        #Build view menu
        if not 'Tools' in self.menu:
            self.menu['Tools'] = dict()
            self.menu['Tools']['_QMenu'] = self.menu['_QMenuBar'].addMenu('Tools')
        
        #Add the action
        self.menu['Tools']['New Fitter...'] = _gui.QAction('New Fitter...', self.menu['Tools']['_QMenu'])
        self.menu['Tools']['_QMenu'].addAction(self.menu['Tools']['New Fitter...'])
        self.menu['Tools']['New Fitter...'].triggered.connect(lambda: self.createNewFitter(**kwargs))
        

        
    def createNewFitter(self, **kwargs):
        #Control Pannel Widget
        self.control_widget = Fitter_Control_Widget(self.graph, **kwargs)
        
        # Try adding it as a docked widget, works if the parent of the graph
        # widget was given and is a Module_Container.  If it fails simply show
        # the widget... (still works but less pretty...)
        try: self.graph.parent().requestNewModule.emit("Fitter", self.control_widget, _core.Qt.LeftDockWidgetArea) 
        except: self.control_widget.show()
        
        



class Fitter_Control_Widget(_gui.QWidget):

    def __init__(self, parent_graph, **kwargs):
        """
        This widget is a control pannel for the fitter
        """
        _gui.QWidget.__init__(self) 
        _uic.loadUi(_os.path.join(_os.path.dirname(__file__),'Fitter.ui'), self)
        self.graph = parent_graph
        self.kwargs = kwargs
        self.fitTraces = dict()
        self._fitted_name_association = dict()
        
        self.generateCtrls()
        
        #Build a quick function to remove an item by name from the signal list
        def removeItemByName(name):
            for i in range(self.signalSelect.count()):
                if self.signalSelect.itemText(i)==name:
                    self.signalSelect.removeItem(i)
        self.signalSelect.removeItemByName = removeItemByName
        
        self.graph.traceAdded[str].connect(lambda x: self.signalSelect.addItem(x))
        self.graph.traceRemoved[str].connect(lambda x: self.signalSelect.removeItemByName(x))
        


    def generateCtrls(self):
        
        #Fill in the signal select input
        items = list(self.graph)
        self.signalSelect.addItems(items)
        self.signalSelect.setCurrentIndex(len(items)-1)
        
        #Link fit buttons
        self.fitBtn.clicked.connect(self.fitData)
        self.guessBtn.clicked.connect(self.guessP)        
        
        #Fill the combobox for fit function
        self.fitFct = fit.getAllFitFct()
        self.fitFctSelect.addItems(self.fitFct.keys())
        self.fitFctSelect.currentIndexChanged.connect(self.generateFitTable)
        self.fitFctSelect.setCurrentIndex(self.fitFct.keys().index('Gaussian'))
        
        #Fill in the combobox for error method
        self.errorMethodSelect.addItems(fit.Generic_Fct.allowedErrorMethods) 
        self.errorMethodSelect.setCurrentIndex(fit.Generic_Fct.allowedErrorMethods.index('subtract'))
        
        #Link the output btns
        self.calcOutBtn.clicked.connect(lambda: self.generateOutputTable()) 
        self.exportOutputAllBtn.clicked.connect(lambda: self.exportOutputToClipboard(All=True))
        self.exportOutputValBtn.clicked.connect(lambda: self.exportOutputToClipboard(All=False))
        
        #Dynamically generate the fit variables table
        self.generateFitTable()
        
        
    def generateFitTable(self):
        """
        Delete the current table and regenerate a new one based on the current
        fonction variables.
        """
        #Fetch fct name and variables
        fctName = str(self.fitFctSelect.currentText())
        fctVars = self.fitFct[fctName].getParamList()
        
        #Update Latex
        self.generateLatex()
        
        #Set the size of the table
        self.fitVariableTable.setRowCount(len(fctVars))
        
        #Fill in the table
        self.fitVarInputs = dict()
        ri = 0
        for var in fctVars:
            #Set variable name in collumn 0
            self.fitVariableTable.setCellWidget(ri,0,_gui.QLabel(str(var)))
            
            #Set variable value in collumn 1
            varValue = _gui.QDoubleSpinBox()
            varValue.setDecimals(16)
            varValue.setMaximum(1000000000000000)
            varValue.setMinimum(-1000000000000000)     
            varValue.setValue(1.0)
            self.fitVariableTable.setCellWidget(ri,2,varValue)
            
            #Set the variable constant checkbox in collumn 2
            varConst = _gui.QCheckBox()
            self.fitVariableTable.setCellWidget(ri,1,varConst)                                  
                                                
            #Remember the widgets
            self.fitVarInputs[var] = dict()
            self.fitVarInputs[var]['value'] = varValue
            self.fitVarInputs[var]['const'] = varConst
            
            #Go to next row
            ri += 1
        return
        
    def generateOutputTable(self, p=None):
        """
        Delete the current table and regenerate a new one based on the current
        fonction variables.
        """
        #Fetch fct name and variables
        fctName = str(self.fitFctSelect.currentText())
        
        if p == None:
            #Read p
            p = dict()
            for var in self.fitVarInputs.keys():
                    p[var] = self.fitVarInputs[var]['value'].value()
                    
        #Calculate output        
        outputVal = self.fitFct[fctName].calcOutput(p)
        
        if outputVal == None:
            #No Output variables defined
            self.outputTable.setRowCount(0)
            return
        else:
            self.outputTable.setRowCount(len(outputVal))
        
        #Fill in the table
        ri = 0
        for val in outputVal.keys():
            #Set variable name in collumn 0
            self.outputTable.setCellWidget(ri,0,_gui.QLabel(str(val)))
            
            
            #Set variable value in collumn 1
            outputLabel = _gui.QLabel(str(outputVal[val]))
            outputLabel.setTextInteractionFlags(_core.Qt.TextSelectableByMouse)
            self.outputTable.setCellWidget(ri,1,outputLabel)
            
            #Go to next row
            ri += 1
        return
        

        
#------------------------------------------------------------------------------
#                   Fit parameters and value
#------------------------------------------------------------------------------    
     
    def fitData(self):
        """
        Get all the variables and perform the desired fit
        """
        #Grab the variables and constants
        fctVars = dict()
        fctConst = dict()
        for var in self.fitVarInputs.keys():
            if self.fitVarInputs[var]['const'].isChecked():
                fctConst[var] = self.fitVarInputs[var]['value'].value()
            else:
                fctVars[var] = self.fitVarInputs[var]['value'].value()
        
        #Get the name of the function
        fctName = str(self.fitFctSelect.currentText())
        #Get the error method
        errorMethod = str(self.errorMethodSelect.currentText())
        #Get the trace name
        trc =str(self.signalSelect.currentText())
        
        #Fit the data
        xData, yData = self.graph.getRegionData(trc)
        if len(fctVars) != 0:
            fitData, p = self.fitFct[fctName].performFit(fctVars, _np.array([xData, yData]), const=fctConst, errorMethod=errorMethod)
        else:
            p = fctConst
        
        #Gets the full fit data
        x = self.graph[trc].getData()[0]
        y = self.fitFct[fctName].evaluateFct(p, x)
        
        #Fill the tables
        self.setTableValue(p)
        self.generateOutputTable(p)
        
        #If Add the fit data if not present and update it if present
        if not trc in self._fitted_name_association:
             trace = self.graph.addTrace(trc+' Fit', **self.kwargs)
             self._fitted_name_association[trc] = fit_trc_name = trace.name
             self.fitTraces[fit_trc_name] = trace
        else:
            fit_trc_name = self._fitted_name_association[trc]
        self.fitTraces[fit_trc_name].setData(x,y)
        
    def setTableValue(self, p):
        """
        Set all variables in the table to their associated dictionnary value
        """
        for var in p.keys():
            if self.fitVarInputs.has_key(var):
                self.fitVarInputs[var]['value'].setValue(p[var])
                
    def generateLatex(self):   
        """
        Generate and show the latex equation
        """
        # Get window background color
        bg = self.palette().window().color()
        cl = (bg.redF(), bg.greenF(), bg.blueF())
        
        #Get figure and make it the same color as background
        fig = self.latexMPLholder.figure
        fig.set_edgecolor(cl)
        fig.set_facecolor(cl)

        # Clear figure
        fig.clf()
        
        #Fetch fct name and variables
        fctName = str(self.fitFctSelect.currentText())
        
        #Update Latex
        latex = self.fitFct[fctName].getLatex()
            
        # Set figure title
        self.latexHolder = fig.suptitle(latex, 
                                        y = 0.5,
                                        x = 0.5,
                                        horizontalalignment='center',
                                        verticalalignment='center',
                                        size = 18)
        self.latexMPLholder.draw()
        
    def guessP(self):
        """
        Guess and set the parameters
        """
        #Fetch fct name and variables
        fctName = str(self.fitFctSelect.currentText())
        
        #Data
        data = self.graph.getRegionData(self.signalSelect.currentText())
        
        #Guess the parametters
        p = self.fitFct[fctName].guessP(data[0], data[1])
        
        if p != None:
            #Set the parametters
            self.setTableValue(p)
        else:
            print "No Guessing algorithm defined for this function!"


#------------------------------------------------------------------------------
#                   Other HELPER methods
#------------------------------------------------------------------------------ 

    def exportOutputToClipboard(self, All=True):
        app = _core.QCoreApplication.instance()
        exportStr = ''
        for i in range(self.outputTable.rowCount()):
            if All:
                exportStr += str(self.outputTable.cellWidget(i, 0).text())
                exportStr += '\t'
            exportStr += str(self.outputTable.cellWidget(i, 1).text())
            exportStr += '\n'
        app.clipboard().setText(exportStr)
        
        
    def closeEvent(self, event):
        for trc in self.fitTraces:
            if trc in self.graph: self.graph.removeTrace(trc)
        try: self.graph.parent().requestSelfDestroy.emit()
        except: pass
        _gui.QWidget.closeEvent(self, event)
        
        
    def loadSettings(self, settingsObj = None, **kwargs):
        print 'Loading Fitter...'
        if type(settingsObj) != _core.QSettings:
            print "No QSetting object was provided"
        else:
            self.restoreGeometry(settingsObj.value('Geometry'))
            print "hey"
            lastFunctionUsed = str(settingsObj.value('FunctionName'))
            print lastFunctionUsed
            self.fitFctSelect.setCurrentIndex(self.fitFct.keys().index(lastFunctionUsed))
            
                
        return
        
    def saveSettings(self, settingsObj = None, **kwargs):
        print 'Saving Fitter...'
        if type(settingsObj) != _core.QSettings:
            print "No QSetting object was provided"
        else:
            settingsObj.setValue('Geometry', self.saveGeometry())
            settingsObj.setValue('FunctionName', str(self.fitFctSelect.currentText()))
        return
