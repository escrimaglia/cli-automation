import sys
import asyncio
import json
from .files_srv import ManageFiles


class SetSocks5Tunnel():
    def __new__(cls, set_verbose: dict):
        import subprocess
        cls.subprocess = subprocess
        return super().__new__(cls)
    
    
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logging = set_verbose.get('logging')
        self.logger = set_verbose.get('logger')

    async def check_pid(self):
        try:
            command_pre = ["lsof", "-t", "-i:1080"]
            check_process = await asyncio.create_subprocess_exec(
                *command_pre,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
            stdout, _ = await check_process.communicate()
            pid = stdout.decode().strip()
            return pid
        except Exception as error:
            print (f"** Error checking the PID: {error}")
            self.logger.error(f"Error checking the PID: {error}")
            sys.exit(1)
        return stdout


    async def set_tunnel(self, jump_user: str, jump_host: str, port: int = 1080):        
        print(f"-> Setting up the SOCKS5 tunnel to the Bastion Host {jump_user}@{jump_host}, local port {port}")
        try:
            pid = await self.check_pid()
            if pid:
                self.logger.info(f"SOCKS5 tunnel already running (PID {pid}")
                print (f"\n** SOCKS5 tunnel already running (PID {pid})")
            else:
                command = ["ssh", "-D", str(port), "-N", "-C", f"{jump_user}@{jump_host}"]
                await asyncio.create_subprocess_exec(
                    *command, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
                )
                self.logger.info(f"SOCKS5 tunnel started successfully at {jump_user}@{jump_host}:{port}")
                print (f"\n** SOCKS5 tunnel started successfully at {jump_user}@{jump_host}:{port}")
                try:
                    mf = ManageFiles(self.logger)
                    content_file = await mf.read_file("config.json")
                    dic_content_file = json.loads(content_file)
                    dic_content_file['tunnel'] = True
                    await mf.create_file("config.json", json.dumps(dic_content_file, indent=2))
                    self.logger.info(f"Config file updated, tunnel status: True")
                except Exception as error:
                    self.logger.error(f"Error reading the file constantes: {error}")
                    sys.exit(1)
        except Exception as error:
            self.logger.error(f"Error setting up SOCKS5 tunnel: {error}")
            sys.exit(1)


    async def kill_tunnel(self, port: int = 1080):
        pid_result = self.subprocess.run(["lsof", "-t", "-i:1080"], capture_output=True, text=True)
        if pid_result.stdout:
            pid = pid_result.stdout.strip()
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
                    try:
                        mf = ManageFiles(self.logger)
                        content_file = await mf.read_file("config.json")
                        dic_content_file = json.loads(content_file)
                        dic_content_file['tunnel'] = False
                    except Exception as error:
                        self.logger.error(f"Error reading the file constantes: {error}")
                        sys.exit(1)
                    await mf.create_file("config.json", json.dumps(dic_content_file, indent=2))
                    self.logger.info(f"Config file updated, tunnel status: False")
                    print (f"\n** SOCKS5 tunnel (PID {pid}) killed successfully")
                    self.logger.info(f"SOCKS5 tunnel (PID {pid}) killed successfully")
                else:
                    print (f"\n** Error executing the command:\n{stderr.decode().strip()}")
                    self.logger.error(f"Error executing the command:\n{stderr.decode().strip()}")
            except Exception as error:
                print (f"\n** Error executing the command: {error}")
                self.logger.error(f"Error executing the command: {error}")
                sys.exit(1)
        else:
            print (f"\n** No SOCKS5 tunnel to kill")
            self.logger.info("No SOCKS5 tunnel to kill")
