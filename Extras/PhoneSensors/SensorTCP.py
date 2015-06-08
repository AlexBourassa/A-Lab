# -*- coding: utf-8 -*-
"""
@author: AlexBourassa

"""

# TODO: Remove this
# Temporary to load the correct library
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget

import subprocess as _subp
import atexit 
from Generic_UI.Widgets.GraphWidget.GraphTrace import Generic_TraceFeeder
import numpy as _np
import os as _os


from PyQt4 import QtCore as _core


import socket

class TCP_Device(_core.QObject):
    
    BUFFER_SIZE = 512
    signal_newData = _core.Signal(object)
    _signal_start_server = _core.Signal()
    
    def __init__(self, listenPort = 5000, setupLocalForwarding = True, dataWindowSize=100, spanThread=True, **kwargs):
        """
        Base Class for a Device which is created in a new thread with a running
        TCP server.  The class will accepts connections on the specified port,
        receive data, parse it and then emit data in the form of an array and/or
        via a feeder (TODO: Decide that...)
        
        listenPort:             gives the TCP port to connect to with the Device
        setupLocalForwarding:   If True, this will span another process that will
                                listen on the specified port and forward the conection
                                to this program on a random port. (this was done
                                because some network were having issues with direct
                                connect (I will need to fix this at some point))
        dataWindowSize:         Specifies the maximum size of the data to buffer
        spanThread:             Places this object in a new thread
        
        """
        _core.QObject.__init__(self)    
        
        if spanThread:
            print "Spanning new Thread..."
            self._thread = _core.QThread()
            self.moveToThread(self._thread)
            self._thread.start()
        
        
        # Make variable stay
        self.PORT = listenPort
        self.dataWindowSize = dataWindowSize
        
        #Create a new socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket
        if setupLocalForwarding:
            # Select a random available port (the OS decides)
            self.socket.bind(('',0))
            
            # Setup a TCP Relay because Python is not receiving outside connection
            # is not receiving outside connections on my system for some reason
            p = _subp.Popen([_os.path.join(_os.path.dirname(__file__),'RELAYTCP'), str(self.PORT), '127.0.0.1',
                            str(self.socket.getsockname()[1])],
                            creationflags=_subp.CREATE_NEW_CONSOLE,
                            stdin=None, stdout=None, stderr=None)
            atexit.register(lambda: p.kill())
        
        else:
            #Directly use the specified port
            self.socket.bind(('', self.PORT))
            
        # Activate the server; this will keep running until you
        # interrupt the program
        self._signal_start_server.connect(self.serve_forever)
        self._signal_start_server.emit()
        
        
    def serve_forever(self):
        """
        This is the main server loop it waits for a connection and then handles it
        ie Checks if some data was received, parses it and emits data
        """
        #Waits for incomming connection
        print "Listening for connection..."
        self.socket.listen(1)
        self.conn, self.connAddr = self.socket.accept()
        print "Openning new connection..."
        
        #Serves it forever (ie until it closes)
        while True:
            data = self.conn.recv(self.BUFFER_SIZE)
            if not data: break
            self.newIncomingStrData(data)
        self.conn.close()
        
        #Wait for a new connection
        self.serve_forever()
        
    def newIncomingStrData(self, s):
        """
        Parses a new incoming str, send out signals and setData
        """
        raise NotImplemented
        



class SensorTCP(TCP_Device):
    feeders = dict()
    dataArrays = dict() #Incoming data buffer
    signal_newFeeder = _core.Signal(str, object)#name, feeder object
    verbose = True
    
    def __init__(self, **kwargs):
        self._timer = _core.QTimer()
        self._timer.timeout.connect(self.updateFeeders)
        self._timer.start(0)
        TCP_Device.__init__(self, **kwargs)
        
    
    def newIncomingStrData(self, s):
        """
        Parses a new incoming str and 
        """
        data = s.split('\n')
        for d in data:
            #Check that the data was fully received (ie that the buffer didn't cut it)
            if len(d)<2:continue #Removes empty items
            if not d[-1] == '}' and d[0]=='{': continue
            d = d[1:-1]#Cut out the {}
            
            try:
                name, d = d.split(':')#Get the name of the channel
                d = d[1:-1]#Cut out the []
                
                #Get the data as an array of float
                d = map(float,d.split(','))
            except:
                if self.verbose: print "Transmission incomplete: Missed a point."
                continue
            
            #Remove bad names   
            if name == '': 
                if self.verbose: print "Transmission incomplete: Missed a point."
                continue
            
            #Create the feeders if they did not exist before
            if not name in self.feeders: 
                self.feeders[name] = list()
                for i in range(len(d)):
                    f = Phone_Feeder()
                    self.feeders[name].append(f)
                    self.signal_newFeeder.emit(name+'_'+str(i), f)
                    
            
            #Create a new data array for each data "kind"
            if not name in self.dataArrays: 
                self.dataArrays[name] = list()
                for i in range(len(d)): 
                    #self.feeders[name][i].addData(_np.array([d[i]]),self.dataWindowSize, setData=True)
                    self.dataArrays[name].append(list())
               
            #Add the data to the array
            for i in range(len(self.dataArrays[name])):
                self.dataArrays[name][i].append(d[i])
        
        
    def updateFeeders(self):
        for name in self.dataArrays:
            for i in range(len(self.dataArrays[name])):
                self.feeders[name][i].addData(_np.array(self.dataArrays[name][i]), self.dataWindowSize, setData=True)
                self.dataArrays[name][i] = list()

        
class Phone_Feeder(Generic_TraceFeeder):
    data = _np.array([])
    x = _np.array([])
    def addData(self, newData, windowSize, setData=True):
        self.data = _np.append(self.data, newData)
        if len(self.data)>windowSize: self.data = self.data[-windowSize:]
        if len(self.data) != len(self.x): self.x = _np.linspace(0,len(self.data)-1, num=len(self.data))
        if setData: self.updateTrace()
        
    def updateTrace(self):
        self.setData(self.x,self.data)
        
    def setData(self, x, y):
        """
        This is a dummy function that will get overwritten when the object is
        associated with a GraphTrace as a feeder.
        """
        return
    
if __name__ == '__main__':
    a= SensorTCP(listenPort = 5000, setupLocalForwarding = True, spanThread=False)