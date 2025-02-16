# Non Blocking Async Netmiko Class
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))
import typer
from typing_extensions import Annotated
from .service_classes import AsyncNetmikoPull, AsyncNetmikoPushSingle, AsyncNetmikoPushMultiple, ManageOutput, Templates
import asyncio
from typing import List
from enum import Enum
import json
from .progress_bar import ProgressBar
from datetime import datetime

app = typer.Typer(no_args_is_help=True)

class Logging(Enum):
    info = "info"
    debug = "debug"
    error = "error"
    warning = "warning"
    critical = "critical"

class DeviceType(Enum):
    cisco_ios = "cisco_ios"
    cisco_xr = "cisco_xr"
    juniper_junos = "juniper_junos"
    arista_eos = "arista_eos"
    huawei = "huawei"
    nokia_sros = "alcatel_sros"
    autodetect = "autodetect"


@app.command("pull-single", help="Pull data from a Single Host", no_args_is_help=True)
def pull_single_host(
        host: Annotated[str, typer.Option("--host", "-h", help="host ip address", rich_help_panel="Connection Parameters", case_sensitive=False)],
        user: Annotated[str, typer.Option("--user", "-u", help="username", rich_help_panel="Connection Parameters", case_sensitive=False)],
        password: Annotated[str, typer.Option(prompt=True, help="password", metavar="password must be provided by keyboard",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],
        commands: Annotated[List[str], typer.Option("--cmd", "-c", help="commands to execute on device", rich_help_panel="Device Commands Parameter", case_sensitive=False)],
        device_type: Annotated[DeviceType, typer.Option("--type", "-t", help="device type", rich_help_panel="Connection Parameters", case_sensitive=False)],
        ssh_config: Annotated[str, typer.Option("--cfg", "-s", help="ssh config file", rich_help_panel="Connection Parameters", case_sensitive=False)] = None,
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters")] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=True)] = None,
    ):
    typer.echo(f"commands: {commands}")
    async def process():
        datos = {
            "devices": [
                {
                    "host": host,
                    "username": user,
                    "password": password,
                    "device_type": device_type.value,
                    "ssh_config_file": ssh_config
                }
            ],
            "commands": commands
        }

        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "single_host": True}
        start = datetime.now()
        netm = AsyncNetmikoPull(set_verbose=set_verbose)
        result = await netm.run(datos)
        end = datetime.now()
        set_verbose = {"verbose": verbose, "result": result, "time": end - start}
        mgmt = ManageOutput(set_verbose=set_verbose)
        await mgmt.create_file()
        mgmt.print_verbose()

    #asyncio.run(process())
    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("pull-multiple", help="Pull data from Multiple Hosts", no_args_is_help=True)
def pull_multiple_host(
        devices: Annotated[typer.FileText, typer.Option("--hosts", "-h", help="group of hosts", metavar="FILENAME Json file", rich_help_panel="Hosts File Parameter", case_sensitive=False)],
        commands: Annotated[List[str], typer.Option("--cmd", "-c", help="commands to execute on device", rich_help_panel="Device Commands Parameter", case_sensitive=False)],
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters")] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=False)] = None,
    ):
    
    async def process():
        file_lines = ""
        for line in devices:
            file_lines += line
        try:
            datos_devices = json.loads(file_lines)
        except json.JSONDecodeError as error:
            typer.echo(f"Error reading json file: {error}")
            raise typer.Exit(code=1)
        
        
        if "devices" not in datos_devices:
            typer.echo("Error reading json file: devices key not found or reading an incorrect json file")
            raise typer.Exit(code=1)
        
        datos_devices["commands"] = commands
        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "single_host": False}
        start = datetime.now()
        netm = AsyncNetmikoPull(set_verbose=set_verbose)
        result = await netm.run(datos_devices)
        end = datetime.now()
        set_verbose = {"verbose": verbose, "result": result, "time": end - start}
        mgmt = ManageOutput(set_verbose=set_verbose)
        await mgmt.create_file()
        mgmt.print_verbose()
    
    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))

