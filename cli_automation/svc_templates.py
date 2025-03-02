import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))

import json
from .svc_files import ManageFiles

class Templates():
    def __init__(self, set_verbose: dict):
        self.verbose = set_verbose.get('verbose')
        self.logger = set_verbose.get('logger')
        self.file = ManageFiles(self.logger)

    async def create_template(self, file_name: str = None) -> None:
        example_hosts_file = {   
            'devices': [
                {
                    'host': 'X.X.X.X',
                    'username': 'user',
                    'password': 'password',
                    'device_type': 'type',
                    'global_delay_factor': None
                }
            ]
        }
        
        example_ssh_commands_file = {
            'X.X.X.X': {
                'commands': [
                    'show version',
                    'show ip int brief'
                ]
            }
        }

        example_telnet_commands_structure = {
            'X.X.X.X': {
                'commands': [
                    'enter privilege mode',
                    'enter configuration mode',
                    'config comand 1',
                    'config command 2',
                    'exit configuration mode',
                    'save configuration command'
                ]
            }
        }

        example_telnet_commands_example = {
            "X.X.X.X": {
                "commands": [
                    'config terminal',
                    'interface loopback 3',
                    'description loopback interface',
                    'ip address 192.168.2.1 255.255.255.0',
                    'end',
                    'write mem'
                ]
            }
        }

        files = [example_hosts_file, example_ssh_commands_file, example_telnet_commands_structure, example_telnet_commands_example]
        self.logger.debug(f"Creating templates")
        if file_name is None:
            for template in files:
                var_name = [name for name, value in locals().items() if value is template][0]
                await self.file.create_file(var_name+".json", json.dumps(template, indent=3))
                self.logger.debug(f"Template {var_name} created")
        else:
            file_name = file_name.split(".")[0] if "." in file_name else file_name
            if file_name in files:
                var_name = [name for name, value in locals().items() if value is template][0]
                await self.file.create_file(var_name+".json", json.dumps(file_name, indent=3))
                self.logger.debug(f"Template {var_name} created")
            else:
                print (f"** Error creating the template {var_name}. The template does not exist")
                self.logger.error(f"Error creating the template {var_name}. The template does not exist")
                sys.exit(1)
