# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

This is an example of how to make a simple Network Analyzer App
"""


#@Bug: I have to load this one first or else PyQt defaults to V1...
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core
import os as _os

import A_Lab.Module_Container as _Module_Container
from A_Lab.Apps.Network_Analyzer.e8364b_gui import E8364B_GUI

class NA_Win(_Module_Container.Module_Container):


    def __init__(self, network_analyzer, **kw):

        # Initialize the super class
        super(NA_Win, self).__init__(**kw)

        #Create 3 new widgets
        self.console = ConsoleWidget()
        self.param_tree = Hiar_Param_Tree(file_handler=None)

        #Add widgets to the main windows
        self.addModule('console', self.console, initial_pos=_core.Qt.TopDockWidgetArea)
        self.addModule('param_tree', self.param_tree, initial_pos=_core.Qt.TopDockWidgetArea)

        #Add the na
        self.na = network_analyzer
        generateLantzParams(self.param_tree, self.na)
        self.na_widget = E8364B_GUI(parent=self, device=self.na, period = 300)
        self.addModule('na_widget', self.na_widget, initial_pos=_core.Qt.TopDockWidgetArea)

        # Enables autosave (for windows settings).  I disable it at the start so it only
        # saves if everything loaded well.  Very useful for debugging, but
        # also probably a good thing to do in general.
        self.params['autoSave'] = True





if __name__=='__main__':
    # uiThread = _core.QThread()
    app = _gui.QApplication([])

    # Create and display the splash screen
    im_path = _os.path.join(_os.path.dirname(_Module_Container.__file__), 'SplashScreen.png')
    splash_pix = _gui.QPixmap(im_path)
    splash = _gui.QSplashScreen(splash_pix, _core.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()


    # User code
    # ------------------------------------------------------------------------------
    from IPython.utils.frame import extract_module_locals
    import numpy as _np
    import sys as _sys

    from A_Lab.Widgets.GraphWidget import GraphWidget as _graph
    from A_Lab.Widgets.ConsoleWidget import ConsoleWidget
    from A_Lab.Widgets.Hiar_Param_Tree import Hiar_Param_Tree

    from lantz.drivers.keysight.e8364b import E8364B
    from A_Lab.Others.LantzAddOns import generateLantzParams
    from lantz.log import log_to_screen, DEBUG, INFO, CRITICAL
    log_to_screen(DEBUG)

    # Create the network analyzer object
    na = E8364B('TCPIP0::192.168.1.106::5025::SOCKET')
    na.initialize()

    #Create the UI
    win = NA_Win(network_analyzer = na, autoSave=False, standardPlugins=True)


    # Create a console widget, add it to the window and push the current
    # current namespace to it
    (current_module, current_ns) = extract_module_locals(depth=0)
    win.console.push(current_ns)
    # ------------------------------------------------------------------------------

    # Kill the splash screen to indicate everything is done loading
    splash.finish(win)

    # Begin the UI event loop
    _sys.exit(app.exec_())













