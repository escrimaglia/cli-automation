# Service classes for the CLI Automation project
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))
import asyncio
#import aiofiles
from netmiko import ConnectHandler, NetmikoAuthenticationException, NetMikoTimeoutException
import paramiko
from pydantic import ValidationError
from datetime import datetime as dt
#import logging
from .model import Model, Devices, ModelPush, ModelTelnet
from typing import List
import json
from .clilogging import Logger
import socks
import socket


class AsyncNetmikoPull():
    def __new__(cls, set_verbose: dict):
        proxy_host = "localhost"
        proxy_port = 1080
        socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
        socket.socket = socks.socksocket
        return super().__new__(cls)

    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logging = set_verbose.get('logging')
        self.single_host = set_verbose.get('single_host')
        self.logger = Logger("cla.log",self.logging).set_logger()
        

    async def netmiko_connection(self, device: dict, commands: List[str]) -> str:
        try:
            connection = await asyncio.to_thread(ConnectHandler, **device)
            output = []
            for command in commands:
                self.logger.info(f"Executing command {command} on device {device['host'], dt.now()}")
                result = await asyncio.to_thread(connection.send_command, command, use_textfsm=True)
                output.append({command: result})
            await asyncio.to_thread(connection.disconnect)
            return output
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error, {dt.now()}")
            return (f"** Error connecting to {device['host']}, authentication error")
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error, {dt.now()}")
            return (f"** Error connecting to {device['host']}, Timeout error")
        except paramiko.ssh_exception.SSHException as ssh_error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko {ssh_error}, {dt.now()}")
            return (f"** Error connecting to {device['host']}, Paramiko {ssh_error}")
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}, {dt.now()}")
            return (f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}")
        

    def data_validation(self, devices: List[Devices], commands: List[str]) -> None:
        print (devices)
        if self.verbose >= 1:
            print ("->", f"About to execute Data Validation for {devices[0].get('host')}")
        try:
            Model(devices=devices, commands=commands)
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            if self.verbose >= 1:
                print (f" ->, {error}")
            sys.exit(1)


    async def run(self, data: dict) -> dict:
        self.data_validation(data.get('devices'), data.get('commands'))
        tasks = []
        for device in data.get('devices'):
            tasks.append(self.netmiko_connection(device, commands=data.get('commands')))
            if self.verbose >= 1:
                print (f"-> Connecting to device {device['host']}, executing commands {data.get('commands')}")
        results = await asyncio.gather(*tasks)
        output_data = []
        for device, output in zip(data.get('devices'), results):
            output_data.append({"Device": device['host'], "Output": output})
        output_data = output_data[0] if self.single_host else output_data
        return json.dumps(output_data, indent=2)
    

class AsyncNetmikoPushSingle():
    def __new__(cls, set_verbose: dict):
        proxy_host = "localhost"
        proxy_port = 1080
        socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
        socket.socket = socks.socksocket
        return super().__new__(cls)
     
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logging = set_verbose.get('logging')
        self.single_host = set_verbose.get('single_host')
        self.logger = Logger("cla.log",self.logging).set_logger()


    async def netmiko_connection(self, device: dict, commands: List[str]) -> str:
        try:
            connection = await asyncio.to_thread(ConnectHandler, **device)
            output = []
            self.logger.info(f"Configuring the following commands {commands} on device {device['host']}")
            result = await asyncio.to_thread(connection.send_config_set, commands)
            result += await asyncio.to_thread(connection.save_config)
            output.append(result)
            await asyncio.to_thread(connection.disconnect)
            return output
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error")
            return (f"** Error connecting to {device['host']}, authentication error")
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error")
            return (f"** Error connecting to {device['host']}, Timeout error")
        except paramiko.ssh_exception.SSHException as ssh_error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko {ssh_error}")
            return (f"** Error connecting to {device['host']}, Paramiko {ssh_error}")
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}")
            return (f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}")


    def data_validation(self, devices: List[Devices], commands: List[str]) -> None:
        if self.verbose >= 1:
            print ("->", f"About to execute Data Validation for {devices[0].get('host')}")
        try:
            Model(devices=devices, commands=commands)
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            if self.verbose >= 1:
                print (f" ->, {error}")
            sys.exit(1)


    async def run(self, data: dict) -> dict:
        self.data_validation(data.get('devices'), data.get('commands'))
        tasks = []
        for device in data.get('devices'):
            tasks.append(self.netmiko_connection(device, commands=data.get('commands')))
            if self.verbose >= 1:
                print (f"-> Connecting to device {device['host']}, configuring commands {data.get('commands')}")
        results = await asyncio.gather(*tasks)
        output_data = []
        for device, output in zip(data.get('devices'), results):
            output_data.append({"Device": device['host'], "Output": output})
        output_data = output_data[0] if self.single_host else output_data
        
        for output in output_data:
            if isinstance(output.get('Output'), str):
                if "Authentication to device failed" in output.get('Output'):
                    output['Output'] = "Authentication to device failed"
            elif isinstance(output.get('Output'), list):
                output['Output'] = "Successful configuration" if ("Invalid input" or "Error") not in output.get('Output')[-1] else "Configuration failed, check the commands in the configuration file"
        
        return json.dumps(output_data, indent=2)
    
