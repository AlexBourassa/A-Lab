# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 16:00:09 2015

@author: Alex

@TODO:  There is probably a better way to find out what changed i the tree
        without scanning the whole tree...
        
@TODO:  Add a drop from file feature.  Drag a file to the widget and it loads
        it and add it to the graph.
"""

from PyQt4 import QtGui as _gui
from PyQt4 import QtCore as _core
from PyQt4 import uic as _uic
import os as _os

class TraceManagerWidget(_gui.QWidget):
    
    def __init__(self, **kwargs):
        _gui.QWidget.__init__(self)
        _uic.loadUi(_os.path.join(_os.path.dirname(__file__),'TraceManagerWidget.ui'), self)
        self.items = dict()
        self.widgets = dict()
        
        self.treeWidget.setAcceptDrops(True)
        self.treeWidget.setDragEnabled(True)
        self.treeWidget.setDragDropMode(_gui.QAbstractItemView.InternalMove)
        self.treeWidget.dropEvent = self._dropEvent
        self.treeWidget.header().close()        
        
        self.root = self.treeWidget.invisibleRootItem()
        self.root.setFlags(self.root.flags() & ~_core.Qt.ItemIsDropEnabled)
        
    # The underscore avoids conflicting with the QObject dropEvent
    def _dropEvent(self, event):
        """
        This will overwrite the treeWidget DropEvent
        """
        #Call the QTreeWidet dropEvent
        _gui.QTreeWidget.dropEvent(self.treeWidget, event)
        
        #Build a list of what's changed
        addLists = dict()
        removeLists = dict()
        nothingChanged = True
        for i in self.items:
            if self.items[i].hasChanged():
                print i + " has changed!"
                addLists[i], removeLists[i] = self.items[i].getChanges()
                nothingChanged = False
                
        if nothingChanged: return
        
        #For each graph
        for i in self.items:
            #Check if you can find the trace in the add list of one item
            #in another item's remove list
            for trc in addLists[i]:
                foundTrc = False
                for j in self.items:
                    #If we find a match, copy the item into graph i and remove
                    #from graph j
                    if trc in self.items[j]:
                        #Change the trace to the other graph
                        self.widgets[i].copyTrace(self.widgets[j][trc])
                        self.widgets[j].removeTrace(trc)
                        
                        #Switch the TracTreeItem to the other list
                        self.items[i].trace_items[trc] = self.items[j].trace_items.pop(trc)
                        
                        #Remove it from the removeList and go to the next trace without error
                        removeLists[j].remove(trc)
                        foundTrc = True
                        break
                if not foundTrc: 
                    event.ignore()
                    raise Exception("Could not locate trace named '" + trc + "' origins...  Cannot add it to '"+i+"'")
                        
        #If something is left in the remove list for some reason... (shouldn't happen...)
        for i in self.items:
            for trc in removeLists[i]:
                self.widgets[i].removeTrace(trc)
                self.items[i].trace_items.pop(trc)
            #Make sure all lists are up to date
            self.items[i].updateTreeItem()


    def addGraph(self, graph_name, graph_widget):

        self.widgets[graph_name] = graph_widget
        self.items[graph_name] = GraphTreeWidgetItem(self, graph_name)

        
        
    def __iter__(self):
        k = self.items.keys()
        return iter(k)
        
    def __len__(self):
        return len(self.items)
        
    def __getitem__(self, key):
        return self.items[key]
        
        
class GraphTreeWidgetItem(_gui.QTreeWidgetItem):
    
    def __init__(self, parent, graph_name, **kwargs):
        _gui.QTreeWidgetItem.__init__(self, parent.root)
        self.setText(0, graph_name)
        self.setFlags(self.flags() & ~_core.Qt.ItemIsDragEnabled)
        self.name = graph_name
        self.parent = parent
        self.trace_items = dict()
        
        self.updateTreeItem()
        
    def emitDataChanged(self):
        print self.name
        
    def updateTreeItem(self):
        """
        Add the missing elements to the item
        """
        #self.trace_items = dict()
        for trc in self.parent.widgets[self.name].traces.keys():
            if not trc in self.trace_items:
                self.trace_items[trc] = TraceTreeWidgetItem(self, trc)
            
    def hasChanged(self):
        return len(self.trace_items) != self.childCount()
            
    def getChanges(self):
        """
        This scans the item for to detect what entry were added or removed
        """
        #Build a add list
        addList = list()
        removeList = list(self.trace_items.keys())
        for i in range(self.childCount()):
            #If a child item as no entry in the trace_items dict it's been added
            if not self.child(i).name in self.trace_items:
                addList.append(self.child(i).name)
            #Else since it appears in the dict it has not been removed
            else:
                removeList.remove(self.child(i).name)
        return addList, removeList

            
    def __iter__(self):
        k = self.trace_items.keys()
        return iter(k)
        
    def __len__(self):
        return len(self.trace_items)
        
    def __getitem__(self, key):
        return self.trace_items[key]


#This class only exist to associate a name to the TreeWidget Item
class TraceTreeWidgetItem(_gui.QTreeWidgetItem):
    def __init__(self, graph_tree_widget_item, trace_name, **kwargs):
        _gui.QTreeWidgetItem.__init__(self)
        self.setText(0, trace_name)
        self.setFlags(self.flags() & ~_core.Qt.ItemIsDropEnabled)
        self.name = trace_name
        
        graph_tree_widget_item.addChild(self)
          
            
            
            