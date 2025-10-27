# SSH Service Classes
# Ed Scrimaglia

import sys
import os

import textfsm
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))

import traceback
import asyncio
from netmiko import ConnectHandler, NetmikoAuthenticationException, NetMikoTimeoutException
import paramiko
from paramiko.ssh_exception import SSHException
from pydantic import ValidationError
from .svc_model import ModelMultipleSsh, ModelSingleSsh, ModelMultipleInteractive, ModelSingleInteractive
from typing import List
import json
from .svc_proxy import TunnelProxy
import socket


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
            if connection.is_alive():
                self.logger.debug(f"Connection to {device['host']} is active")
            else:
                self.logger.debug(f"Connection to {device['host']} failed")
                connection.disconnect()
                return f"** Connection to device {device['host']} failed"
            connection.enable()
            output = []
            for command in commands:
                self.logger.debug(f"Executing command {command} on device {device['host']}")
                result = await asyncio.to_thread(connection.send_command, command, use_textfsm=True)
                self.logger.debug(f"Output: {result}")
                output.append(self.format_output(command, result))
            await asyncio.to_thread(connection.disconnect)
            return output
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error")
            return f"** Error connecting to {device['host']}, authentication error"
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error")
            return f"** Error connecting to {device['host']}, Timeout error"
        except paramiko.SSHException as error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko error: {error}")
            return f"** Error connecting to {device['host']}, Paramiko error: {error}"
        except (SSHException, socket.timeout, socket.error) as error:
            self.logger.error(f"Error connecting to {device['host']}, SSH error: {error}")
            return f"** Error connecting to {device['host']}, SSH error: {error}"
        except textfsm.TextFSMError:
            self.logger.error(f"Error connecting to {device['host']}, TextFSM error")
            return f"** Error connecting to {device['host']}, TextFSM error"
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}\n{traceback.format_exc()}")
            return f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}"
        
       
    def data_validation(self, data) -> None:
        if self.verbose in [1,2]:
            print ("->", f"About to execute Data Validation")
        try:
            if self.single_host:
                ModelSingleSsh(device=data.get('device'), commands=data.get('commands'))
            else:
                ModelMultipleSsh(device=data)
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            print (f"->, {error}")
            sys.exit(1)


    async def run(self, data) -> dict:
        self.data_validation(data)
        tasks = []
        if self.single_host:
            tasks.append(self.netmiko_connection(device=data.get('device'), commands=data.get('commands')))
            if self.verbose in [1,2]:
                print (f"-> Connecting to device {data.get('device').get('host')}, executing commands {data.get('commands')}")
            self.logger.info(f"Connecting to device {data.get('device')}, executing commands {data.get('commands')}")
        else:
            for device in data:
                tasks.append(self.netmiko_connection(device=device.get('device'), commands=device.get('commands')))
                if self.verbose in [1,2]:
                    print (f"-> Connecting to device {device.get('device').get('host')}, executing commands {device.get('commands')}")
                self.logger.info(f"Connecting to device {device.get('device').get('host')}, executing commands {device.get('commands')}")
        results = await asyncio.gather(*tasks)
        output_data = []
        if self.single_host:
            for output in results:
                output_data.append({"Device": data.get('device').get('host'), "Output": output})
        else:
            for device, output in zip(data, results):
                output_data.append({"Device": device.get('device').get('host'), "Output": output})
        return json.dumps(output_data, indent=2)


    def format_output(self, command: str, output: any) -> dict:
        if isinstance(output, str):
            result = output.splitlines()
            return {"type": "non-textfsm", command: result}
        elif isinstance(output, list):
            return {"type": "textfsm", command: output}
        else:
            return {"type": "non-textfsm", command: "Unknown output type"}

    
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
            if connection.is_alive():
                self.logger.debug(f"Connection to {device['host']} is active")
            else:
                self.logger.debug(f"Connection to {device['host']} failed")
                connection.disconnect()
                return f"** Connection to device {device['host']} failed"
            connection.enable()
            self.logger.debug(f"Detected prompt {connection.find_prompt()}")
            output = []
            self.logger.debug(f"Configuring the following commands {commands} on device {device['host']}")
            result = await asyncio.to_thread(connection.send_config_set, commands)
            self.logger.debug(f"Output: {result}")
            output.append(result)
            await asyncio.to_thread(connection.disconnect)
            return output
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error")
            return f"** Error connecting to {device['host']}, authentication error"
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error")
            return f"** Error connecting to {device['host']}, Timeout error"
        except paramiko.SSHException as error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko error: {error}")
            return f"** Error connecting to {device['host']}, Paramiko error: {error}"
        except (SSHException, socket.timeout, socket.error) as error:
            self.logger.error(f"Error connecting to {device['host']}, SSH error: {error}")
            return f"** Error connecting to {device['host']}, SSH error: {error}"
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}\n{traceback.format_exc()}")
            return f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}"
        
        
    def data_validation(self, data) -> None:
        if self.verbose in [1,2]:
            print ("->", f"About to execute Data Validation")
        try:
            if self.single_host:
                ModelSingleSsh(device=data.get('device'), commands=data.get('commands'))
            else:
                ModelMultipleSsh(device=data)
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            print (f" ->, {error}")
            sys.exit(1)


    async def run(self, data: dict) -> dict:
        self.data_validation(data=data)   
        tasks = []
        if self.single_host:
            tasks.append(self.netmiko_connection(device=data.get('device'), commands=data.get('commands')))
            if self.verbose in [1,2]:
                print (f"-> Connecting to device {data.get('device').get('host')}, configuring commands {data.get('commands')}")
            self.logger.info(f"Connecting to device {data.get('device').get('host')}, executing commands {data.get('commands')}")
        else:
            for device in data:
                tasks.append(self.netmiko_connection(device=device.get('device'), commands=device.get('commands')))
                if self.verbose in [1,2]:
                    print (f"-> Connecting to device {device.get('device').get('host')}, configuring commands {device.get('commands')}")
                self.logger.info(f"Connecting to device {device.get('device').get('host')}, executing commands {device.get('commands')}")
        results = await asyncio.gather(*tasks)
        output_data = []
        if self.single_host:
            for output in results:
                output_data.append({"Device": data.get('device').get('host'), "Output": output})
        else:
            for device, output in zip(data, results):
                output_data.append({"Device": device.get('device').get('host'), "Output": output})

        for output in output_data:
            has_error = ["Invalid input", "Error", "Incomplete command", "Ambiguous command", "Authentication to device failed"]
            if isinstance(output.get('Output'), list):
                if not any(error in output.get('Output')[-1] for error in has_error):
                    output['Output'] = "Successful configuration"
                else: 
                    output['Output'] = "Configuration failed, check the commands in the configuration file"
            elif isinstance(output.get('Output'), str):
                if not any(error in output.get('Output') for error in has_error):
                    output['Output'] = "Successful configuration"
                else: 
                    output['Output'] = "Configuration failed, check the commands in the configuration file or credentials"
            
        return json.dumps(output_data, indent=2)
    
    
