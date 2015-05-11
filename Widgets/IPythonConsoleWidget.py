# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 16:36:29 2015

@author: AlexBourassa

This file allows for easy creation of iPython Qt Console Widget

Most of the code comes from Spyder's code (ipythonconsole.py).
I made some quick modification to make it work, but that migth have broken some things...

@TODO:  Add a timer that sends an empty str to be printed out every periodically
        to ensure no prints are miss
"""
import sys, os, atexit


from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib.kernel import find_connection_file
from PyQt4 import QtGui as _gui

from IPython.qt.manager import QtKernelManager

try: # IPython = "<=2.0"
    from IPython.external.ssh import tunnel as zmqtunnel
    import IPython.external.pexpect as pexpect
except ImportError:
    from zmq.ssh import tunnel as zmqtunnel      # analysis:ignore
    try:
        import pexpect                           # analysis:ignore
    except ImportError:
        pexpect = None                           # analysis:ignore
        
        
# Replacing pyzmq openssh_tunnel method to work around the issue
# https://github.com/zeromq/pyzmq/issues/589 which was solved in pyzmq
# https://github.com/zeromq/pyzmq/pull/615
def _stop_tunnel(cmd):
    pexpect.run(cmd)

def openssh_tunnel(self, lport, rport, server, remoteip='127.0.0.1',
                   keyfile=None, password=None, timeout=0.4):
    if pexpect is None:
        raise ImportError("pexpect unavailable, use paramiko_tunnel")
    ssh="ssh "
    if keyfile:
        ssh += "-i " + keyfile
    
    if ':' in server:
        server, port = server.split(':')
        ssh += " -p %s" % port
    
    cmd = "%s -O check %s" % (ssh, server)
    (output, exitstatus) = pexpect.run(cmd, withexitstatus=True)
    if not exitstatus:
        pid = int(output[output.find("(pid=")+5:output.find(")")]) 
        cmd = "%s -O forward -L 127.0.0.1:%i:%s:%i %s" % (
            ssh, lport, remoteip, rport, server)
        (output, exitstatus) = pexpect.run(cmd, withexitstatus=True)
        if not exitstatus:
            atexit.register(_stop_tunnel, cmd.replace("-O forward",
                                                      "-O cancel",
                                                      1))
            return pid
    cmd = "%s -f -S none -L 127.0.0.1:%i:%s:%i %s sleep %i" % (
                                  ssh, lport, remoteip, rport, server, timeout)
    
    # pop SSH_ASKPASS from env
    env = os.environ.copy()
    env.pop('SSH_ASKPASS', None)
    
    ssh_newkey = 'Are you sure you want to continue connecting'
    tunnel = pexpect.spawn(cmd, env=env)
    failed = False
    while True:
        try:
            i = tunnel.expect([ssh_newkey, '[Pp]assword:'], timeout=.1)
            if i==0:
                host = server.split('@')[-1]
                question = ("The authenticity of host <b>%s</b> can't be "
                             "established. Are you sure you want to continue "
                             "connecting?") % host
                reply = _gui.QMessageBox.question(self, 'Warning', question,
                                             _gui.QMessageBox.Yes | _gui.QMessageBox.No,
                                             _gui.QMessageBox.No)
                if reply == _gui.QMessageBox.Yes:
                    tunnel.sendline('yes')
                    continue
                else:
                    tunnel.sendline('no')
                    raise RuntimeError("The authenticity of the host can't be established")
            if i==1 and password is not None:
                tunnel.sendline(password) 
        except pexpect.TIMEOUT:
            continue
        except pexpect.EOF:
            if tunnel.exitstatus:
                raise RuntimeError("Tunnel '%s' failed to start"%cmd)
            else:
                return tunnel.pid
        else:
            if failed or password is None:
                raise RuntimeError("Could not connect to remote host")
                # TODO: Use this block when pyzmq bug #620 is fixed
                # # Prompt a passphrase dialog to the user for a second attempt
                # password, ok = QInputDialog.getText(self, _('Password'),
                #             _('Enter password for: ') + server,
                #             echo=QLineEdit.Password)
                # if ok is False:
                #      raise RuntimeError('Could not connect to remote host.') 
            tunnel.sendline(password)
            failed = True


class Easy_RichIPythonWidget(RichIPythonWidget):
    def __init__(self, connection_file, *args, **kw):
        """
        This Widget simplifies the creation of a QT console
        """
        kernel_manager, kernel_client = self.create_kernel_manager_and_client(connection_file=connection_file)
        RichIPythonWidget.__init__(self, *args, **kw)
        
        
        
        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
        
        self.kernel_manager = kernel_manager
        self.kernel_client = kernel_client
        self.exit_requested.connect(stop)
        
       #------ Public API (for kernels) ------------------------------------------
    def ssh_tunnel(self, *args, **kwargs):
        if sys.platform == 'win32':
            return zmqtunnel.paramiko_tunnel(*args, **kwargs)
        else:
            return openssh_tunnel(self, *args, **kwargs)

    def tunnel_to_kernel(self, ci, hostname, sshkey=None, password=None, timeout=10):
        """tunnel connections to a kernel via ssh. remote ports are specified in
        the connection info ci."""
        lports = zmqtunnel.select_random_ports(4)
        rports = ci['shell_port'], ci['iopub_port'], ci['stdin_port'], ci['hb_port']
        remote_ip = ci['ip']
        for lp, rp in zip(lports, rports):
            self.ssh_tunnel(lp, rp, hostname, remote_ip, sshkey, password, timeout)
        return tuple(lports)


        
    def create_kernel_manager_and_client(self, connection_file=None,
                                         hostname=None, sshkey=None,
                                         password=None):
        """Create kernel manager and client"""
        cf = find_connection_file(connection_file, profile='default')
        kernel_manager = QtKernelManager(connection_file=cf, config=None)
        kernel_client = kernel_manager.client()
        kernel_client.load_connection_file()
        if hostname is not None:
            try:
                newports = self.tunnel_to_kernel(dict(ip=kernel_client.ip,
                                      shell_port=kernel_client.shell_port,
                                      iopub_port=kernel_client.iopub_port,
                                      stdin_port=kernel_client.stdin_port,
                                      hb_port=kernel_client.hb_port),
                                      hostname, sshkey, password)
                (kernel_client.shell_port, kernel_client.iopub_port,
                 kernel_client.stdin_port, kernel_client.hb_port) = newports
            except Exception as e:
                print "Could not open ssh tunnel. The error was:\n\n" + e.message
                return None, None
        kernel_client.start_channels()
        # To rely on kernel's heartbeat to know when a kernel has died
        kernel_client.hb_channel.unpause()
        return kernel_manager, kernel_client
        

def put_ipy(parent):
    kernel_manager = QtInProcessKernelManager()
    kernel_manager.start_kernel()
    kernel = kernel_manager.kernel
    kernel.gui = 'qt4'

    kernel_client = kernel_manager.client()
    kernel_client.start_channels()
    kernel_client.namespace  = parent
    
    #kernel.execute_request("a=1",0, {'silent': False})

    def stop():
        kernel_client.stop_channels()
        kernel_manager.shutdown_kernel()

    layout = _gui.QVBoxLayout(parent)
    widget = RichIPythonWidget(parent=parent)
    layout.addWidget(widget)
    widget.kernel_manager = kernel_manager
    widget.kernel_client = kernel_client
    widget.exit_requested.connect(stop)
    ipython_widget = widget
    ipython_widget.show()
    kernel.shell.push({'widget':widget,'kernel':kernel, 'parent':parent})
    return {'widget':widget,'kernel':kernel}
    
if __name__ == "__main__":

    
    #uiThread = _core.QThread()
    app = _gui.QApplication([])
    
    