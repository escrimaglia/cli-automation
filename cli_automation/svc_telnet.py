# Telnet Service Classes
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))

import traceback
import paramiko
from paramiko.ssh_exception import SSHException
from netmiko import ConnectHandler, NetmikoAuthenticationException, NetMikoTimeoutException
from pydantic import ValidationError
from .svc_model import ModelTelnetPull, ModelTelnetPush
from .svc_proxy import TunnelProxy
import asyncio
import paramiko
from typing import List
import json
from .svc_files import ManageFiles
import socket
from cli_automation import config_data

class AsyncNetmikoTelnetPull():
    def __init__(self, inst_dict: dict):
        self.verbose = inst_dict.get('verbose')
        self.logger = inst_dict.get('logger')
        proxy = TunnelProxy(logger=self.logger, verbose=self.verbose)
        proxy.set_proxy()


    async def device_connect(self, device: dict, command: str) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.connect, device, command)


    def connect(self, device: dict, command: str) -> str:
        try:
            device['device_type'] = 'generic_telnet'
            device["global_delay_factor"] = 2
            connection = ConnectHandler(**device)
            connection.send_command_timing(device.get('username'))
            connection.send_command_timing(device.get('password'))
            self.logger.debug(f"Sending user {device.get('username')} and password {device.get('password')} to device")
            if device.get('secret'):
                connection.enable()
            connection.clear_buffer()
            self.logger.debug(f"Executing command {command} on device {device['host']}")
            output = connection.send_command_timing(command)
            self.logger.debug(f"Output: {output}")
            connection.disconnect()
            return f"\nDevice: {device['host']}\n{output.strip()}"
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error")
            return f"** Error connecting to {device['host']}, authentication error"
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error")
            return f"** Error connecting to {device['host']}, Timeout error"
        except (paramiko.SSHException) as error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko error: {error}")
            return f"** Error connecting to {device['host']}, Paramiko error: {error}"
        except (SSHException, socket.timeout, socket.error) as error:
            self.logger.error(f"Error connecting to {device['host']}, SSH error: {error}")
            return f"** Error connecting to {device['host']}, SSH error: {error}"
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}\n{traceback.format_exc()}")
            return f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}"


    def data_validation(self, data: ModelTelnetPull) -> None:
        if self.verbose in [1,2]:
            print(f"-> About to execute Data Validation")
        try:
            ModelTelnetPull(devices=data.get('devices'), command=data.get('command'))
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            print(f" -> {error}")
            sys.exit(1)


    async def run(self, data: dict) -> str:
        self.data_validation(data=data)
        output = []
        tasks = []
        for device in data.get('devices'):
            tasks.append(self.device_connect(device, data.get('command')))
            if self.verbose in [1,2]:
                print(f"-> Connecting to device {device['host']}, executing command {data.get('command')}")
            self.logger.debug(f"Connecting to device {device['host']}, executing command {data.get('command')}")
        results = await asyncio.gather(*tasks)
        output.extend(results)
        return "\n".join(output)
    

class AsyncNetmikoTelnetPush():
    def __init__(self, inst_dict: dict):
        self.verbose = inst_dict.get('verbose')
        self.logger = inst_dict.get('logger')
        proxy = TunnelProxy(logger=self.logger, verbose=self.verbose)
        proxy.set_proxy()

    async def handle_read_file(self):
        mf = ManageFiles(self.logger)
        content = await mf.read_file("config.json")
        return content


    async def device_connect(self, device: dict, command: List[str], prompts: List[str]) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.connect, device, command, prompts)


    def connect(self, device: dict, commands: str, prompts: List[str]) -> str:
        try:
            device["device_type"] = "generic_telnet"
            device["global_delay_factor"] = 2
            connection = ConnectHandler(**device)
            connection.send_command_timing(device.get('username'))
            connection.send_command_timing(device.get('password'))
            self.logger.debug(f"Sending user {device.get('username')} and password {device.get('password')} to device")
            aut = False
            output = ""
            for prompt in prompts:
                if prompt in connection.find_prompt():
                    aut = True
                    output = (f"Login valid")
                    self.logger.debug(f"Login: {output}")
                    break
            if not aut:
                output = (f"Login invalid")
                connection.disconnect()
                self.logger.debug(f"Login: {output}")
                return f"Output, {output.strip()}"
            if device.get('secret'):
                connection.enable()
            output = ""
            for cmd in commands:
                self.logger.debug(f"Executing command {cmd} on device {device['host']}")
                result = connection.send_command_timing(cmd)
                self.logger.debug(f"Output: {result}")
                if "Invalid input" in result or "Error" in result:
                    output = (f"Invalid input, {cmd}")
                    self.logger.debug(f"Output: {output}")
                    break
            connection.disconnect()
            return f"Output {output.strip()}"
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error")
            return f"** Error connecting to {device['host']}, authentication error"
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error")
            return f"** Error connecting to {device['host']}, Timeout error"
        except (paramiko.SSHException) as ssh_error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko error: {ssh_error}")
            return f"** Error connecting to {device['host']}, Paramiko error: {ssh_error}"
        except SSHException as ssh_error:
            self.logger.error(f"Error connecting to {device['host']}, SSH error: {ssh_error}")
            return f"** Error connecting to {device['host']}, SSH error: {ssh_error}"
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}\n{traceback.format_exc()}")
            return f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}"


    def data_validation(self, data: ModelTelnetPush) -> None:
        if self.verbose in [1,2]:
                print(f"-> About to execute Data Validation")
        try:
            ModelTelnetPush(device=data)
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            print (f" ->, {error}")
            sys.exit(1)

    
    async def run(self, data: List[dict]) -> dict:
        self.data_validation(data=data)
        prompts = config_data.get("telnet_prompts")
        tasks = []
        print ("\n")
        for device in data:
            dev = device.get('device')
            cmd = device.get('commands')
            tasks.append(self.device_connect(device=dev, command=cmd, prompts=prompts))
            if self.verbose in [1,2]:
                print (f"-> Connecting to device {dev.get('host')}, configuring commands {cmd}")
            self.logger.info(f"Connecting to device {dev.get('host')}, executing command {cmd}")
        results = await asyncio.gather(*tasks)
        output_data = []
        for device, output in zip(data, results):
            output_data.append({"Device": device.get('device').get('host'), "Output": output})
        for output in output_data:
            if isinstance(output.get('Output'), str):
                if ("Invalid input" or "Error") in output.get('Output'):
                    output['Output'] = "Configuration failed, check the commands in the configuration file"
                elif "Login invalid" in output["Output"]:
                    output['Output'] = "Authentication to device failed"
                else: 
                    output['Output'] = "Configuration successfully applied"
            else:
                output['Output'] = "Unknown configuration status" 
        dict_output = {}
        for device in output_data:
            dict_output.update({"Device": device["Device"], "Result": device["Output"]})
        return json.dumps(output_data, indent=2, ensure_ascii=False)
