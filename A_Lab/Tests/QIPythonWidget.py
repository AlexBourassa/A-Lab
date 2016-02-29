import atexit


from PyQt4 import QtGui as _gui

from IPython.lib.kernel import find_connection_file
from IPython.qt.manager import QtKernelManager
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget



class QIPythonWidget(RichIPythonWidget):


    def __init__(self, parent=None, colors='linux', instance_args=[]):
        super(QIPythonWidget, self).__init__()
        #self.app = self.KernelApp.instance(argv=instance_args)
        #self.app.initialize()
        self.set_default_style(colors=colors)
        self.connect_kernel('kernel-example.json')

    def connect_kernel(self, conn, heartbeat=False):
        km = QtKernelManager(connection_file=find_connection_file(conn))
        km.load_connection_file()
        km.start_channels(hb=heartbeat)
        self.kernel_manager = km
        atexit.register(self.kernel_manager.cleanup_connection_file)

    def get_user_namespace(self):
        return self.app.get_user_namespace()


if __name__ == "__main__":

    
    #uiThread = _core.QThread()
    app = _gui.QApplication([])
    