@app.command("push-single", help="Push configuration to a Single Host", no_args_is_help=True)
def push_single_host(
        host: Annotated[str, typer.Option("--host", "-h", help="host ip address", rich_help_panel="Connection Parameters", case_sensitive=False)],
        user: Annotated[str, typer.Option("--user", "-u", help="username", rich_help_panel="Connection Parameters", case_sensitive=False)],
        password: Annotated[str, typer.Option(prompt=True, help="password", metavar="password must be provided by keyboard",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],
        device_type: Annotated[DeviceType, typer.Option("--type", "-t", help="device type", rich_help_panel="Connection Parameters", case_sensitive=False)],
        commands: Annotated[List[str], typer.Option("--cmd", "-c", help="commands to configure on device",rich_help_panel="Additional parameters", case_sensitive=False)] = None,
        cmd_file: Annotated[typer.FileText, typer.Option("--cmdf", "-f", help="commands to configure on device", metavar="FILENAME Json file",rich_help_panel="Configuration File Parameters", case_sensitive=False)] = None,
        ssh_config: Annotated[str, typer.Option("--cfg", "-s", help="ssh config file", rich_help_panel="Connection Parameters", case_sensitive=False)] = None,
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters")] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=False)] = None,
    ):

    if commands == None and cmd_file == None:
        typer.echo("Error, you must provide commands or a file with commands")
        raise typer.Exit(code=1)

    async def process():
        if commands == None:
            file_lines = ""
            for line in cmd_file:
                file_lines += line
            try:
                datos_cmds = json.loads(file_lines)
            except json.JSONDecodeError as error:
                typer.echo(f"Error reading json file: {error}")
                raise typer.Exit(code=1)
            
            if datos_cmds.get(host) is None:
                typer.echo(f"Error reading json file: commands not found for host {host} or reading an incorrect json file {cmd_file.name}")
                raise typer.Exit(code=1)
            datos_cmds = datos_cmds.get(host).get('commands')
        
        else:        
            datos_cmds = commands

        datos = {
            "devices": [
                {
                    "host": host,
                    "username": user,
                    "password": password,
                    "device_type": device_type.value,
                    "ssh_config_file": ssh_config
                }
            ],
            "commands": datos_cmds
        }

        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "single_host": True}
        start = datetime.now()
        netm = AsyncNetmikoPushSingle(set_verbose=set_verbose)
        result = await netm.run(datos)
        end = datetime.now()
        set_verbose = {"verbose": verbose, "result": result, "time": end - start}
        mgmt = ManageOutput(set_verbose=set_verbose)
        await mgmt.create_file()
        mgmt.print_verbose()

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("push-multiple", help="Push configuration file to Multiple Hosts", no_args_is_help=True)
def push_multiple_host(
        devices: Annotated[typer.FileText, typer.Option("--hosts", "-h", help="group of hosts", metavar="FILENAME Json file", rich_help_panel="Hosts File Parameters", case_sensitive=False)],
        cmd_file: Annotated[typer.FileText, typer.Option("--cmdf", "-f", help="commands to configure on device", metavar="FILENAME Json file",rich_help_panel="Configuration File Parameters", case_sensitive=False)],
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters")] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=False)] = None,
    ):

    async def process():
        file_lines = ""
        datos = []
        for line in devices:
            file_lines += line
        try:
            datos_devices = json.loads(file_lines)
        except json.JSONDecodeError as error:
            typer.echo(f"Error reading json file: {error}")
            raise typer.Exit(code=1)
        
        if "devices" not in datos_devices:
            typer.echo(f"Error reading json file: devices key not found or reading an incorrect json file {devices.name}")
            raise typer.Exit(code=1)
        list_devices = datos_devices.get("devices")
    
        file_lines = ""
        for line in cmd_file:
            file_lines += line
        try:
            datos_cmds = json.loads(file_lines)
        except json.JSONDecodeError as error:
            typer.echo(f"Error reading json file: {error}")
            raise typer.Exit(code=1)

        for device in list_devices:
            if device.get("host") not in datos_cmds:
                typer.echo(f"Error reading json file: commands not found for host {device.get("host")} or reading an incorrect json file {cmd_file.name}")
                raise typer.Exit(code=1)
        
            dic = {
                "parameters": device,
                "commands": datos_cmds.get(device.get("host")).get('commands')
            }
            datos.append(dic)

        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "single_host": False}
        start = datetime.now()
        netm = AsyncNetmikoPushMultiple(set_verbose=set_verbose)
        result = await netm.run(datos)
        end = datetime.now()
        set_verbose = {"verbose": verbose, "result": result, "time": end - start}
        mgmt = ManageOutput(set_verbose=set_verbose)
        await mgmt.create_file()
        mgmt.print_verbose()

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("templates", help="Download templates to create hosts and config commands files with the necessary information", no_args_is_help=True)
def download_templates(
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters")] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=False)] = None,
    ):
   
    async def process():
        hosts_file_name = "template_netmiko_hosts.json"
        commands_file_name = "template_netmiko_commands.json"
        set_verbose = {"logging": log.value if log != None else None}
        template = Templates(set_verbose=set_verbose)
        result = await template.create_template(hosts_file_name, commands_file_name)
        set_verbose = {"verbose": verbose, "result": result, "time": None}
        mgmt = ManageOutput(set_verbose=set_verbose)
        mgmt.print_verbose()

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.callback(invoke_without_command=True, help="SSH library for network automation")
def callback(ctx: typer.Context):
    """
    SSH library for network automation
    """
    typer.echo(f"-> About to execute Netmiko sub-command: {ctx.invoked_subcommand}")
    

# if __name__ == "__main__":
#     app()