
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))

import socks
import socket
from . import config_data
from .svc_tunnel import SetSocks5Tunnel


class TunnelProxy():
    def __init__(self, logger, verbose, proxy_host: str = "localhost", proxy_port: int = 1080):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.logger = logger
        self.verbose = verbose
        self.bastion_host = config_data.get('bastion_host')
        self.local_port = config_data.get('local_port')
        self.bastion_user = config_data.get('bastion_user')
        self.tunnel = config_data.get('tunnel')

        
    def set_proxy(self):
        if self.tunnel:
            self.logger.info(f"Setting up the application to use the tunnel at local-port {self.local_port}")
            set_verbose = {
                            'verbose': self.verbose, 
                            'logger': self.logger, 
                            'logging': None, 
                            'bastion_host': self.bastion_host, 
                            'local_port': self.local_port, 
                            'bastion_user': self.bastion_user
                        }
            tunnel = SetSocks5Tunnel(set_verbose=set_verbose)
            status = tunnel.is_tunnel_active()
            if self.verbose in [2]:
                print (f"-> tunnel status: {status}")
            if status:
                self.test_proxy(22)
            else:
                self.logger.error(f"Application can not use the tunnel, it is not running, check tunnel status with 'cla tunnel status'")
                if self.verbose in [1,2]:
                    print (f"** Application can not use the tunnel, it is not running, check tunnel status with 'cla tunnel status'")
                sys.exit(1)
        else:
            print (f"-> Tunnel to BastionHost is not configured, if needed please run 'cla tunnel setup'")
            self.logger.debug(f"Tunnel to BastionHost is not configured, if needed please run 'cla tunnel setup'")

    
    def test_proxy(self, test_port=22):
        self.logger.info(f"Testing the tunnel at remote-port {test_port}")
        try:
            socks.set_default_proxy(socks.SOCKS5, self.proxy_host, self.proxy_port)
            socket.socket = socks.socksocket
            socket.socket().connect((self.bastion_host, test_port))
            self.logger.debug(f"Application ready to use the tunnel. Tunnel tested at remote-port {test_port}")
            if self.verbose in [2]:
                print (f"-> Application ready to use the tunnel. Tunnel tested at remote-port {test_port}") 
        except (socks.ProxyConnectionError, socket.error):
            self.logger.error(f"Application can not use the tunnel, tunnel is not Up and Running")
            print (f"** Application can not use the tunnel, tunnel is not Up and Running. Start tunnel with 'cla tunnel setup'")
            sys.exit(1)