# SSH Access Typer Aplication
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))

import typer
from typing_extensions import Annotated
from .svc_ssh import AsyncNetmikoPull, AsyncNetmikoPush
import asyncio
from typing import List
from .svc_enums import Logging, DeviceType
import json
from .svc_progress import ProgressBar
from datetime import datetime
from . import logger


app = typer.Typer(no_args_is_help=True)

@app.command("onepull", help="Pull config from a single host", no_args_is_help=True)
def pull_single_host(
        host: Annotated[str, typer.Option("--host", "-h", help="host name or ip address", rich_help_panel="Connection Parameters", case_sensitive=False)],
        user: Annotated[str, typer.Option("--user", "-u", help="username", rich_help_panel="Connection Parameters", case_sensitive=False)],
        password: Annotated[str, typer.Option(prompt=True, help="password", metavar="password must be provided by keyboard",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],
        commands: Annotated[List[str], typer.Option("--cmd", "-c", help="commands to execute on the device", rich_help_panel="Commands Parameter", case_sensitive=False)],
        secret: Annotated[str, typer.Option(prompt=True, help="secret", metavar="password must be provided by keyboard to raise privileges",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],
        device_type: Annotated[DeviceType, typer.Option("--type", "-t", help="device type", rich_help_panel="Connection Parameters", case_sensitive=False)],
        port: Annotated[int, typer.Option("--port", "-p", help="port", rich_help_panel="Connection Parameters")] = 22,
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional parameters", min=0, max=2)] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="log level", rich_help_panel="Additional parameters", case_sensitive=True)] = Logging.info.value,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", rich_help_panel="Additional parameters", case_sensitive=False)] = "output.json",
        global_delay: Annotated[float, typer.Option("--delay", "-d", help="global delay", rich_help_panel="Connection Parameters", min=.1, max=4)] = 0.1,
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

        
        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "single_host": True, "logger": logger}
        if verbose == 2:
            print (f"--> data: {json.dumps(datos, indent=3)}")
        start = datetime.now()
        netm = AsyncNetmikoPull(set_verbose=set_verbose)
        result = await netm.run(datos)
        end = datetime.now()
        output.write(result)
        if verbose in [1,2]:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("pullconfig", help="Pull config from multiple hosts", no_args_is_help=True)
def pull_multiple_host(
        devices: Annotated[typer.FileText, typer.Option("--hosts", "-h", help="group of hosts", metavar="FILENAME Json file", rich_help_panel="Hosts File Parameter", case_sensitive=False)],
        commands: Annotated[List[str], typer.Option("--cmd", "-c", help="commands to execute on the device", rich_help_panel="Device Commands Parameter", case_sensitive=False)],
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional parameters", min=0, max=2)] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="log level", rich_help_panel="Additional parameters", case_sensitive=False)] = Logging.info.value,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", metavar="FILENAME Json file", rich_help_panel="Additional parameters", case_sensitive=False)] = "output.json",

    ):
    
    async def process():
        datos = json.loads(devices.read())
        if "devices" not in datos:
            typer.echo("Error reading json file: devices key not found or reading an incorrect json file")
            raise typer.Exit(code=1)
        
        command = json.loads(commands.read())
        print (f"command: {command}")
        datos["commands"] = command
        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "single_host": False, "logger": logger}
        if verbose == 2:
            print (f"--> data: {json.dumps(datos, indent=3)}")  
        start = datetime.now()
        netm = AsyncNetmikoPull(set_verbose=set_verbose)
        result = await netm.run(datos)
        end = datetime.now()
        if verbose in [1,2]:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")
        output.write(result)
    
    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("onepush", help="Push config to a single host", no_args_is_help=True)