class AsyncNetmikoInteractive():
    def __init__(self, inst_dict: dict):
        self.verbose = inst_dict.get('verbose')
        self.single_host = inst_dict.get('single_host')
        self.logger = inst_dict.get('logger')
        proxy = TunnelProxy(logger=self.logger, verbose=self.verbose)
        proxy.set_proxy()


    async def netmiko_connection(self, device: dict, commands_pattern: List[str]) -> ConnectHandler:
        try:
            connection = await asyncio.to_thread(ConnectHandler, **device)
            if connection.is_alive():
                self.logger.debug(f"Connection to {device['host']} is active")
            else:
                self.logger.debug(f"Connection to {device['host']} failed")
                connection.disconnect()
                return f"** Connection to device {device['host']} failed"
            connection.enable()
            self.logger.debug(f"Detected prompt {connection.find_prompt()}")
            output = []
            self.logger.debug(f"Configuring the following commands and patterns {commands_pattern} on device {device['host']}")
            result = await asyncio.to_thread(connection.send_multiline, commands_pattern)
            self.logger.debug(f"Output: {result}")
            output.append(result)
            await asyncio.to_thread(connection.disconnect)
            return output
        except NetmikoAuthenticationException:
            self.logger.error(f"Error connecting to {device['host']}, authentication error")
            return f"** Error connecting to {device['host']}, authentication error"
        except NetMikoTimeoutException:
            self.logger.error(f"Error connecting to {device['host']}, Timeout error")
            return f"** Error connecting to {device['host']}, Timeout error"
        except paramiko.SSHException as error:
            self.logger.error(f"Error connecting to {device['host']}, Paramiko error: {error}")
            return f"** Error connecting to {device['host']}, Paramiko error: {error}"
        except (SSHException,socket.timeout, socket.error) as error:
            self.logger.error(f"Error connecting to {device['host']}, SSH error: {error}")
            return f"** Error connecting to {device['host']}, SSH error: {error}"
        except Exception as error:
            self.logger.error(f"Error connecting to {device['host']}: unexpected {error}\n{traceback.format_exc()}")
            return f"** Error connecting to {device['host']}: unexpected {str(error).replace('\n', ' ')}"
    

    def data_validation(self, data) -> None:
        if self.verbose in [1,2]:
            print ("->", f"About to execute Data Validation")
        try:
            if self.single_host:
                ModelSingleInteractive(device=data.get('device'), commands=data.get('commands'))
            else:
                ModelMultipleInteractive(device=data)
        except ValidationError as error:
            self.logger.error(f"Data validation error: {error}")
            print (f" ->, {error}")
            sys.exit(1)


    async def run(self, data: dict) -> dict:
        self.data_validation(data=data)   
        tasks = []
        if self.single_host:
            tasks.append(self.netmiko_connection(device=data.get('device'), commands_pattern=data.get('commands')))
            if self.verbose in [1,2]:
                print (f"-> Connecting to device {data.get('device').get('host')}, configuring commands {data.get('commands')}")
            self.logger.info(f"Connecting to device {data.get('device').get('host')}, executing commands {data.get('commands')}")
        else:
            for device in data:
                tasks.append(self.netmiko_connection(device=device.get('device'), commands_pattern=device.get('commands')))
                if self.verbose in [1,2]:
                    print (f"-> Connecting to device {device.get('device').get('host')}, configuring commands {device.get('commands')}")
                self.logger.info(f"Connecting to device {device.get('device').get('host')}, executing commands {device.get('commands')}")
        results = await asyncio.gather(*tasks)
        output_data = []
        if self.single_host:
            for output in results:
                output_data.append({"Device": data.get('device').get('host'), "Output": output})
        else:
            for device, output in zip(data, results):
                output_data.append({"Device": device.get('device').get('host'), "Output": output})

        for output in output_data:
            has_error = ["Invalid input", "Error", "Incomplete command", "Ambiguous command", "Authentication to device failed"]
            if isinstance(output.get('Output'), list):
                if not any(error in output.get('Output')[-1] for error in has_error):
                    output['Output'] = "Successful configuration"
                else: 
                    output['Output'] = "Configuration failed, check the commands in the configuration file"
            elif isinstance(output.get('Output'), str):
                if not any(error in output.get('Output') for error in has_error):
                    output['Output'] = "Successful configuration"
                else: 
                    output['Output'] = "Configuration failed, check the commands in the configuration file or credentials"
            
        return json.dumps(output_data, indent=2)