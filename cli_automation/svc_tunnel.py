# SOCK5 Tunnel Service Class
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))

import asyncio
import json
from .svc_files import ManageFiles
from cli_automation import config_data
import socket
import requests
import subprocess
import socks


class SetSocks5Tunnel():
    def __init__(self, inst_dict: dict):
        self.verbose = inst_dict.get('verbose')
        self.logger = inst_dict.get('logger')
        self.cfg = config_data
        self.file = ManageFiles(self.logger)

    
    def is_tunnel_active(self, local_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", local_port)) == 0
        
        
    async def check_remote_ip(self, local_port):
        proxies = {
            "http": f"socks5h://localhost:{local_port}",
            "https": f"socks5h://localhost:{local_port}"
        }
        try:
            ip = requests.get("https://api64.ipify.org", proxies=proxies, timeout=5).text
            if self.verbose in [2]:
                print(f"\n** The public IP through the tunnel is: {ip}")
            self.logger.debug(f"The public IP through the tunnel is: {ip}")
        except requests.RequestException:
            if self.verbose in [2]:
                print("\n** Failed to obtain the IP through the tunnel")
            self.logger.error("Failed to obtain the IP through the tunnel")


    def get_pid(self):
        command_pre = ["lsof", "-t", f"-i:{self.cfg.get("tunnel_local_port")}"]
        try:
            result = subprocess.run(command_pre, capture_output=True, text=True)
            pid = result.stdout.strip() if result.stdout.strip() else None
            self.logger.debug(f"Getting tunnel process PID. PID found: {pid}")
            return pid
        except subprocess.CalledProcessError as error:
            print (f"\n** Error checking the PID: {error.stderr}")
            self.logger.error(f"Error checking the PID: {error.stderr}")
            sys.exit(1)


    async def start_socks5_tunnel(self, timeout, bastion_user, bastion_host, local_port):
        self.logger.debug(f"Starting the tunnel to the Bastion Host {bastion_host}, user: {bastion_user}, local-port: {local_port}")
        command = f"ssh -N -D {local_port} -f {bastion_user}@{bastion_host}"
        try:
            subprocess.run(command, shell=True, check=True, timeout=timeout)
            pid = self.get_pid()
            if self.verbose in [1,2]:
                print(f"-> Tunnel process PID {pid}")
            return pid, None
        except Exception as error:
            self.logger.error(f"Error starting the tunnel: {error}")
            return None, f"** Error starting the tunnel: {error}"

    
    async def start_tunnel(self, timeout, bastion_user, bastion_host, local_port):
        if self.verbose in [1,2]:
            print(f"-> Setting up the tunnel to the Bastion Host {bastion_user}@{bastion_host}, local-port {local_port}")
        self.logger.info(f"Setting up the tunnel to the Bastion Host {bastion_host}, user: {bastion_user}, local-port: {local_port}")
        self.logger.debug(f"Checking if tunnel is up, local-port: {local_port}, status: {self.is_tunnel_active(local_port=local_port)}")
        if self.is_tunnel_active(local_port=local_port):
            pid = self.get_pid()
            self.logger.info(f"Tunnel already running (PID {pid})")
            return pid, f"-> Tunnel already running (PID {pid})"
        else:
            pid, msg = await self.start_socks5_tunnel(timeout=timeout, bastion_user=bastion_user, bastion_host=bastion_host, local_port=local_port)
            self.logger.debug(f"Checking if tunnel is up, local-port: {local_port}, status: {self.is_tunnel_active(local_port=local_port)}")
            if self.is_tunnel_active(local_port=local_port):
                self.cfg['bastion_host'] = bastion_host
                self.cfg['bastion_user'] = bastion_user
                self.cfg['tunnel_local_port'] = local_port
                self.cfg['tunnel'] = True
                config_data_file = self.cfg.copy()
                del config_data_file["version"]
                self.logger.debug(f"Tunnel status updated to True")
                await self.file.create_file("config.json", json.dumps(config_data_file, indent=2))
                self.logger.debug(f"Tunnel started successfully for user: {bastion_user}, bastion host: {bastion_host}, local-port: {local_port}, PID: {pid}")
                await self.check_remote_ip(local_port=local_port)
            return pid, msg


    async def kill_tunnel(self):
        pid_result = subprocess.run(["lsof", "-t", f"-i:{self.cfg.get("tunnel_local_port")}"], capture_output=True, text=True)
        pid = pid_result.stdout.strip()
        if pid:
            try:
                command = ["kill", "-9", pid]
                print (f"-> Killing the tunnel to the Bastion Host, local port {self.cfg.get("tunnel_local_port")}, process {pid}")
                self.logger.info(f"Killing the tunnel to the Bastion Host, local port {self.cfg.get("tunnel_local_port")}, process {pid}")
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode == 0:
                    self.cfg['tunnel'] = False
                    config_data_file = self.cfg.copy()
                    del config_data_file["version"]
                    await self.file.create_file("config.json", json.dumps(config_data_file, indent=2))
                    self.logger.debug(f"Tunnel status updated to False")
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

    async def tunnel_status(self, timeout, test_port, local_port):
        self.logger.info(f"Checking if tunnel is up, local-port: {local_port}, status: {self.is_tunnel_active(local_port=local_port)}")
        if self.is_tunnel_active(local_port=local_port):
            self.logger.debug(f"Checking if proxy is active, local-port: {local_port}, test-port: {test_port}, timeout: {timeout}")
            if self.test_proxy(timeout=timeout, test_port=test_port, local_port=local_port):
                self.logger.debug(f"Tunnel is running at local-port {local_port}")
                self.cfg['tunnel'] = True
                config_data_file = self.cfg.copy()
                if self.cfg.get("version"):
                    del config_data_file["version"]
                self.logger.debug(f"Tunnel status updated to True")
                await self.file.create_file("config.json", json.dumps(config_data_file, indent=2))
                return True
            else:
                self.logger.error(f"Application can not use the tunnel, tunnel is not running or bastion-host not reachable. Reset the tunnel")
                self.cfg['tunnel'] = False
                config_data_file = self.cfg.copy()
                if self.cfg.get("version"):
                    del config_data_file["version"]
                self.logger.debug(f"Tunnel status updated to False")
                await self.file.create_file("config.json", json.dumps(config_data_file, indent=2))
                return False
        else:
            self.logger.debug(f"Tunnel is not running at local-port {local_port}")
            self.cfg['tunnel'] = False
            config_data_file = self.cfg.copy()
            del config_data_file["version"]
            self.logger.debug(f"Tunnel status updated to False")
            await self.file.create_file("config.json", json.dumps(config_data_file, indent=2))
            return False
     

    def test_proxy(self, timeout, test_port, local_port):
        self.logger.debug(f"Testing the tunnel at remote-port: {test_port}, local-port: {local_port}, timeout: {timeout}, proxy: {self.cfg.get("proxy_host")}, bastion: {self.cfg.get("bastion_host")}")
        try:
            proxy = self.cfg.get("proxy_host")
            bastion = self.cfg.get("bastion_host")
            socks.set_default_proxy(socks.SOCKS5, self.cfg.get("proxy_host"), local_port)
            socket.socket = socks.socksocket
            socket.setdefaulttimeout(timeout)
            socket.socket().connect((self.cfg.get("bastion_host"), test_port))
            self.logger.debug(f"Application ready to use the tunnel. Tunnel tested at remote-port {test_port}")
            return True
        except (socks.ProxyConnectionError, socket.error):
            self.logger.error(f"Application can not use the tunnel. Tunnel not tested at remote-port {test_port}")
            return False
        except Exception as error:
            self.logger.error(f"Application can not use the tunnel. Eror: {error}")
            return False