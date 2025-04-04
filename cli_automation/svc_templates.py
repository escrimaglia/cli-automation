# Telmplates Service Class
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))

import json
from .svc_files import ManageFiles
from pathlib import Path

class Templates():
    def __init__(self, inst_dict: dict):
        self.verbose = inst_dict.get('verbose')
        self.logger = inst_dict.get('logger')
        self.file = ManageFiles(self.logger)
        self.directory = "examples"

    async def create_template(self) -> None:
        directory = Path(self.directory)
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception:
            print(f"** Error creating the directory {directory}")
            self.logger.error(f"Error creating the directory {directory}")
            sys.exit(1)

        examples = {
                'hosts_file': {   
                    'devices': [
                        {
                            'host': 'X.X.X.X',
                            'username': 'user',
                            'password': 'password',
                            'secret': 'secret',
                            'device_type': 'type',
                            'global_delay_factor': 'null'
                        }
                    ]
                },
                'extreme_exos_commands_file': {
                    'X.X.X.X': {
                        'commands': [
                            'create vlan Loopback0',
                            'configure vlan Loopback0 add ports 1',
                            'configure vlan Loopback0 ipaddress 192.168.10.1/32',
                            'enable loopback0',
                        ]
                    }
                },
                'cisco_ios_commands_file': {
                    'X.X.X.X': {
                        'commands': [
                            'show version',
                            'show ip int brief'
                        ]
                    }
                },
                'cisco_xe_commands_file': {
                    'X.X.X.X': {
                        'commands': [
                            "interface Serial0/0/1",
                            "ip address 192.168.10.1 255.255.255.252",
                            "encapsulation ppp",
                            "no shutdown",
                            "exit",
                        ]
                    }
                },
                'vyos_commands_file': {
                    'X.X.X.X': {
                        'commands': [
                            'configure',
                            'set interfaces ethernet eth1 address',
                            'set interfaces ethernet eth1 description "LAN Interface"',
                            'set system host-name "VyOS-Router"',
                            'commit',
                            'save',
                            'exit'
                        ]
                    }
                },
                'cisco_nxos_commands_file': {
                    'X.X.X.X': {
                        'commands': [
                            'interface Ethernet1/1',
                            'description Conectado a Servidor',
                            'switchport mode access',
                            'switchport access vlan 10',
                            'no shutdown'
                        ]
                    }
                },
                'cisco_xr_commands_file':{
                    'X.X.X.X': {
                        'commands': [
                            'interface GigabitEthernet0/0/0/0',
                            'description Configurado desde Netmiko',
                            'ipv4 address 192.168.1.1 255.255.255.0',
                            'commit'
                        ]
                    }
                },
                'huawei_commands_file':{
                    'X.X.X.X': {
                        'commands': [
                            'system-view',
                            'interface GigabitEthernet0/0/1',
                            'description Conexion a Servidor',
                            'quit',
                            'save'
                        ]
                    }
                },
                'huawei_vrp_commands_file': {
                    'X.X.X.X': {
                        'commands': [
                            'sysname Router-Huawei',
                            'interface GigabitEthernet0/0/1',
                            'ip address 192.168.10.1 255.255.255.0',
                            'description Conexion_LAN',
                            'quit',
                            'firewall zone trust',
                            'add interface GigabitEthernet0/0/1',
                            'quit',
                            'commit',
                            'save'
                        ]
                    }
                },
                'juniper_junos_commands_file': {
                    'X.X.X.X': {
                        'commands': [
                            "set interfaces ge-0/0/1 description 'Conexión a core'",
                            "set interfaces ge-0/0/1 unit 0 family inet address 192.168.2.1/24",
                            "commit"
                        ]
                    }
                },
                'arista_eos_commands_file': {
                    'X.X.X.X': {
                        'commands': [
                            'interface Ethernet1',
                            'description Conexion a Servidor',
                            'no shutdown',
                            'exit',
                        ]
                    }
                },
                'telnet_commands_structure': {
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
                },
                'telnet_commands_example': {
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
            }

        self.logger.info(f"Creating templates")
        for name, value in examples.items():
            await self.file.create_file(f"{directory}/{name}.json", json.dumps(value, indent=3))
       
    