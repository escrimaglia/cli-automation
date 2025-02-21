# SSH Access Typer Aplication
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))
import typer
from typing_extensions import Annotated
from .service_classes import AsyncNetmikoPull, AsyncNetmikoPushSingle, AsyncNetmikoPushMultiple
import asyncio
from typing import List
from .enum_classes import Logging, DeviceType
import json
from .progress_bar import ProgressBar
from datetime import datetime
from .create_file import CreateFile

app = typer.Typer(no_args_is_help=True)


@app.command("pullsingle", help="Pull data from a Single Host", no_args_is_help=True)
def pull_single_host(
        host: Annotated[str, typer.Option("--host", "-h", help="host ip address", rich_help_panel="Connection Parameters", case_sensitive=False)],
        user: Annotated[str, typer.Option("--user", "-u", help="username", rich_help_panel="Connection Parameters", case_sensitive=False)],
        password: Annotated[str, typer.Option(prompt=True, help="password", metavar="password must be provided by keyboard",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],
        commands: Annotated[List[str], typer.Option("--cmd", "-c", help="commands to execute on device", rich_help_panel="Commands Parameter", case_sensitive=False)],
        secret: Annotated[str, typer.Option(prompt=True, help="secret", metavar="password must be provided by keyboard to raise privileges",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)] = None,
        device_type: Annotated[DeviceType, typer.Option("--type", "-t", help="device type", rich_help_panel="Connection Parameters", case_sensitive=False)] = "generic_telnet",
        port: Annotated[int, typer.Option("--port", "-p", help="port", rich_help_panel="Connection Parameters", case_sensitive=False)] = 22,
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters")] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=True)] = None,
        global_delay: Annotated[float, typer.Option("--delay", "-d", help="port", rich_help_panel="Connection Parameters", case_sensitive=False)] = 0.1,
        ssh_config: Annotated[str, typer.Option("--cfg", "-s", help="ssh config file", rich_help_panel="Connection Parameters", case_sensitive=False)] = None,

    ):
    
    async def process():
        datos = {
            "devices": [
                {
                    "host": host,
                    "username": user,
                    "password": password,
                    "secret": secret,
                    "device_type": device_type.value,
                    "port": port,
                    "ssh_config_file": ssh_config,
                    "global_delay_factor": global_delay
                }
            ],
            "commands": commands
        }

        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "single_host": True}
        start = datetime.now()
        netm = AsyncNetmikoPull(set_verbose=set_verbose)
        result = await netm.run(datos)
        end = datetime.now()
        cf = CreateFile(set_verbose=set_verbose)
        await cf.create_file("output.json", result)
        if verbose >= 2:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("pullmultiple", help="Pull data from Multiple Hosts", no_args_is_help=True)
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
        cf = CreateFile(set_verbose=set_verbose)
        await cf.create_file("output.json", result)
        if verbose >= 2:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")
    
    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))

@app.command("pushsingle", help="Push configuration to a Single Host", no_args_is_help=True)
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
        cf = CreateFile(set_verbose=set_verbose)
        await cf.create_file("output.json", result)
        if verbose >= 2:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("pushmultiple", help="Push configuration file to Multiple Hosts", no_args_is_help=True)
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
        cf = CreateFile(set_verbose=set_verbose)
        await cf.create_file("output.json", result)
        if verbose >= 2:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("templates", help="Download templates to create hosts and config commands files with the necessary information", no_args_is_help=True)
def download_templates(
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters")] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=False)] = None,
    ):
    from templates import Templates
   
    async def process():
        hosts_file_name = "template_netmiko_hosts.json"
        commands_file_name = "template_commands.json"
        set_verbose = {"logging": log.value if log != None else None}
        template = Templates(set_verbose=set_verbose)
        result = await template.create_template(hosts_file_name, commands_file_name)
        if verbose >= 2:
            print (f"\n{result}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.callback(invoke_without_command=True, help="Access devices using SSH protocol")
def callback(ctx: typer.Context):
    """
    Access devices using SSH protocol
    """
    typer.echo(f"-> About to execute {ctx.invoked_subcommand} sub-command")
    

# if __name__ == "__main__":
#     app()