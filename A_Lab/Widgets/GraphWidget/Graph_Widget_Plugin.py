"""
@author: AlexBourassa
"""

from PyQt4 import QtCore as _core

class Graph_Widget_Plugin(_core.QObject):
    
    def __init__(self, parent_graph):
        _core.QObject.__init__(self)
        self.graph = parent_graph
        
    def loadSettings(self, settingsObj = None, **kwargs):
        """
        Implement this function if your Plugin need some state info from the 
        settings file.  You don't actually need to use the <settingsObj>
        (ie you can create your own files), but using it make the state file
        much simpler (only one file!).
        """
        return
        
    def saveSettings(self, settingsObj = None, **kwargs):
        """
        Implement this function if your Plugin need some state info from the 
        settings file.  You don't actually need to use the <settingsObj>
        (ie you can create your own files), but using it make the state file
        much simpler (only one file!).
        """
        return