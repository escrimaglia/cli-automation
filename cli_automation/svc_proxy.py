# Tunnel Proxy Service Class
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))

import socks
import socket
from . import config_data
from .svc_tunnel import SetSocks5Tunnel


class TunnelProxy():
    def __init__(self, logger, verbose):
        self.logger = logger
        self.verbose = verbose
        self.cfg = config_data

        
    def set_proxy(self):
        if self.cfg.get("tunnel"):
            self.logger.info(f"Setting up the application to use the tunnel at local-port {self.cfg.get('tunnel_local_port')}")
            inst_dict = {'verbose': self.verbose, 'logger': self.logger}
            tunnel = SetSocks5Tunnel(inst_dict=inst_dict)
            status = tunnel.is_tunnel_active(local_port=self.cfg.get('tunnel_local_port'))
            if self.verbose in [2]:
                print (f"-> tunnel status: {status}")
            if status:
                self.test_proxy(test_port=self.cfg.get("tunnel_port_test"), timeout=self.cfg.get("tunnel_timeout"))
            else:
                self.logger.error(f"Application can not use the tunnel, it is not running, check tunnel status with 'cla tunnel status'")
                if self.verbose in [1,2]:
                    print (f"** Application can not use the tunnel, it is not running, check tunnel status with 'cla tunnel status'")
                sys.exit(1)
        else:
            print (f"-> Tunnel to BastionHost is not configured, if needed please run 'cla tunnel setup'")
            self.logger.debug(f"Tunnel to BastionHost is not configured, if needed please run 'cla tunnel setup'")

    
    def test_proxy(self, test_port, timeout):
        self.logger.info(f"Testing the tunnel at remote-port {test_port}")
        try:
            socks.set_default_proxy(socks.SOCKS5, self.cfg.get("proxy_host"), self.cfg.get("tunnel_local_port"))
            socket.socket = socks.socksocket
            socket.setdefaulttimeout(timeout)
            socket.socket().connect((self.cfg.get("bastion_host"), test_port))
            self.logger.debug(f"Application ready to use the tunnel. Tunnel tested at remote-port {test_port}")
            if self.verbose in [2]:
                print (f"-> Application ready to use the tunnel. Tunnel tested at remote-port {test_port}") 
        except (socks.ProxyConnectionError, socket.error):
            self.logger.error(f"Application can not use the tunnel, tunnel is not running")
            print (f"** Application can not use the tunnel, tunnel is not running. Start the tunnel with 'cla tunnel setup'")
            sys.exit(1)