# -*- coding: utf-8 -*-
"""
@author: AlexBourassa
        
@TODO:  Copy and delete feature (perhaps using keyboard Ctrl-C/Ctrl-V and Delete)        
        
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
        
        self.initTreeWidget()
        
        self.treeWidget.itemPressed.connect(self.itemPressed)
        #self.treeWidget.dragEnterEvent = self._dragEnterEvent
        
    def initTreeWidget(self):
        self.treeWidget.clear()
        self.treeWidget.setAcceptDrops(True)
        self.treeWidget.setDragEnabled(True)
        self.treeWidget.setDragDropMode(_gui.QAbstractItemView.InternalMove)
        self.treeWidget.dropEvent = self._dropEvent
        self.treeWidget.header().close()     
        
              
        self.root = self.treeWidget.invisibleRootItem()
        self.root.setFlags(self.root.flags() & ~_core.Qt.ItemIsDropEnabled)
    
    def itemPressed(self, item, col):
        #If the item pressed was not a graph, but a trace
        if item.name not in self.items:
            self.pressedItem = item, item.parent().name
        return
        
    # The underscore avoids conflicting with the QObject dropEvent
    def _dropEvent(self, event):
        """
        This will overwrite the treeWidget DropEvent
        """
        #Call the QTreeWidet dropEvent
        _gui.QTreeWidget.dropEvent(self.treeWidget, event)
        
        #Find the trace and graph item
        trace_item, old_parent_name = self.pressedItem
        graph_item = trace_item.parent()
        
        #Remove the item from the new parent
        graph_item.removeChild(trace_item)
        
        # Add a new trace in the new parent (we remove then add beacause the
        # name might change)
        self.widgets[graph_item.name].copyTrace(self.widgets[old_parent_name][trace_item.name])
        
        #Remove trace from old parent
        self.widgets[old_parent_name].removeTrace(trace_item.name)
        self.items[old_parent_name].removeTraceItem(trace_item.name)
        
        

    def addGraph(self, graph_name, graph_widget):
        self.widgets[graph_name] = graph_widget
        self.items[graph_name] = GraphTreeWidgetItem(self, graph_name)
        
    def __iter__(self):
        k = list(self.items.keys())
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
        self.graph = self.parent.widgets[self.name]
        self.trace_items = dict()
        
        self.graph.traceAdded.connect(lambda x: self.updateTreeItem())
        self.graph.traceRemoved.connect(lambda x: self.updateTreeItem())        
        
        self.updateTreeItem()
        
        
    def updateTreeItem(self):
        """
        Add the missing elements to the item, and remove the extra ones
        """
        removeList = self.getTreeItemNameList()
        #Add the missing items
        for trc in list(self.graph.traces.keys()):
            if not trc in self.trace_items:
                self.addTraceItem(trc)
            elif trc in removeList:
                removeList.remove(trc)
        
        #Remove the extra items
        for trc in removeList:
            if trc in self.trace_items: self.removeTraceItem(trc)
        
    def removeTraceItem(self, trc):
        self.removeChild(self.trace_items.pop(trc))
        
    def addTraceItem(self, trc):
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
            elif self.child(i).name in removeList:
                removeList.remove(self.child(i).name)
            #Handles the case were a second trace of the same name was added
            else:
                addList.append(self.child(i).name)
        return addList, removeList
        
    def getTreeItemNameList(self):
        ans = list()
        for i in range(self.childCount()):
            ans.append(self.child(i).name)
        return ans
            
    def __iter__(self):
        k = list(self.trace_items.keys())
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
          
            
            
            