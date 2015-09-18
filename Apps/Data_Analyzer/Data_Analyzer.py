"""
@author: AlexBourassa

@details: This file give a method of loading and analysing data.
It currently only supports the Standard_File_Handlers formats (that is data which was saved by a Generic_Ui) but could be made to eventually support more

"""

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

from Generic_UI.Module_Container import *

kernel_name = 'kernel-analyzer.json'

class Data_Analyzer(Module_Container):
    """
    Here is an example of how to build a UI by putting together a whole bunch
    pre-made widgets.  
    """
    
    def __init__(self, **kw):
        # Initialize the windowsb
        super(Data_Analyzer, self).__init__(**kw)

        # Set the window name
        self.setWindowTitle("Data Analyzer")

        # Create some widgets and objects
        self.main_plot      = _graph.PyQtGraphWidget(parent = self)
        self.tree           = Hiar_Param_Tree(file_handler = None)
        self.console        = _ipy.Easy_RichIPythonWidget(connection_file = kernel_name, font_size=12)
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
    splash_pix = _gui.QPixmap('SplashScreen.png')
    splash = _gui.QSplashScreen(splash_pix, _core.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # Do all other imports here (so the splash screen shows that something is happening)
    import IPython
    from IPython.utils.frame import extract_module_locals
    import numpy as _np
    import Generic_UI.Widgets.GraphWidget.GraphWidget as _graph
    import Generic_UI.Widgets.IPythonConsoleWidget as _ipy
    from Generic_UI.Widgets.TraceManagerWidget import TraceManagerWidget
    from Generic_UI.Devices.Test_Device import *
    from Generic_UI.Widgets.Hiar_Param_Tree import Hiar_Param_Tree
    from Generic_UI.Others.File_Handler import File_Handler
    import Generic_UI.Widgets.Graph2D.Graph2D as _2d_graph
    from Generic_UI.Module_Container_Plugins.View_Menu import View_Menu
    from Generic_UI.Module_Container_Plugins.Load_Save import Load_Save
    

    # Get the current process to be able to kill the kernel from inside the client
    kernel_pid = _os.getpid()

    
    # We can't actually put the code here now, because if the kernel opens up on
    # a new tcp address the connection won't work properly...  This is the awkward
    # part...
    # This is due to the fact that the console is initialized as soon as the windows
    # is started and it will thus try to connect with a non-existent connection file
#------------------------------------------------------------------------------
    #Create the object
    win = Data_Analyzer(autoSave=False, standardPlugins=False, kill_kernel_pid=kernel_pid, default_folder = 'C:\\Python27\\Lib\\site-packages\\Generic_UI\\Apps\\Data_Analyzer') #This should eventually go in exec_lines, but having it here makes debugging easier...

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
                         connection_file = kernel_name)