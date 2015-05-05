# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 16:00:09 2015

@author: Alex

@TODO:  There is probably a better way to find out what changed i the tree
        without scanning the whole tree... (I added getTreeItemNameList which
        migth simplify the function)
        
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
        self.uniqueID = 0
        
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
        
        
    def _dragEnterEvent(self, event):
        _gui.QTreeWidget.dragEnterEvent(self, event)
        print event
        print 'hey'
        self.e = event
        return
    
    def itemPressed(self, item, col):
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
        print self.widgets[old_parent_name][trace_item.name]
        print graph_item.name
        self.widgets[graph_item.name].copyTrace(self.widgets[old_parent_name][trace_item.name])
        
        #Remove trace from old parent
        self.widgets[old_parent_name].removeTrace(trace_item.name)
        self.items[old_parent_name].removeTraceItem(trace_item.name)
        
        
        
        #Get old uid changes
#        add_uids = dict()
#        for graph_name in self.items:
#            add_uids[graph_name] = self.items[graph_name].uidList
#            self.items[graph_name]
#            new_uids = self.items[graph_name].uidList
        
        
        
#    # The underscore avoids conflicting with the QObject dropEvent
#    def _dropEvent(self, event):
#        """
#        This will overwrite the treeWidget DropEvent
#        """
#        #Call the QTreeWidet dropEvent
#        _gui.QTreeWidget.dropEvent(self.treeWidget, event)
#        
#        
#        #Build a list of what's changed
#        addLists = dict()
#        removeLists = dict()
#        nothingChanged = True
#        for i in self.items:
#            if self.items[i].hasChanged():
#                addLists[i], removeLists[i] = self.items[i].getChanges()
#                nothingChanged = False
#            else:
#                addLists[i], removeLists[i] = [], []
#            print i, addLists[i], removeLists[i]
#                
#        if nothingChanged: return
#        
#        #For each graph
#        for i in self.items:
#            #Check if you can find the trace in the add list of one item
#            #in another item's remove list
#            for trc in addLists[i]:
#                foundTrc = False
#                for j in self.items:
#                    #If we find a match, copy the item into graph i and remove
#                    #from graph j
#                    if trc in removeLists[j]:
#                        #Remove the item that was just dropped
#                        #print event.pos()
#                        #print self.widgets[i].indexAt(event.pos())
#                        
#                        
#                        #Change the trace to the other graph
#                        traceObj = self.widgets[i].copyTrace(self.widgets[j][trc])
#                        self.widgets[j].removeTrace(trc)
#                        print j, trc
#                        
#                        #Switch the TracTreeItem to the other list
#                        if trc in self.items[j].trace_items:
#                            self.items[i].trace_items[traceObj.name] = self.items[j].trace_items.pop(trc)
#                        
#                        #Remove it from the removeList and go to the next trace without error
#                        if trc in removeLists[j]: removeLists[j].remove(trc)
#                        foundTrc = True
#                        break
#                if not foundTrc: 
#                    event.ignore()
#                    raise Exception("Could not locate trace named '" + trc + "' origins...  Cannot add it to '"+i+"'")
#                        
#        #If something is left in the remove list for some reason... (shouldn't happen...)
#        for i in self.items:
#            for trc in removeLists[i]:
#                self.widgets[i].removeTrace(trc)
#                self.items[i].trace_items.pop(trc)
#            #Make sure all lists are up to date
#            self.items[i].updateTreeItem()


    def addGraph(self, graph_name, graph_widget):
        self.widgets[graph_name] = graph_widget
        self.items[graph_name] = GraphTreeWidgetItem(self, graph_name)

    def requestUID(self):
        ans = self.uniqueID
        self.uniqueID +=1
        return ans
        
    def getItemByUID(self, uid):
        for graph_name in self.items:
            childItem = self.items[graph_name].getItemByUID(uid)
            if childItem != None:
                return childItem
        
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
        self.graph = self.parent.widgets[self.name]
        self.trace_items = dict()
        self.requestUID = parent.requestUID
        self.uidList = list()
        
        self.graph.traceAdded.connect(lambda x: self.updateTreeItem())
        self.graph.traceRemoved.connect(lambda x: self.updateTreeItem())        
        
        self.updateTreeItem()
        
        
    def updateTreeItem(self):
        """
        Add the missing elements to the item, and remove the extra ones
        """
        removeList = self.getTreeItemNameList()
        #Add the missing items
        for trc in self.graph.traces.keys():
            if not trc in self.trace_items:
                self.addTraceItem(trc)
            elif trc in removeList:
                removeList.remove(trc)
        
        #Remove the extra items
        for trc in removeList:
            if trc in self.trace_items: self.removeTraceItem(trc)
        
    def removeTraceItem(self, trc):
        self.removeChild(self.trace_items.pop(trc))
        self.updateUIDlist()
        
    def addTraceItem(self, trc):
        self.trace_items[trc] = TraceTreeWidgetItem(self, trc)
        self.updateUIDlist()
        
    def updateUIDlist(self):
        self.uidList = list()
        for i in range(self.childCount()):
            self.uidList.append(self.child(i).uid)
            
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
        
    def removeByName(self, trace_name, takeAll = True):
        for i in range(self.childCount()):
            if self.child(i).name == trace_name: 
                self.takeChild(i)
                self.updateUIDlist()
                if not takeAll: return
                    
    def getItemByUID(self, uid):
        for i in range(self.childCount()):
            if self.child(i).uid == uid: return self.child(i)
        return None
            
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
        self.uid = graph_tree_widget_item.requestUID()
          
            
            
            