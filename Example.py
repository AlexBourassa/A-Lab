# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 14:57:06 2015

@author: Alex
@BUG: I have to load Widgets.IPythonConsoleWidget first or else PyQt defaults
      to V1. (ie ?import IPython.qt.console.rich_ipython_widget? does something to
      make sure we're on V2.)
"""

#import os as _os
#_os.environ['QT_API'] = 'pyside'# 'pyqt' for PyQt4 / 'pyside' for PySide
#from QtVariant import QtGui as _gui
#from QtVariant import QtCore as _core

#import sip,os
#sip.setapi('QVariant', 2)

#env_api = os.environ.get('QT_API', 'pyqt')
#os.environ['QT_API'] = 'pyqt'


#Bug: I have to load this one first or else PyQt defaults to V1
import Widgets.IPythonConsoleWidget as _ipy
from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

from Module_Container import *

class example(Module_Container):
    
    def __init__(self, **kw):
        #Initialize the windows
        super(example, self).__init__(**kw)
       
        self.plugins = dict()
        self.plugins['View_Menu'] = View_Menu(self)

        #Create widget 1 with some traces
        w1 = _graph.PyQtGraphWidget()
        w1['t1'] = {'x':x, 'y':y, 'pen':'y'}
        w1.addTrace('t2', x=x, y=_np.sin(x), pen='r')
        w1.addTrace('t3', y=x)
        
        def test():
            print 'alex'
            
        w1.hide_signal.connect(test)
        
        w2 = _graph.PyQtGraphWidget()
        
        w3 = _ipy.Easy_RichIPythonWidget(connection_file = u'kernel-example.json', font_size=12)
        
        w4 = TraceManagerWidget()
        
        for wi in [w1,w2,w3,w4]:
            self.addModule('mod', wi, initial_pos = _core.Qt.TopDockWidgetArea)
        
        w4.addGraph('mod',w1)
        #w4.addGraph('mod2',w2)        
        
        self.loadUISettings()
        
        self.show()
        



if __name__ == "__main__":

    
    #uiThread = _core.QThread()
    app = _gui.QApplication([])
    
    # Create and display the splash screen
    splash_pix = _gui.QPixmap('splash_loading.png')
    splash = _gui.QSplashScreen(splash_pix, _core.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # Do all other imports here
    import IPython
    from IPython.utils.frame import extract_module_locals
    import numpy as _np
    import Widgets.GraphWidget.GraphWidget as _graph
    import Widgets.IPythonConsoleWidget as _ipy
    from Module_Container_Plugins.View_Menu import View_Menu
    from Widgets.TraceManagerWidget import TraceManagerWidget
    
    
    x = _np.linspace(0,4*_np.pi)
    y = _np.cos(x)
    win = example()
#    #win = Module_Container(default_folder = _os.getcwd())    
#    
#    #Create widget 1 with some traces
#    w1 = _graph.PyQtGraphWidget()
#    
#    win.addModule('graph1', w1, initial_pos = _core.Qt.TopDockWidgetArea)
#    win['graph1']['t1'] = {'x':x, 'y':y, 'pen':'y'}
#    win['graph1'].addTrace('t2', x=x, y=_np.sin(x), pen='r')
#    win['graph1'].addTrace('t3', y=x)
#
#    w2 = _graph.PyQtGraphWidget()
#    win.addModule('graph2', w2, initial_pos = _core.Qt.TopDockWidgetArea)
#    
#    #w3 = _ipy.Easy_RichIPythonWidget(connection_file = u'kernel-example.json', font_size=12) 
#    #win.addModule('console', w3, initial_pos = _core.Qt.TopDockWidgetArea)
#    
#    def test():
#        print 'alex'
#        raise Exception("test")
#    win['graph1'].hide_signal.connect(test)
    
    # Runs a new IPython kernel, that begins the qt event loop.
    #
    # Other options for the ipython kernel can be found at:
    # https://ipython.org/ipython-doc/dev/config/options/kernel.html
    #
    # To connect to the kernel use the info in C:\Users\Alex\.ipython\profile_default\security\kernel-example.json
    (current_module, current_ns) = extract_module_locals(depth=0)
    IPython.start_kernel(user_ns = current_ns, 
                         exec_lines=[u'splash.finish(win)'],#u'win = example()', u'splash.finish(win)'], 
                         gui='qt', 
                         connection_file='kernel-example.json')




        
            