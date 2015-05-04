"""
@author: Alex
"""

from PyQt4 import QtCore as _core

class Graph_Widget_Plugin(_core.QObject):
    
    def __init__(self, parent_graph):
        _core.QObject.__init__(self)
        self.graph = parent_graph
        
    def loadSettings(self, container_setting_filename, group_name):
        """
        Implement this function if your Plugin need some state info from the 
        settings file.  You don't actually need to use the <container_setting_filename>
        (ie you can create your own files), but using it make the state file
        much simpler (only one file!).
        """
        return
        
    def saveSettings(self, container_setting_filename, group_name):
        """
        Implement this function if your Plugin need some state info from the 
        settings file.  You don't actually need to use the <container_setting_filename>
        (ie you can create your own files), but using it make the state file
        much simpler (only one file!).
        """
        return