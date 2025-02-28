import sys
import asyncio
import json
from .files_srv import ManageFiles
from . import config_data


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
        try:
            process = await asyncio.create_subprocess_exec(
                "lsof", "-t", f"-i:{self.local_port}",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            pid = stdout.decode().strip() if stdout else None
            if not pid:
                self.logger.info("SOCKS5 tunnel not running")
                print (f"\n** SOCKS5 tunnel not running")
            return pid
        except Exception as error:
            print (f"\n** Error checking SOCKS5 tunnel: {error}")
            self.logger.error(f"Error checking SOCKS5 tunnel: {error}")
            return None


    def sync_check_pid(self):
        command_pre = ["lsof", "-t", f"-i:{self.local_port}"]
        try:
            result = self.subprocess.run(command_pre, capture_output=True, text=True, check=True)
            pids = result.stdout.strip().split("\n")
            if len(pids) > 0:
                pid = ",".join(result.stdout.strip().split("\n"))
                self.logger.info(f"SOCKS5 tunnel already running (PID {pid}")
                print (f"\n** SOCKS5 tunnel already running (PID {pid})")
                return pids
            else:
                self.logger.info("SOCKS5 tunnel not running")
                print (f"\n** SOCKS5 tunnel not running")
                return None
        except self.subprocess.CalledProcessError as error:
            print (f"\n** Error checking the PID: {error.stderr}")
            self.logger.info(f"Error checking the PID: {error.stderr}")
            sys.exit(1)


    async def set_tunnel(self):        
        print(f"-> Setting up the SOCKS5 tunnel to the Bastion Host {self.bastion_user}@{self.bastion_host}, local port {self.local_port}")
        try:
            pid = await self.async_check_pid()
            if not pid:
                command = ["ssh", "-D", str(self.local_port), "-N", "-C", f"{self.bastion_user}@{self.bastion_host}"]
                process = await asyncio.create_subprocess_exec(
                    *command, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
                )
                config_data['bastion_host'] = self.bastion_host
                config_data['bastion_user'] = self.bastion_user
                config_data['local_port'] = self.local_port
                config_data['tunnel'] = True
                await self.file.create_file("config.json", json.dumps(config_data, indent=2))
                self.logger.info(f"SOCKS5 tunnel started successfully at {self.bastion_user}@{self.bastion_host}:{self.local_port}")
                print (f"** SOCKS5 tunnel started successfully at {self.bastion_user}@{self.bastion_host}:{self.local_port}")
            else:
                print (f"\n** SOCKS5 tunnel already running (PID: {pid})")
                self.logger.info(f"SOCKS5 tunnel already running (PID: {pid})")
        except Exception as error:
            print (f"** Error setting up SOCKS5 tunnel: {error}")
            self.logger.error(f"Error setting up SOCKS5 tunnel: {error}")
            sys.exit(1)


    async def kill_tunnel(self, port: int = 1080):
        pid_result = self.subprocess.run(["lsof", "-t", "-i:1080"], capture_output=True, text=True)
        pid = pid_result.stdout.strip()
        if pid:
            try:
                command = ["kill", "-9", pid]
                print (f"-> Killing the SOCKS5 tunnel to the Bastion Host, local port {port}, process {pid}")
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode == 0:
                    config_data['tunnel'] = False
                    await self.file.create_file("config.json", json.dumps(config_data, indent=2))
                    self.logger.info(f"Config file updated, tunnel status: False")
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
