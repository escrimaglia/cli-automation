import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))

import asyncio
import json
from .svc_files import ManageFiles
from . import config_data
import socket
import requests
import time
import subprocess
import socks


class SetSocks5Tunnel():
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logging = set_verbose.get('logging')
        self.logger = set_verbose.get('logger')
        self.proxy_host = set_verbose.get('proxy_host')
        self.bastion_host = set_verbose.get('bastion_host', config_data.get('bastion_host'))
        self.local_port = set_verbose.get('local_port', config_data.get('local_port'))
        self.bastion_user = set_verbose.get('bastion_user', config_data.get('bastion_user'))
        self.file = ManageFiles(self.logger)

    
    def is_tunnel_active(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", self.local_port)) == 0
        
        
    async def check_remote_ip(self):
        proxies = {
            "http": f"socks5h://localhost:{self.local_port}",
            "https": f"socks5h://localhost:{self.local_port}"
        }
        try:
            ip = requests.get("https://api64.ipify.org", proxies=proxies, timeout=5).text
            if self.verbose in [2]:
                print(f"** The public IP through the tunnel is: {ip}")
            self.logger.debug(f"The public IP through the tunnel is: {ip}")
        except requests.RequestException:
            if self.verbose in [2]:
                print("** Failed to obtain the IP through the tunnel")
            self.logger.error("Failed to obtain the IP through the tunnel")


    def get_pid(self):
        command_pre = ["lsof", "-t", f"-i:{self.local_port}"]
        try:
            result = subprocess.run(command_pre, capture_output=True, text=True)
            pid = result.stdout.strip() if result.stdout.strip() else None
            self.logger.debug(f"Getting tunnel process PID, command: {result.args}")
            self.logger.debug(f"Tunnel process PID found: {pid}")
            return pid
        except subprocess.CalledProcessError as error:
            print (f"\n** Error checking the PID: {error.stderr}")
            self.logger.error(f"Error checking the PID: {error.stderr}")
            sys.exit(1)


    async def start_socks5_tunnel(self, timeout: int = 15):
        command = f"ssh -N -D {self.local_port} -f {self.bastion_user}@{self.bastion_host}"
        if self.verbose in [1,2]:
            print(f"-> Setting up the tunnel to the Bastion Host {self.bastion_user}@{self.bastion_host}, local-port {self.local_port}")
        self.logger.info(f"Setting up the tunnel to the Bastion Host {self.bastion_host}, user: {self.bastion_user}, local-port: {self.local_port}")
        try:
            subprocess.run(command, shell=True, check=True, timeout=timeout)
            pid = self.get_pid()
            if self.verbose in [1,2]:
                print(f"-> Tunnel process PID {pid}")
            self.logger.debug(f"Tunnel process PID {pid}")
            return pid
        except subprocess.CalledProcessError as error:
            print(f"** Error starting the tunnel: {error}")
            self.logger.error(f"Error starting the tunnel: {error}")
        except subprocess.TimeoutExpired:
            print(f"** Error starting the tunnel: Timeout")
            self.logger.error(f"Error starting the tunnel: Timeout")
        except Exception as error:
            print(f"** Error starting the tunnel: {error}")
            self.logger.error(f"Error starting the tunnel: {error}")

    
    async def start_tunnel(self, timeout: int = 15):
            if self.is_tunnel_active():
                pid = self.get_pid()
                self.logger.info(f"Tunnel already running (PID {pid})")
                if self.verbose in [1,2]:
                    print (f"-> Tunnel already running (PID {pid})")
            else:
                pid = await self.start_socks5_tunnel(timeout=timeout)
                time.sleep(.2)
                if self.is_tunnel_active():
                    config_data['bastion_host'] = self.bastion_host
                    config_data['bastion_user'] = self.bastion_user
                    config_data['local_port'] = self.local_port
                    config_data['tunnel'] = True
                    self.logger.debug(f"Tunnel status updated to True")
                    await self.file.create_file("config.json", json.dumps(config_data, indent=2))
                    self.logger.debug(f"Tunnel started successfully for user: {self.bastion_user}, bastion host: {self.bastion_host}, local-port: {self.local_port}, PID: {pid}")
                    if self.verbose in [1,2]:    
                        print (f"\n** Tunnel started successfully for user: {self.bastion_user}, bastion host: {self.bastion_host}, local-port: {self.local_port}, PID: {pid}")
                    await self.check_remote_ip()


    async def kill_tunnel(self, port: int = 1080):
        pid_result = subprocess.run(["lsof", "-t", "-i:1080"], capture_output=True, text=True)
        pid = pid_result.stdout.strip()
        if pid:
            try:
                command = ["kill", "-9", pid]
                print (f"-> Killing the tunnel to the Bastion Host, local port {port}, process {pid}")
                self.logger.info(f"Killing the tunnel to the Bastion Host, local port {port}, process {pid}")
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode == 0:
                    config_data['tunnel'] = False
                    await self.file.create_file("config.json", json.dumps(config_data, indent=2))
                    self.logger.info(f"Tunnel status updated to False")
                    print (f"\n** Tunnel (PID {pid}) killed successfully")
                    self.logger.debug(f"Tunnel (PID {pid}) killed successfully")
                else:
                    print (f"** Error executing the command: {stderr.decode().strip()}")
                    self.logger.error(f"Error executing the command: {stderr.decode().strip()}")
            except Exception as error:
                print (f"** Error executing the command: {error}")
                self.logger.error(f"Error executing the command: {error}")
                sys.exit(1)
        else:
            print (f"** No tunnel to kill")
            self.logger.info("No tunnel to kill")

    async def tunnel_status(self, timeout: int = 10, test_port: int = 22):
        config_data['bastion_host'] = self.bastion_host
        config_data['bastion_user'] = self.bastion_user
        config_data['local_port'] = self.local_port
        if self.is_tunnel_active():
            if self.test_proxy(test_port=test_port, timeout=timeout):
                self.logger.debug(f"Tunnel is running at local-port {self.local_port}")
                config_data['tunnel'] = True
                self.logger.debug(f"Tunnel status updated to True")
                await self.file.create_file("config.json", json.dumps(config_data, indent=2))
                return True
            else:
                self.logger.error(f"Application can not use the tunnel, tunnel is not running")
                config_data['tunnel'] = False
                self.logger.debug(f"Tunnel status updated to False")
                await self.file.create_file("config.json", json.dumps(config_data, indent=2))
                return False
        else:
            self.logger.debug(f"Tunnel is not running at local-port {self.local_port}")
            config_data['tunnel'] = False
            self.logger.debug(f"Tunnel status updated to False")
            await self.file.create_file("config.json", json.dumps(config_data, indent=2))
            return False

    def test_proxy(self, test_port, timeout):
        self.logger.info(f"Testing the tunnel at remote-port {test_port}")
        try:
            socks.set_default_proxy(socks.SOCKS5, self.proxy_host, self.local_port)
            socket.socket = socks.socksocket
            socket.setdefaulttimeout(timeout)
            socket.socket().connect((self.bastion_host, test_port))
            self.logger.debug(f"Application ready to use the tunnel. Tunnel tested at remote-port {test_port}")
            return True
        except (socks.ProxyConnectionError, socket.error):
            self.logger.error(f"Application can not use the tunnel, tunnel running")
            return False