def push_single_host(
        host: Annotated[str, typer.Option("--host", "-h", help="host name or ip address", rich_help_panel="Connection Parameters", case_sensitive=False)],
        user: Annotated[str, typer.Option("--user", "-u", help="username", rich_help_panel="Connection Parameters", case_sensitive=False)],
        password: Annotated[str, typer.Option(prompt=True, help="password", metavar="password must be provided by keyboard",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],
        secret: Annotated[str, typer.Option(prompt=True, help="enable password", metavar="password for privilege mode",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],        
        device_type: Annotated[DeviceType, typer.Option("--type", "-t", help="device type", rich_help_panel="Connection Parameters", case_sensitive=False)],
        commands: Annotated[List[str], typer.Option("--cmd", "-c", help="commands to configure on the device",rich_help_panel="Config Parameters", case_sensitive=False)] = None,
        cmd_file: Annotated[typer.FileText, typer.Option("--cmdf", "-f", help="commands to configure on the device", metavar="FILENAME Json file",rich_help_panel="Config Parameters", case_sensitive=False)] = None,
        port: Annotated[int, typer.Option("--port", "-p", help="port", rich_help_panel="Connection Parameters")] = 22,        
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional parameters", min=0, max=2)] = 0,
        log: Annotated[Logging, typer.Option("--llog", "-l", help="log level", rich_help_panel="Additional parameters", case_sensitive=False)] = Logging.info.value,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", rich_help_panel="Additional parameters", case_sensitive=False)] = "output.json",
        global_delay: Annotated[float, typer.Option("--delay", "-d", help="global delay factor", rich_help_panel="Connection Parameters", min=.1, max=4)] = .1,
        ssh_config: Annotated[str, typer.Option("--cfg", "-s", help="ssh config file", rich_help_panel="Connection Parameters", case_sensitive=False)] = None,

    ):

    if commands == None and cmd_file == None:
        typer.echo("Error, you must provide commands or a file with commands")
        raise typer.Exit(code=1)

    async def process():
        if commands == None:
            datos_cmds = json.loads(cmd_file.read()) 
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
                    "secret": secret,
                    "device_type": device_type.value,
                    "port": port,
                    "global_delay_factor": global_delay,
                    "ssh_config_file": ssh_config
                }
            ],
            "commands": datos_cmds
        }

        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "single_host": True, "logger": logger}
        if verbose == 2:
            print (f"--> data: {json.dumps(datos, indent=3)}")
        start = datetime.now()
        netm = AsyncNetmikoPush(set_verbose=set_verbose)
        result = await netm.run(datos)
        end = datetime.now()
        output.write(result)
        if verbose in [1,2]:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("pushconfig", help="Push config file to multiple hosts", no_args_is_help=True)
def push_multiple_host(
        devices: Annotated[typer.FileText, typer.Option("--hosts", "-h", help="group of hosts", metavar="FILENAME Json file", rich_help_panel="Hosts File Parameters", case_sensitive=False)],
        cmd_file: Annotated[typer.FileText, typer.Option("--cmd", "-c", help="commands to configure on the device", metavar="FILENAME Json file",rich_help_panel="Configuration File Parameters", case_sensitive=False)],
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional parameters", min=0, max=2)] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="log level", rich_help_panel="Additional parameters", case_sensitive=False)] = Logging.info.value,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", metavar="FILENAME Json file", rich_help_panel="Additional parameters", case_sensitive=False)] = "output.json",

    ):

    async def process():
        datos = []
        datos_devices = json.loads(devices.read())
        if "devices" not in datos_devices:
            typer.echo(f"Error reading json file: devices key not found or reading an incorrect json file {devices.name}")
            raise typer.Exit(code=1)
        list_devices = datos_devices.get("devices")
    
        datos_cmds = json.loads(cmd_file.read())
        for device in list_devices:
            if device.get("host") not in datos_cmds:
                typer.echo(f"Error reading json file: commands not found for host {device.get("host")} or reading an incorrect json file {cmd_file.name}")
                raise typer.Exit(code=1)
        
            dic = {
                "device": device,
                "commands": datos_cmds.get(device.get("host")).get('commands')
            }
            datos.append(dic)

        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "single_host": False, "logger": logger}
        if verbose == 2:
            print (f"--> data: {json.dumps(datos, indent=3)}")
        start = datetime.now()
        netm = AsyncNetmikoPush(set_verbose=set_verbose)
        result = await netm.run(datos)
        end = datetime.now()
        output.write(result)
        logger.logger.info(f"File {output.name} created")
        if verbose in [1,2]:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.callback(invoke_without_command=True, short_help="Accesses devices via the SSH protocol")
def callback(ctx: typer.Context):
    """
    The cla ssh command allows access to devices via the SSH protocol. The command can be used to pull or push configurations to devices.
    To structure the output data when retrieving configurations, the `cla ssh pullconfig` command uses TextFSM templates. If the query 
    command is included in the templates, the output will be in JSON format; otherwise, the output will be in TXT format.
    """
    
    typer.echo(f"-> About to execute {ctx.invoked_subcommand} sub-command")
    
# if __name__ == "__main__":
#     app()