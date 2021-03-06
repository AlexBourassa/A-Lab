"""
@author: AlexBourassa

@details: This file give a method of loading and analysing data.
It currently only supports the Standard_File_Handlers formats (that is data which was saved by a A_Lab) but could be made to eventually support more

"""

#Make sure to use pyqt
import os as _os
_os.environ['QT_API'] = 'pyqt'

#@Bug: I have to load this one first or else PyQt defaults to V1
from qtconsole.rich_jupyter_widget import RichJupyterWidget

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core

import A_Lab.Module_Container as Module_Container

kernel_name = 'kernel-analyzer.json'

class Data_Analyzer(Module_Container.Module_Container):
    """
    Here is an example of how to build a UI by putting together a whole bunch
    pre-made widgets.  
    """
    
    def __init__(self, **kw):
        # Initialize the windows
        super(Data_Analyzer, self).__init__(**kw)

        # Set the window name
        self.setWindowTitle("Data Analyzer")

        # Create some widgets and objects
        self.main_plot      = _graph.PyQtGraphWidget(parent = self)
        self.tree           = Hiar_Param_Tree(file_handler = None)
        self.console        = ConsoleWidget(font_size=12)
        self.trc_manager    = TraceManagerWidget()

        # Add the widgets to the container
        self.addModule('main_plot', self.main_plot, initial_pos = _core.Qt.TopDockWidgetArea)
        self.addModule('tree', self.tree, initial_pos = _core.Qt.TopDockWidgetArea)
        self.addModule('console', self.console, initial_pos = _core.Qt.TopDockWidgetArea)
        self.addModule('trc_manager', self.trc_manager, initial_pos = _core.Qt.TopDockWidgetArea)

        # Add a load save menu which will use custom functions
        self.plugins['View_Menu'] = View_Menu(self)
        self.plugins['Load_Save'] = Load_Save(self, standard_menu = False)
        ls = self.plugins['Load_Save']
        ls.menu['File']['Save'] = ls.menu['File']['_QMenu'].addAction('Save...')
        ls.menu['File']['Save'].triggered.connect(lambda: ls.save())
        ls.menu['File']['Load'] = ls.menu['File']['_QMenu'].addAction('Load...')
        ls.menu['File']['Load'].triggered.connect(lambda: self.loadToMains())

        # Add a plots menu
        self.menu['Plots'] = dict()
        self.menu['Plots']['_QMenu'] = self.menu['_QMenuBar'].addMenu('Plots')
        self.menu['Plots']['Add Plot...'] = _gui.QAction('Add Plot...', self.menu['Plots']['_QMenu'])
        self.menu['Plots']['_QMenu'].addAction(self.menu['Plots']['Add Plot...'])
        def askName_addPlot():
            invalidName = True
            while(invalidName):
                name, ok = _gui.QInputDialog.getText(None, "Plot's name?", "Please enter a name for the new plot:", text="plot")
                name = str(name)
                if name != '': invalidName = False
            if ok: self.addPlot(name)
        self.menu['Plots']['Add Plot...'].triggered.connect(askName_addPlot)

        
        #Decide which graph the trace manager deals with (here both graphs)        
        self.trc_manager.addGraph('main_plot',self.main_plot)

        # Enables autosave.  I disable it at the start so it only
        # saves if everything loaded well.  Very usefull for debugging, but
        # also probably a good thing to do in general.
        self.params['autoSave'] = True
        

    def loadToMains(self):
        """
        Loads all the ::TraceData to self.main_plot and all the ::Hiar_Param_Tree to
        self.tree
        """
        handler = self.plugins['Load_Save']._loadToHandler()
        self.plugins['Load_Save'].loadKey2Mod('::TraceData', 'main_plot', handler = handler)
        self.plugins['Load_Save'].loadKey2Mod('::Hiar_Param_Tree', 'tree', handler = handler, present_in_both = False)

    def addPlot(self, name):
        p = _graph.PyQtGraphWidget(parent = self)
        self.addModule(name, p)
        self.trc_manager.addGraph(name, p)

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
    from IPython.utils.frame import extract_module_locals
    import numpy as _np
    import A_Lab.Widgets.GraphWidget.GraphWidget as _graph
    from A_Lab.Widgets.ConsoleWidget import ConsoleWidget
    from A_Lab.Widgets.TraceManagerWidget import TraceManagerWidget
    from A_Lab.Devices.Test_Device import *
    from A_Lab.Widgets.Hiar_Param_Tree import Hiar_Param_Tree
    from A_Lab.Others.File_Handler import File_Handler
    import A_Lab.Widgets.Graph2D.Graph2D as _2d_graph
    from A_Lab.Module_Container_Plugins.View_Menu import View_Menu
    from A_Lab.Module_Container_Plugins.Load_Save import Load_Save
    import sys as _sys
    

    # Get the current process to be able to kill the kernel from inside the client
    kernel_pid = _os.getpid()

#------------------------------------------------------------------------------
    #Create the object
    win = Data_Analyzer(autoSave=False, standardPlugins=False, kill_kernel_pid=kernel_pid, default_folder = 'C:\\Python27\\Lib\\site-packages\\A_Lab\\Apps\\Data_Analyzer') 

    # Here you can add shortcuts for the command line (for example, let's say
    # we use the Test_Device trace from module mod2 a lot)
    #trace = win['mod2']['Test_Device']
#------------------------------------------------------------------------------

    # Create a console widget, add it to the window and push the current
    # current namespace to it
    (current_module, current_ns) = extract_module_locals(depth=0)
    win.console.push(current_ns)

    # Kill the splash screen to indicate everything is done loading
    splash.finish(win)

    # Begin the UI event loop
    _sys.exit(app.exec_())