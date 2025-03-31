# SSH Service Classes
# Ed Scrimaglia

import sys
import os

import paramiko.ssh_exception
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))

import traceback
import asyncio
from netmiko import ConnectHandler, NetmikoAuthenticationException, NetMikoTimeoutException
import paramiko
from pydantic import ValidationError
from .svc_model import ModelSsh
from typing import List
import json
from .svc_proxy import TunnelProxy


class AsyncNetmikoPull():
    def __init__(self, inst_dict: dict):
        self.verbose = inst_dict.get('verbose')
        self.single_host = inst_dict.get('single_host')
        self.logger = inst_dict.get('logger')
        proxy = TunnelProxy(logger=self.logger, verbose=self.verbose)
        proxy.set_proxy()
        

    async def netmiko_connection(self, device: dict, commands: List[str]) -> str:
        try:
            connection = await asyncio.to_thread(ConnectHandler, **device)
            output = []
            for command in commands:
                self.logger.debug(f"Executing command {command} on device {device['host']}")
                result = await asyncio.to_thread(connection.send_command, command, use_textfsm=True)
                self.logger.debug(f"Output: {result}")
                output.append({command: result})
            await asyncio.to_thread(connection.disconnect)
            return output
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error")
            return f"** Error connecting to {device['host']}, authentication error"
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error")
            return f"** Error connecting to {device['host']}, Timeout error"
        except (paramiko.ssh_exception.SSHException, paramiko.SSHException) as ssh_error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko error: {ssh_error}")
            return f"** Error connecting to {device['host']}, Paramiko error: {ssh_error}"
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}\n{traceback.format_exc()}")
            return f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}"
        
       
    def data_validation(self, data: ModelSsh) -> None:
        if self.verbose in [1,2]:
            print ("->", f"About to execute Data Validation")
        try:
            ModelSsh(devices=data.get('devices'), commands=data.get('commands'))
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            print (f"->, {error}")
            sys.exit(1)


    async def run(self, data: dict) -> dict:
        self.data_validation(data)
        tasks = []
        for device in data.get('devices'):
            tasks.append(self.netmiko_connection(device, commands=data.get('commands')))
            if self.verbose in [1,2]:
                print (f"-> Connecting to device {device['host']}, executing commands {data.get('commands')}")
            self.logger.info(f"Connecting to device {device['host']}, executing commands {data.get('commands')}")
        results = await asyncio.gather(*tasks)
        output_data = []
        for device, output in zip(data.get('devices'), results):
            output_data.append({"Device": device['host'], "Output": output})
        output_data = output_data[0] if self.single_host else output_data
        return json.dumps(output_data, indent=2)
    
    
class AsyncNetmikoPush():
    def __init__(self, inst_dict: dict):
        self.verbose = inst_dict.get('verbose')
        self.single_host = inst_dict.get('single_host')
        self.logger = inst_dict.get('logger')
        proxy = TunnelProxy(logger=self.logger, verbose=self.verbose)
        proxy.set_proxy()
      

    async def netmiko_connection(self, device: dict, commands: List[str]) -> str:
        try:
            connection = await asyncio.to_thread(ConnectHandler, **device)
            output = []
            self.logger.debug(f"Configuring the following commands {commands} on device {device['host']}")
            result = await asyncio.to_thread(connection.send_config_set, commands)
            self.logger.debug(f"Output: {result}")
            result += await asyncio.to_thread(connection.save_config)
            output.append(result)
            await asyncio.to_thread(connection.disconnect)
            return output
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error")
            return f"** Error connecting to {device['host']}, authentication error"
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error")
            return f"** Error connecting to {device['host']}, Timeout error"
        except (paramiko.ssh_exception.SSHException, paramiko.SSHException) as ssh_error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko error: {ssh_error}")
            return f"** Error connecting to {device['host']}, Paramiko error: {ssh_error}"
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}\n{traceback.format_exc()}")
            return f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}"
        
        
    def data_validation(self, data: ModelSsh) -> None:
        if self.verbose in [1,2]:
            print ("->", f"About to execute Data Validation")
        try:
            ModelSsh(devices=data.get('devices'), commands=data.get('commands'))
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            print (f" ->, {error}")
            sys.exit(1)


    async def run(self, data: dict) -> dict:
        self.data_validation(data=data)   
        tasks = []
        commands = data.get('commands')
        for device in data.get('devices'):
            tasks.append(self.netmiko_connection(device, commands=commands))
            if self.verbose in [1,2]:
                print (f"-> Connecting to device {device['host']}, configuring commands {commands}")
            self.logger.info(f"Connecting to device {device['host']}, executing commands {commands}")
        results = await asyncio.gather(*tasks)
        output_data = []
        for device, output in zip(data.get('devices'), results):
            output_data.append({"Device": device.get('host'), "Output": output})
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
