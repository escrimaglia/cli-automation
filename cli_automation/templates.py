
from datetime import datetime as dt
from .clilogging import Logger
from .create_file import CreateFile
import sys
import json

class Templates():
    def __init__(self, set_verbose: dict):
        self.logging = set_verbose.get('logging')
        self.logger = Logger("cla.log",self.logging).set_logger()
        self.file = CreateFile(set_verbose=set_verbose)

    async def create_template(self, file_name_hosts: str, file_name_commands) -> None:
        hosts = {   
            'devices': [
                {
                    'host': 'X.X.X.X',
                    'username': 'user',
                    'password': 'password',
                    'device_type': 'type',
                    'ssh_config_file': '~/.ssh/config'
                }
            ]
        }
        
        commands = {
            'X.X.X.X': {
                'commands': [
                    'show version',
                    'show ip int brief'
                ]
            }
        }

        result = self.file.create_file(file_name_hosts, hosts)
        # async with aiofiles.open(file_name_hosts, "w") as file:
        #     await file.write(json.dumps(hosts, indent=2))

        result  = self.file.create_file(file_name_commands, commands)
        # async with aiofiles.open(file_name_commands, "w") as file:
        #     await file.write(json.dumps(commands, indent=2))

        result = {"result": f"Templates '{file_name_hosts}' and '{file_name_commands}' created"}

        return json.dumps(result, indent=2)