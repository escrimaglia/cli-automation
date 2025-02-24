import socks
import socket
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))
from.files_srv import ManageFiles
import json
import asyncio


class TunnelProxy:
    def __init__(self, proxy_host, proxy_port, logger, verbose):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.logger = logger
        self.verbose = verbose

    async def handle_read_file(self):
            mf = ManageFiles(self.logger)
            content = await mf.read_file("config.json")  # Await the coroutine
            return content

    def set_proxy(self):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            task = loop.create_task(self.handle_read_file())  # Schedule the coroutine
            task.add_done_callback(lambda t: self.get_result(t.result()))
        else:
            result = loop.run_until_complete(self.handle_read_file())
            self.get_result(result)
        
    def get_result(self,result):
        dic_result = json.loads(result)
        if dic_result.get('tunnel'):
            proxy_host = "localhost"
            proxy_port = 1080
            socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
            socket.socket = socks.socksocket
            self.logger.info(f"\n-> Setting up the application to use the SOCKS5 tunnel, proxy-host: {proxy_host}, local-port: {proxy_port}")
            print (f"\n-> Setting up the application to use the SOCKS5 tunnel, proxy-host: {proxy_host}, local-port: {proxy_port}")
        else:
            self.logger.info(f"\n-> Application can not use the SOCKS5 tunnel, tunnel is not Up and Running")
            print (f"\n-> Application can not use the SOCKS5 tunnel, tunnel is not Up and Running")
