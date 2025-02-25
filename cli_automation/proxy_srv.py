import socks
import socket
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))
from . import config_data


class TunnelProxy:
    def __init__(self, logger, verbose, proxy_host: str = "localhost", proxy_port: int = 1080):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.logger = logger
        self.verbose = verbose

    # async def handle_read_file(self):
    #         mf = ManageFiles(self.logger)
    #         content = await mf.read_file("config.json")  # Await the coroutine
    #         return content

    # def set_proxy(self):
    #     loop = asyncio.get_event_loop()
    #     if loop.is_running():
    #         task = loop.create_task(self.handle_read_file())  # Schedule the coroutine
    #         task.add_done_callback(lambda t: self.get_result(t.result()))
    #     else:
    #         result = loop.run_until_complete(self.handle_read_file())
    #         self.get_result(result)
        
    def set_proxy(self):
        if config_data.get('tunnel'):
            socks.set_default_proxy(socks.SOCKS5, self.proxy_host, self.proxy_port)
            socket.socket = socks.socksocket
            self.logger.info(f"\n-> Setting up the application to use the SOCKS5 tunnel, proxy-host: {self.proxy_host}, local-port: {self.proxy_port}")
            print (f"\n-> Setting up the application to use the SOCKS5 tunnel, proxy-host: {self.proxy_host}, local-port: {self.proxy_port}")
        else:
            self.logger.info(f"\n-> Application can not use the SOCKS5 tunnel, tunnel is not Up and Running")
            print (f"\n-> Application can not use the SOCKS5 tunnel, tunnel is not Up and Running")
