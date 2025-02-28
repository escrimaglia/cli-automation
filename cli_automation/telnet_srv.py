# Telnet classes for the CLI Automation project
# Ed Scrimaglia

from netmiko import ConnectHandler, NetmikoAuthenticationException, NetMikoTimeoutException
from pydantic import ValidationError
from .model_srv import ModelTelnetPull, ModelTelnetPush
from .proxy_srv import TunnelProxy
import asyncio
import paramiko
import sys
from typing import List
import os
import json
from .files_srv import ManageFiles
from . import config_data

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))

class AsyncNetmikoTelnetPull():
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logger = set_verbose.get('logger')
        proxy = TunnelProxy(logger=self.logger, verbose=self.verbose, proxy_host="localhost", proxy_port=1080)
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
            if device.get('secret'):
                connection.enable()
            connection.clear_buffer()
            output = connection.send_command_timing(command)
            connection.disconnect()
            return f"\nDevice: {device['host']}\n{output.strip()}"
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error")
            return f"** Error connecting to {device['host']}, authentication error"
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error")
            return f"** Error connecting to {device['host']}, Timeout error"
        except paramiko.ssh_exception.SSHException as ssh_error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko {ssh_error}")
            return f"** Error connecting to {device['host']}, Paramiko {ssh_error}"
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}")
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
        results = await asyncio.gather(*tasks)
        output.extend(results)
        return "\n".join(output)
    

class AsyncNetmikoTelnetPush():
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logger = set_verbose.get('logger')
        proxy = TunnelProxy(logger=self.logger, verbose=self.verbose, proxy_host="localhost", proxy_port=1080)
        proxy.set_proxy()

    async def handle_read_file(self):
        mf = ManageFiles(self.logger)
        content = await mf.read_file("config.json")  # Await the coroutine
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
            aut = False
            output = ""
            for prompt in prompts:
                if prompt in connection.find_prompt():
                    aut = True
                    break
            if not aut:
                output = (f"Login invalid")
                connection.disconnect()
                return f"Output, {output.strip()}"
            if device.get('secret'):
                connection.enable()
            output = ""
            for cmd in commands:
                result = connection.send_command_timing(cmd)
                if "Invalid input" in result or "Error" in result:
                    output = (f"Invalid input, {cmd}")
                    break
            connection.disconnect()
            return f"Output {output.strip()}"
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error")
            return f"** Error connecting to {device['host']}, authentication error"
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error")
            return f"** Error connecting to {device['host']}, Timeout error"
        except paramiko.ssh_exception.SSHException as ssh_error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko {ssh_error}")
            return f"** Error connecting to {device['host']}, Paramiko {ssh_error}"
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}")
            return f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}"


    def data_validation(self, data: ModelTelnetPush) -> None:
        if self.verbose in [1,2]:
                print(f"-> About to execute Data Validation")
        try:
            ModelTelnetPush(devices=data.get('device'), commands=data.get('commands'))
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            print (f" ->, {error}")
            sys.exit(1)

    
    async def run(self, data: dict) -> dict:
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