class AsyncNetmikoPushMultiple():
    def __new__(cls, set_verbose: dict):
        proxy_host = "localhost"
        proxy_port = 1080
        socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
        socket.socket = socks.socksocket
        return super().__new__(cls)
     
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logging = set_verbose.get('logging')
        self.single_host = set_verbose.get('single_host')
        self.logger = Logger("cla.log",self.logging).set_logger()
      

    async def netmiko_connection(self, device: dict, commands: List[str]) -> str:
        try:
            connection = await asyncio.to_thread(ConnectHandler, **device)
            output = []
            self.logger.info(f"Configuring the following commands {commands} on device {device['host']}")
            result = await asyncio.to_thread(connection.send_config_set, commands)
            result += await asyncio.to_thread(connection.save_config)
            output.append(result)
            await asyncio.to_thread(connection.disconnect)
            return output
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error")
            return (f"** Error connecting to {device['host']}, authentication error")
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error")
            return (f"** Error connecting to {device['host']}, Timeout error")
        except paramiko.ssh_exception.SSHException as ssh_error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko {ssh_error}")
            return (f"** Error connecting to {device['host']}, Paramiko {ssh_error}")
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}")
            return (f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}")
        
        
    def data_validation(self, devices: Devices, commands: List[str]) -> None:
        if self.verbose >= 1:
            print ("->", f"About to execute Data Validation for {devices.get('host')}")
        try:
            ModelPush(devices=devices, commands=commands)
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            if self.verbose >= 1:
                print (f" ->, {error}")
            sys.exit(1)


    async def run(self, data: List[dict]) -> dict:
        for device in data:
            self.data_validation(device.get('parameters'), device.get('commands'))
        tasks = []
        for device in data:
            parameters = device.get('parameters')
            commands = device.get('commands')
            tasks.append(self.netmiko_connection(parameters, commands=commands))
            if self.verbose >= 1:
                print (f"-> Connecting to device {parameters['host']}, configuring commands {commands}")
        results = await asyncio.gather(*tasks)
        output_data = []
        for device, output in zip(data, results):
            output_data.append({"Device": device.get('parameters').get('host'), "Output": output})
        #output_data = output_data[0] if self.single_host else output_data
        for output in output_data:
            if isinstance(output.get('Output'), list):
                if ("Invalid input" or "Error") not in output.get('Output')[-1]:
                    output['Output'] = "Successful configuration"
                else: 
                    output['Output'] = "Congiguration failed, check the commands in the configuration file"
            elif isinstance(output.get('Output'), str):
                if "Authentication to device failed" in output.get('Output'):
                    output['Output'] = "Authentication to device failed"
            
        return json.dumps(output_data, indent=2)

# class SyncNetmikoTelnet():
#     def __new__(cls, set_verbose: dict):
#         proxy_host = "localhost"
#         proxy_port = 1080
#         socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
#         socket.socket = socks.socksocket
#         return super().__new__(cls)
     
#     def __init__(self, set_verbose: dict):
#         self.verbose = set_verbose.get('verbose')
#         self.logging = set_verbose.get('logging')
#         self.logger = CliLogging(self.logging).set_logging()

#     def device_connect(self, device: dict, command: str) -> List[str]:
#         try:
#             connection = ConnectHandler(**device)
#             connection.send_command_timing(device.get('username'))
#             connection.send_command_timing(device.get('password'))
#             if device.get('secret'):
#                 connection.enable()
#             if self.verbose >=1: # Entrar en modo privilegiado si hay una clave enable
#                 print("-> Conexión establecida correctamente.")
#             connection.clear_buffer()
#             output = connection.send_command_timing(command)
#             connection.disconnect()
#             #output = "\n".join(output)
#             return output
#         except NetmikoAuthenticationException:
#             self.logger.error(f"Error connecting to {device['host']}, authentication error, {dt.now()}")
#             return (f"** Error connecting to {device['host']}, authentication error")
#         except NetMikoTimeoutException:
#             self.logger.error(f"Error connecting to {device['host']}, Timeout error, {dt.now()}")
#             return (f"** Error connecting to {device['host']}, Timeout error")
#         except paramiko.ssh_exception.SSHException as ssh_error:
#             self.logger.error(f"Error connecting to {device['host']}, Paramiko {ssh_error}, {dt.now()}")
#             return (f"** Error connecting to {device['host']}, Paramiko {ssh_error}")
#         except Exception as error:
#             self.logger.error(f"Error connecting to {device['host']}: unexpected {error}, {dt.now()}")
#             return (f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}")

#     def data_validation(self, devices: List[Devices], command: str) -> None:
#         if self.verbose >= 1:
#             print ("->", f"About to execute Data Validation for {devices[0].get('host')}")
#         try:
#             ModelTelnet(devices=devices, commands=command)
#         except ValidationError as error:
#             self.logger.error(f"Data validation error: {error}")
#             if self.verbose >= 1:
#                 print (" ->", error)
#             sys.exit(1)

