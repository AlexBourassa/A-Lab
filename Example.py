# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

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

import sys as _sys

# This line is just temporary, in practice I will put this in th site-package
# it should be necessary
_os.path.join(_os.getcwd())

#@Bug: I have to load this one first or else PyQt defaults to V1...
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

import Module_Container as Module_Container

class example(Module_Container.Module_Container):
    """
    Here is an example of how to build a UI by putting together a whole bunch
    pre-made widgets.  
    """
    
    def __init__(self, **kw):
        #Initialize the windowsb
        super(example, self).__init__(**kw)

        #Create some widgets and objects
        w1 = _graph.PyQtGraphWidget(parent = self)
        w2 = _graph.PyQtGraphWidget(parent = self)
        w3 = ConsoleWidget()
        w4 = TraceManagerWidget()
        w5 = Hiar_Param_Tree(file_handler = None)
        w6 = _2d_graph.PyQtImageWidget(parent = self)

        
        #Add the modules to the container
        for wi in [w1,w2,w3,w4,w5,w6]:
            self.addModule('mod', wi, initial_pos = _core.Qt.TopDockWidgetArea)
        
        #Decide which graph the trace manager deals with (here both graphs)        
        w4.addGraph('mod',w1)
        w4.addGraph('mod2',w2)  
        
        #Add some data
        w1['t'] = {'x':x, 'y':y, 'pen':'y'}
        w1.addTrace('t', x=x, y=_np.sin(x), pen='r')
        w1.addTrace('t', y=0.05*x)
        w2.addTrace('Test_Device', feeder = Test_Device())
        self.im_device = Raster_Test_Device(w6)

        w5['v0'] = 42
        w5['g3/g3.1/g3.1.1/vHey'] = 'hey'
        w5['/g2/asfdg'] = 'asfdf'
        w5['/g1/v1'] = True
        w5['g1/v2'] = 2
        w5.addParam('g1/v2', 10000000, siPrefix = True, suffix = 'Hz') 
        w5.addParam('g1/g1.1/g1_1', 'b', values = ['a','b','c'], type = 'list') 


        #Create a lantz example fungen
        fungen = LantzSignalGenerator('TCPIP::localhost::5678::SOCKET')
        fungen.initialize()
        generateLantzParams(w5, fungen)
        self.fungen = fungen

        # from lantz.ui.widgets import FeatWidget, connect_feat, DictFeatWidget, connect_driver,DriverTestWidget
        # target = self.fungen
        # feat_name = 'dout'
        # feat = target.feats[feat_name]
        #w = DictFeatWidget(None, fungen, feat)
        #w = DriverTestWidget(None, fungen)
        #connect_driver(w, target)
        #self.addModule('feat', w, initial_pos = _core.Qt.TopDockWidgetArea)

        # try:
        #     fungen = LantzSignalGenerator('TCPIP::localhost::5678::SOCKET')
        #     fungen.initialize()
        #     generateLantzParams(w5, fungen)
        #     self.fungen = fungen
        # except:
        #     print("Could not could to a Simulated Lantz Signal Generator, perhaps you didn't launch the 'lantz-sim fungen tcp' process")

        #Experimenting with Phone sensors
#        phone = SensorTCP()
#        phone.signal_newFeeder.connect(lambda name, feeder: w2.addTrace(name, feeder = feeder))
#        self.phone = phone

        
        # Enables autosave.  I disable it at the start so it only
        # saves if everything loaded well.  Very usefull for debugging, but
        # also probably a good thing to do in general.
        self.params['autoSave'] = True
        



# This part is a bit more involved (compared to the creation of the rest of the
# UI), so if you don't feel comfortable with what's happenning here, be 
# carefull...  Things must happen in a specific order:
#       1. Create the App
#       2. Create the Splash Screen (optional)
#       3. Do imports (doing import here is optional, but prefered since it 
#                      means the big time consuming import will be done while
#                      displaying the splash screen is up and showing something
#                      is happening.)
#       4. Do some general variable declaration if necessary.
#       5. Everything after (and including) the main win needs to be done in
#          exec_line of the kernel init. This is a bit awkward and I plan on 
#          spending some time to make this process simpler for the 
#          user later... But for now, it will do!
if __name__ == "__main__": 
    
    #uiThread = _core.QThread()
    app = _gui.QApplication([])
    
    # Create and display the splash screen
    im_path = _os.path.join(_os.path.dirname(Module_Container.__file__), 'SplashScreen.png')
    splash_pix = _gui.QPixmap(im_path)
    splash = _gui.QSplashScreen(splash_pix, _core.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # Do all other imports here (so the splash screen shows that something is happening)
    #import IPython
    from IPython.utils.frame import extract_module_locals
    import numpy as _np
    from Widgets.GraphWidget import GraphWidget as _graph
    from Widgets.TraceManagerWidget import TraceManagerWidget
    from Devices.Test_Device import *
    from Widgets.Hiar_Param_Tree import Hiar_Param_Tree
    from Others.File_Handler import File_Handler
    from Widgets.Graph2D import Graph2D as _2d_graph
    from A_Lab.Widgets.ConsoleWidget import ConsoleWidget

    #@py27 These don't exist in Python 2.7 so you won't be able to use them
    from lantz.drivers.examples import LantzSignalGenerator
    from A_Lab.Others.LantzAddOns import generateLantzParams


    # try:
    #     from lantz.drivers.examples import LantzSignalGenerator
    #     from A_Lab.Others.LantzAddOns import generateLantzParams
    # except:
    #     print("Lantz is a not installed on this Python distribution")


    #Gives me some time to look at the beautiful splash screen
#    import time as _t
#    _t.sleep(3)    
    
    #Do some application specific work (for this example, create some variables)
    x = _np.linspace(0,4*_np.pi, 200)
    y = _np.cos(x)
    

    # Get the current process to be able to kill the kernel from inside the client
    kernel_pid = _os.getpid()

    
    # We can't actually put the code here now, because if the kernel opens up on
    # a new tcp address the connection won't work properly...  This is the awkward
    # part...
    # This is due to the fact that the console is initialized as soon as the windows
    # is started and it will thus try to connect with a non-existent connection file
#------------------------------------------------------------------------------
    #Create the object
    win = example(autoSave=False, standardPlugins=True, kill_kernel_pid=kernel_pid)

    # Here you can add shortcuts for the command line (for example, let's say
    # we use the Test_Device trace from module mod2 a lot)
    trace = win['mod2']['Test_Device']
#------------------------------------------------------------------------------

    # Create a console widget, add it to the window and push the current
    # current namespace to it
    (current_module, current_ns) = extract_module_locals(depth=0)
    win['mod3'].push(current_ns)

    # Kill the splash screen to indicate everything is done loading
    splash.finish(win)

    # Begin the UI event loop
    _sys.exit(app.exec_())
        