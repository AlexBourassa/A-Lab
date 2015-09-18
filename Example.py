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

# This line is just temporary, in practice I will put this in th site-package
# it should be necessary
_os.path.join(_os.getcwd())

#@Bug: I have to load this one first or else PyQt defaults to V1
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

from Module_Container import *

class example(Module_Container):
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
        w3 = _ipy.Easy_RichIPythonWidget(connection_file = u'kernel-example.json', font_size=12)
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
        #Phone sensors
#        phone = SensorTCP()
#        phone.signal_newFeeder.connect(lambda name, feeder: w2.addTrace(name, feeder = feeder))
#        self.phone = phone
        
        #Add some tree parametters (taken from spinmob's example)
        # w5.add_parameter('LOL_WUT', 32.5, type='float')
        # w5.add_parameter('Some Category/Some Other Categ./parameter', '32')
        # w5.add_parameter('Some Category/parameter2', values=dict(a=32,b=45,c=17), value=45, type='list')
        # w5.add_parameter('LOL_WUT/test', 'lsdkjf')
        # w5.add_parameter('Numbers/limits(min=-7_max=0)', -3, type='int', limits=(-7,0), step=0.1)
        # w5.add_parameter('Numbers/Units Too!', 1e-6, type='float', siPrefix=True, suffix='V', step=1e-4)
        # btn=w5.add_button('Some Category/test button')
        # def f(): print "hey"
        # btn.signal_clicked.connect(f)
        
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
    from Devices.Test_Device import *
    from Widgets.Hiar_Param_Tree import Hiar_Param_Tree
    from Generic_UI.Others.File_Handler import File_Handler
    from Generic_UI.Extras.PhoneSensors.SensorTCP import SensorTCP
    import Widgets.Graph2D.Graph2D as _2d_graph
    
    
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
    win = example(autoSave=False, standardPlugins=True, kill_kernel_pid=kernel_pid) #This should eventually go in exec_lines, but having it here makes debugging easier...

    # Here you can add shortcuts for the command line (for example, let's say
    # we use the Test_Device trace from module mod2 a lot)
    #trace = win['mod2']['Test_Device']
#------------------------------------------------------------------------------

    # Runs a new IPython kernel, that begins the qt event loop.
    #
    # Other options for the ipython kernel can be found at:
    # https://ipython.org/ipython-doc/dev/config/options/kernel.html
    #
    # To connect to the kernel use the info in <...>\.ipython\profile_default\security\kernel-example.json
    # where <...> under windows is probably C:\Users\<username>
    (current_module, current_ns) = extract_module_locals(depth=0)
    IPython.start_kernel(user_ns = current_ns, 
                         exec_lines= [u'', u'splash.finish(win)'], 
                         gui='qt', 
                         connection_file='kernel-example.json')


        
            