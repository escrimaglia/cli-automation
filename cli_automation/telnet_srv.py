from netmiko import ConnectHandler, NetmikoAuthenticationException, NetMikoTimeoutException
from pydantic import ValidationError
from .model_srv import ModelTelnet
from .proxy_srv import TunnelProxy
import asyncio
import paramiko
import sys
from typing import List
import os
from .logging import Logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))

class AsyncNetmikoTelnet():
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logger = set_verbose.get('logger')
        tunnel = TunnelProxy(proxy_host="localhost", proxy_port=1080, logger=self.logger, verbose=self.verbose)
        tunnel.set_proxy()

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
        return "\n".join(output)