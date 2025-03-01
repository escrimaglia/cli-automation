import sys
import asyncio
import json
from .files_srv import ManageFiles
from . import config_data
import socket
import requests
import time


class SetSocks5Tunnel():
    def __new__(cls, set_verbose: dict):
        import subprocess
        cls.subprocess = subprocess
        return super().__new__(cls)
    
    
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logging = set_verbose.get('logging')
        self.logger = set_verbose.get('logger')
        self.bastion_host = set_verbose.get('bastion_host')
        self.local_port = set_verbose.get('local_port')
        self.bastion_user = set_verbose.get('bastion_user')
        self.file = ManageFiles(self.logger)

    
    async def async_check_pid(self):
        command = "lsof", "-t", f"-i:{self.local_port}"
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            self.logger.info(f"Checking tunnel process PID command: {command}")
            stdout, _ = await process.communicate()
            pid = stdout.decode().strip() if stdout else None
            if self.verbose in [2]:
                print (f"\n-> Checking tunnel process PID command: {command}")
            if pid:
                self.logger.info(f"SOCKS5 tunnel already running (PID {pid})")
                if self.verbose in [1]:
                    print (f"\n-> SOCKS5 tunnel already running")
                elif self.verbose in [2]:
                    print (f"-> SOCKS5 tunnel already running (PID {pid})")
                return pid
            else:
                self.logger.info("SOCKS5 tunnel not running")
                if self.verbose in [2]:
                    print (f"-> SOCKS5 tunnel not running")
                return None
        except Exception as error:
            print (f"\n** Error checking SOCKS5 tunnel: {error}")
            self.logger.error(f"Error checking SOCKS5 tunnel: {error}")
            return None
    
    async def is_socks5_tunnel_active(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect_ex(("localhost", self.local_port))
            return s
        
    # def check_ip_through_proxy(self):
    #     proxies = {
    #         "http": f"socks5h://localhost:{self.local_port}",
    #         "https": f"socks5h://localhost:{self.local_port}"
    #     }
    #     try:
    #         ip = requests.get("https://api64.ipify.org", proxies=proxies, timeout=5).text
    #         print(f"Tu IP pública a través del proxy SOCKS5 es: {ip}")
    #     except requests.RequestException:
    #         print("No se pudo obtener la IP a través del proxy SOCKS5.")

    def get_pid(self):
        command_pre = ["lsof", "-t", f"-i:{self.local_port}"]
        try:
            result = self.subprocess.run(command_pre, capture_output=True, text=True)
            pid = result.stdout.strip() if result.stdout.strip() else None
            self.logger.info(f"Getting tunnel process PID, command: {result.args}")
            self.logger.info(f"Tunnel process PID found: {pid}")
            return pid
        except self.subprocess.CalledProcessError as error:
            print (f"\n** Error checking the PID: {error.stderr}")
            self.logger.error(f"Error checking the PID: {error.stderr}")
            sys.exit(1)

    async def start_socks5_tunnel(self):
        SSH_CMD = f"ssh -N -D {self.local_port} -f {self.bastion_user}@{self.bastion_host}"
        if self.verbose in [1]:
            padding = "\n"
        elif self.verbose in [2]:
            padding = ""
        print(f"{padding}-> Setting up the SOCKS5 tunnel to the Bastion Host {self.bastion_user}@{self.bastion_host}, local-port {self.local_port}")
        self.logger.info(f"Setting up the SOCKS5 tunnel to the Bastion Host {self.bastion_host}, user: {self.bastion_user}, local-port: {self.local_port}")
        try:
            self.subprocess.run(SSH_CMD, shell=True, check=True)
            pid = self.get_pid()
            if self.verbose in [1]:
                print("-> SOCKS5 tunnel started successfully")
            elif self.verbose in [2]:
                print(f"-> SOCKS5 tunnel started successfully (PID {pid})")
        except self.subprocess.CalledProcessError as error:
            print(f"Error starting the tunnel: {error}")

    async def start_tunnel(self, wait_time: int = 1):
        pid = await self.async_check_pid()
        if not pid:
            await self.start_socks5_tunnel()
            time.sleep(wait_time)
        else:
            if await self.is_socks5_tunnel_active():
                config_data['bastion_host'] = self.bastion_host
                config_data['bastion_user'] = self.bastion_user
                config_data['local_port'] = self.local_port
                config_data['tunnel'] = True
                self.logger.info(f"Tunnel status updated to True")
                await self.file.create_file("config.json", json.dumps(config_data, indent=2))
                self.logger.info(f"SOCKS5 tunnel started successfully for user: {self.bastion_user}, bastion host: {self.bastion_host}, local-port: {self.local_port}")
            else:
                print("El túnel SOCKS5 no está activo.")
    
    def sync_check_pid(self):
        command_pre = ["lsof", "-t", f"-i:{self.local_port}"]
        try:
            result = self.subprocess.run(command_pre, capture_output=True, text=True)
            pid = result.stdout.strip() if result.stdout.strip() else None
            self.logger.info(f"Checking tunnel process PID command: {result.args}")
            self.logger.info(f"Tunnel process PID found: {pid}")
            if self.verbose in [2]:
                print (f"-> Checking tunnel process PID command: {result.args}")
            if pid:
                self.logger.info(f"SOCKS5 tunnel already running (PID {pid})")
                if self.verbose in [2]:
                    print (f"-> SOCKS5 tunnel already running (PID {pid})")
                return pid
            else:
                self.logger.info("SOCKS5 tunnel not running")
                if self.verbose in [2]:
                    print (f"-> SOCKS5 tunnel not running")
                return None
        except self.subprocess.CalledProcessError as error:
            print (f"\n** Error checking the PID: {error.stderr}")
            self.logger.error(f"Error checking the PID: {error.stderr}")
            sys.exit(1)


    # async def set_tunnel(self):        
    #     print(f"-> Setting up the SOCKS5 tunnel to the Bastion Host {self.bastion_user}@{self.bastion_host}, local-port {self.local_port}")
    #     self.logger.info(f"Setting up the SOCKS5 tunnel to the Bastion Host {self.bastion_host}, user: {self.bastion_user}, local-port: {self.local_port}")
    #     try:
    #         pid = self.sync_check_pid()
    #         if not pid:
    #             command = ["ssh", "-D", str(self.local_port), "-N", "-C", "-f", f"{self.bastion_user}@{self.bastion_host}"]
    #             process = await asyncio.create_subprocess_exec(
    #                 *command, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
    #             )
    #             config_data['bastion_host'] = self.bastion_host
    #             config_data['bastion_user'] = self.bastion_user
    #             config_data['local_port'] = self.local_port
    #             config_data['tunnel'] = True
    #             self.logger.info(f"Tunnel status updated to True")
    #             await self.file.create_file("config.json", json.dumps(config_data, indent=2))
    #             self.logger.info(f"SOCKS5 tunnel started successfully for user: {self.bastion_user}, bastion host: {self.bastion_host}, local-port: {self.local_port}")
    #             print (f"\n** SOCKS5 tunnel started successfully at {self.bastion_user}@{self.bastion_host}:{self.local_port}")
    #         else:
    #             print (f"\n** SOCKS5 tunnel already running (PID: {pid})")
    #             self.logger.info(f"SOCKS5 tunnel already running (PID: {pid})")
    #     except Exception as error:
    #         print (f"** Error setting up SOCKS5 tunnel: {error}")
    #         self.logger.error(f"Error setting up SOCKS5 tunnel: {error}")
    #         sys.exit(1)


    async def kill_tunnel(self, port: int = 1080):
        pid_result = self.subprocess.run(["lsof", "-t", "-i:1080"], capture_output=True, text=True)
        pid = pid_result.stdout.strip()
        if pid:
            try:
                command = ["kill", "-9", pid]
                print (f"-> Killing the SOCKS5 tunnel to the Bastion Host, local port {port}, process {pid}")
                self.logger.info(f"Killing the SOCKS5 tunnel to the Bastion Host, local port {port}, process {pid}")
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
                    print (f"\n** SOCKS5 tunnel (PID {pid}) killed successfully")
                    self.logger.info(f"SOCKS5 tunnel (PID {pid}) killed successfully")
                else:
                    print (f"** Error executing the command: {stderr.decode().strip()}")
                    self.logger.error(f"Error executing the command: {stderr.decode().strip()}")
            except Exception as error:
                print (f"** Error executing the command: {error}")
                self.logger.error(f"Error executing the command: {error}")
                sys.exit(1)
        else:
            print (f"** No SOCKS5 tunnel to kill")
            self.logger.info("No SOCKS5 tunnel to kill")
