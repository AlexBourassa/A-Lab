# -*- coding: utf-8 -*-
"""
@author: Alex

@BUG: I have to load Widgets.IPythonConsoleWidget first or else PyQt defaults
      to V1. (ie ?import IPython.qt.console.rich_ipython_widget? does something to
      make sure we're on V2.)
"""

# Attempt to make this work with both pyside and pyQt (it works but the added
# wasn't worth it...)
        #_os.environ['QT_API'] = 'pyside'# 'pyqt' for PyQt4 / 'pyside' for PySide
        #from QtVariant import QtGui as _gui
        #from QtVariant import QtCore as _core
        
        #import sip,os
        #sip.setapi('QVariant', 2)
        
        #env_api = os.environ.get('QT_API', 'pyqt')

#Make sure to use pyqt
import os as _os
_os.environ['QT_API'] = 'pyqt'

#@Bug: I have to load this one first or else PyQt defaults to V1
import Widgets.IPythonConsoleWidget as _ipy
from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

from Module_Container import *

class example(Module_Container):
    
    def __init__(self, **kw):
        #Initialize the windows
        super(example, self).__init__(**kw)

        #Create some widgets
        w1 = _graph.PyQtGraphWidget(parent = self)
        w2 = _graph.PyQtGraphWidget(parent = self)
        w3 = _ipy.Easy_RichIPythonWidget(connection_file = u'kernel-example.json', font_size=12)
        w4 = TraceManagerWidget()
        device = Test_Device()
        
        #Add the modules to the container
        for wi in [w1,w2,w3,w4]:
            self.addModule('mod', wi, initial_pos = _core.Qt.TopDockWidgetArea)
        
        #Add some data
        w1['t'] = {'x':x, 'y':y, 'pen':'y'}
        w1.addTrace('t', x=x, y=_np.sin(x), pen='r')
        w1.addTrace('t', y=x)
        w2.addTrace('Test_Device', feeder = device)
        
        
        #Decide which graph the trace manager deals with (here both graphs)        
        w4.addGraph('mod',w1)
        w4.addGraph('mod2',w2)        
        
        # Enables autosave (I disable it at the start for debugging so it only
        # saves if everything loaded well)
        self.params['autoSave'] = True
        



if __name__ == "__main__":

    
    #uiThread = _core.QThread()
    app = _gui.QApplication([])
    
    # Create and display the splash screen (this is an image I found on google)
    splash_pix = _gui.QPixmap('SplashScreen.png')
    splash = _gui.QSplashScreen(splash_pix, _core.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # Do all other imports here (so the splash screen shows that something is happening)
    import IPython
    from IPython.utils.frame import extract_module_locals
    import numpy as _np
    import Widgets.GraphWidget.GraphWidget as _graph
    import Widgets.IPythonConsoleWidget as _ipy
    from Widgets.TraceManagerWidget import TraceManagerWidget
    from Widgets.Devices.Test_Device import Test_Device
    
    #Gives me some time to look at the beautifull splash screen
#    import time as _t
#    _t.sleep(3)    
    
    x = _np.linspace(0,4*_np.pi)
    y = _np.cos(x)
    win = example(autoSave=False, standardPlugins=True)

    
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




        
            