#     def run(self, data: dict) -> dict:
#         self.data_validation(data.get('devices'), data.get('command'))
#         output = []
#         for device in data.get('devices'):
#             output.append(f"\nDevice: {device.get('host')}")
#             if self.verbose >= 1:
#                 print (f"-> Connecting to device {device['host']} via Telnet, executing command {data.get('command')}")
#             results = self.device_connect(device, command=data.get('command'))
#             output.append(results)

#         return  "\n".join(output)


class AsyncNetmikoTelnet():
    def __new__(cls, set_verbose: dict):
        proxy_host = "localhost"
        proxy_port = 1080
        socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
        socket.socket = socks.socksocket
        return super().__new__(cls)

    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose', 0)
        self.logging = set_verbose.get('logging', 'INFO')
        self.logger = Logger("cla.log",self.logging).set_logger()

    async def device_connect(self, device: dict, command: str) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.connect, device, command)

    def connect(self, device: dict, command: str) -> str:
        try:
            connection = ConnectHandler(**device)
            connection.send_command_timing(device.get('username'))
            connection.send_command_timing(device.get('password'))
            if device.get('secret'):
                connection.enable()
            connection.clear_buffer()
            output = connection.send_command_timing(command)
            connection.disconnect()
            return f"\nDevice: {device['host']}\n{output.strip()}"
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error, {dt.now()}")
            return f"** Error connecting to {device['host']}, authentication error"
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error, {dt.now()}")
            return f"** Error connecting to {device['host']}, Timeout error"
        except paramiko.ssh_exception.SSHException as ssh_error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko {ssh_error}, {dt.now()}")
            return f"** Error connecting to {device['host']}, Paramiko {ssh_error}"
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}, {dt.now()}")
            return f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}"

    async def data_validation(self, devices: List[dict], command: str) -> None:
        if self.verbose >= 1:
            print(f"-> About to execute Data Validation")
        try:
            ModelTelnet(devices=devices, commands=command)
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            if self.verbose >= 1:
                print(f" -> {error}")
            sys.exit(1)

    async def run(self, data: dict) -> str:
        await self.data_validation(data.get('devices'), data.get('command'))
        output = []
        tasks = []
        for device in data.get('devices'):
            tasks.append(self.device_connect(device, data.get('command')))
            if self.verbose >= 1:
                print(f"-> Connecting to device {device['host']}, executing command {data.get('command')}")
        results = await asyncio.gather(*tasks)
        output.extend(results)
        self.logger.info("\n".join(output))
        return "\n".join(output)


class SetSOCKS5Tunnel():
    def __new__(cls, set_verbose: dict):
        import subprocess
        cls.subprocess = subprocess
        return super().__new__(cls)
    
    
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logging = set_verbose.get('logging')
        self.logger = Logger("cla.log",self.logging).set_logger()

    async def set_tunnel(self, jump_user: str, jump_host: str, port: int = 1080):        
        if self.verbose >= 1:
            print(f"-> Setting up the SOCKS5 tunnel to the Bastion Host {jump_user}@{jump_host}")
        try:
            command_pre = ["lsof", "-t", "-i:1080"]
            check_process = await asyncio.create_subprocess_exec(
               *command_pre,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await check_process.communicate()
            if stdout:
                pid = stdout.decode().strip()
                self.logger.info(f"SOCKS5 tunnel already running (PID {pid}")
                return f"** SOCKS5 tunnel already running (PID {pid})"

            command = ["ssh", "-D", str(port), "-N", "-C", "-f", f"{jump_user}@{jump_host}"]
            process = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
            )
            self.logger.info(f"SOCKS5 tunnel started successfully")
            return f"** SOCKS5 tunnel started successfully"
        except Exception as error:
            self.logger.error(f"Error setting up SOCKS5 tunnel: {error}")
            sys.exit(1)


    async def kill_tunnel(self, port: int = 1080):
        pid_result = self.subprocess.run(["lsof", "-t", "-i:1080"], capture_output=True, text=True)
        if pid_result.stdout:
            pid = pid_result.stdout.strip()
            try:
                command = ["kill", "-9", pid]
                if self.verbose >= 1:
                    print (f"-> Killing the SOCKS5 tunnel to the Bastion Host, local port {port}, process {pid}")
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode == 0:
                    result = f"\n** SOCKS5 tunnel (PID {pid}) killed successfully"
                    self.logger.info(f"SOCKS5 tunnel (PID {pid}) killed successfully")
                else:
                    result = f"\n** Error executing the command:\n{stderr.decode().strip()}"
                    self.logger.error(f"Error executing the command:\n{stderr.decode().strip()}")
            except Exception as error:
                self.logger.error(f"Error executing the command: {error}")
                sys.exit(1)
        else:
            result = f"\n** No SOCKS5 tunnel to kill"
            self.logger.info("No SOCKS5 tunnel to kill")
        return result