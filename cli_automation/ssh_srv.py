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
from .model_srv import Model, Devices, ModelPush, ModelTelnet
from typing import List
import json
from .proxy_srv import TunnelProxy

class AsyncNetmikoPull():
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logging = set_verbose.get('logging')
        self.single_host = set_verbose.get('single_host')
        self.logger = set_verbose.get('logger')
        tunnel = TunnelProxy(proxy_host="localhost", proxy_port=1080, logger=self.logger, verbose=self.verbose)
        tunnel.set_proxy()
        

    async def netmiko_connection(self, device: dict, commands: List[str]) -> str:
        try:
            connection = await asyncio.to_thread(ConnectHandler, **device)
            output = []
            for command in commands:
                self.logger.info(f"Executing command {command} on device {device['host']}")
                result = await asyncio.to_thread(connection.send_command, command, use_textfsm=True)
                output.append({command: result})
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
                print (f"-> Connecting to device {device['host']}, executing commands {data.get('commands')}")
        results = await asyncio.gather(*tasks)
        output_data = []
        for device, output in zip(data.get('devices'), results):
            output_data.append({"Device": device['host'], "Output": output})
        output_data = output_data[0] if self.single_host else output_data
        return json.dumps(output_data, indent=2)
    

class AsyncNetmikoPushSingle():
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logging = set_verbose.get('logging')
        self.single_host = set_verbose.get('single_host')
        self.logger = set_verbose.get('logger')
        #self.logger = Logger(level=self.logging).set_logger()
        tunnel = TunnelProxy(proxy_host="localhost", proxy_port=1080, logger=self.logger, verbose=self.verbose)
        tunnel.set_proxy()


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
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logging = set_verbose.get('logging')
        self.single_host = set_verbose.get('single_host')
        self.logger = set_verbose.get('logger')
        tunnel = TunnelProxy(proxy_host="localhost", proxy_port=1080, logger=self.logger, verbose=self.verbose)
        tunnel.set_proxy()
      

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
