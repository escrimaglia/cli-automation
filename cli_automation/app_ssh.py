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
from .svc_enums import DeviceType
import json
from .svc_progress import ProgressBar
from datetime import datetime
from cli_automation import logger


app = typer.Typer(no_args_is_help=True)

@app.command("onepull", help="Pull config from a single host", no_args_is_help=True)
def pull_single_host(
        host: Annotated[str, typer.Option("--host", "-h", help="host name or ip address", rich_help_panel="Connection Parameters", case_sensitive=False)],
        user: Annotated[str, typer.Option("--user", "-u", help="username", rich_help_panel="Connection Parameters", case_sensitive=False)],
        password: Annotated[str, typer.Option(prompt=True, help="password", metavar="password must be provided by keyboard",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],
        commands: Annotated[List[str], typer.Option("--cmd", "-c", help="commands to execute on the device", metavar="Multiple -c parameter", rich_help_panel="Connection Parameters", case_sensitive=False)],
        secret: Annotated[str, typer.Option(prompt=True, help="secret", metavar="password must be provided by keyboard to raise privileges",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],
        device_type: Annotated[DeviceType, typer.Option("--type", "-t", help="device type", rich_help_panel="Connection Parameters", case_sensitive=False)],
        port: Annotated[int, typer.Option("--port", "-p", help="port", rich_help_panel="Connection Parameters")] = 22,
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional Parameters", min=0, max=2)] = 0,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", metavar="FILENAME Json file", rich_help_panel="Additional Parameters", case_sensitive=False)] = "output.json",
        global_delay: Annotated[float, typer.Option("--delay", "-d", help="global delay", rich_help_panel="Connection Parameters", min=.1, max=4)] = 0.1,
        ssh_config: Annotated[str, typer.Option("--cfg", "-s", help="ssh config file", rich_help_panel="Connection Parameters", case_sensitive=False)] = None,

    ):
    
    async def process():
        datos = {
            "device": {
                "host": host,
                "username": user,
                "password": password,
                "secret": secret,
                "device_type": device_type.value,
                "port": port,
                "ssh_config_file": ssh_config,
                "global_delay_factor": global_delay
            },
            "commands": commands
        }

        
        inst_dict = {"verbose": verbose, "single_host": True, "logger": logger}
        if verbose == 2:
            print (f"--> data: {json.dumps(datos, indent=3)}")
        start = datetime.now()
        logger.info(f"Running SSH command onepull on device {host}")
        netm = AsyncNetmikoPull(inst_dict=inst_dict)
        result = await netm.run(data=datos)
        end = datetime.now()
        output.write(result)
        if verbose in [1,2]:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("pullconfig", short_help="Pull config from multiple hosts", help="the commands can be entered via the command line or through a JSON file", no_args_is_help=True)
def pull_multiple_host(
        devices: Annotated[typer.FileText, typer.Option("--hosts", "-h", help="group of hosts", metavar="FILENAME Json file", rich_help_panel="Connection Parameters", case_sensitive=False)],
        commands: Annotated[List[str], typer.Option("--cmd", "-c", help="commands to execute on the device", metavar="Multiple -c parameter", rich_help_panel="Connection Parameters", case_sensitive=False)] = None,
        cmd_file: Annotated[typer.FileText, typer.Option("--cmdf", "-f", help="commands to configure on the device", metavar="FILENAME Json file",rich_help_panel="Connection Parameters", case_sensitive=False)] = None,        
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional parameters", min=0, max=2)] = 0,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", metavar="FILENAME Json file", rich_help_panel="Additional parameters", case_sensitive=False)] = "output.json",

    ):

    if commands == None and cmd_file == None:
        typer.echo("** Error, you must provide commands or a file with commands")
        raise typer.Exit(code=1)
    
    async def process():
        datos = []
        if commands == None:
            file_name = cmd_file.name
            try:
                datos_cmds = json.loads(cmd_file.read()) 
            except Exception:
                typer.echo(f"** Error reading the json file {file_name}, check the syntax")
                raise typer.Exit(code=1)
        else:        
            datos_cmds = commands

        file_name = devices.name
        try:
            datos_hosts = json.loads(devices.read())
        except Exception:
            typer.echo(f"** Error reading the json file {file_name}, check the syntax")
            raise typer.Exit(code=1)
        
        if "devices" not in datos_hosts:
            typer.echo(f"Error reading json file: devices key not found in {devices.name} or reading an incorrect json file")
            raise typer.Exit(code=1)
        
        if commands == None:
            list_devices = datos_hosts.get("devices")
            for device in list_devices:
                if device.get("host") not in datos_cmds:
                    typer.echo(f"Error reading json file: commands not found for host {device.get('host')} or reading an incorrect json file {cmd_file.name}")
                    raise typer.Exit(code=1)
                else:
                    if "commands" not in datos_cmds.get(device.get("host")):
                        typer.echo(f"Error reading json file: commands key not found in {cmd_file.name} for host {device.get('host')} or reading an incorrect json file {cmd_file.name}")
                        raise typer.Exit(code=1)
        
                dic = {
                    "device": device,
                    "commands": datos_cmds.get(device.get("host")).get('commands')
                }
                datos.append(dic)
        
        datos_hosts["commands"] = datos_cmds
        inst_dict = {"verbose": verbose, "single_host": False, "logger": logger}
        if verbose == 2:
            print (f"--> data: {json.dumps(datos, indent=3)}")  
        start = datetime.now()
        logger.info(f"Running SSH command pullconfig on devices {devices.name}")
        netm = AsyncNetmikoPull(inst_dict=inst_dict)
        result = await netm.run(data=datos)
        end = datetime.now()
        output.write(result)
        if verbose in [1,2]:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")
       
    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("onepush", short_help="Push config to a single host", help="the commands can be entered via the command line or through a JSON file", no_args_is_help=True)
def push_single_host(
        host: Annotated[str, typer.Option("--host", "-h", help="host name or ip address", rich_help_panel="Connection Parameters", case_sensitive=False)],
        user: Annotated[str, typer.Option("--user", "-u", help="username", rich_help_panel="Connection Parameters", case_sensitive=False)],
        password: Annotated[str, typer.Option(prompt=True, help="password", metavar="password must be provided by keyboard",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],
        secret: Annotated[str, typer.Option(prompt=True, help="enable password", metavar="password for privilege mode",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],        
        device_type: Annotated[DeviceType, typer.Option("--type", "-t", help="device type", rich_help_panel="Connection Parameters", case_sensitive=False)],
        commands: Annotated[List[str], typer.Option("--cmd", "-c", help="commands to configure the device", metavar="Multiple -c parameter", rich_help_panel="Connection Parameters", case_sensitive=False)] = None,
        cmd_file: Annotated[typer.FileText, typer.Option("--cmdf", "-f", help="commands to configure the device", metavar="FILENAME Json file",rich_help_panel="Connection Parameters", case_sensitive=False)] = None,
        port: Annotated[int, typer.Option("--port", "-p", help="port", rich_help_panel="Connection Parameters")] = 22,        
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional Parameters", min=0, max=2)] = 0,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", metavar="FILENAME Json file", rich_help_panel="Additional Parameters", case_sensitive=False)] = "output.json",
        global_delay: Annotated[float, typer.Option("--delay", "-d", help="global delay factor", rich_help_panel="Connection Parameters", min=.1, max=4)] = .1,
        ssh_config: Annotated[str, typer.Option("--cfg", "-s", help="ssh config file", rich_help_panel="Connection Parameters", case_sensitive=False)] = None,

    ):

    if commands == None and cmd_file == None:
        typer.echo("** Error, you must provide commands or a file with commands")
        raise typer.Exit(code=1)

    async def process():
        if commands == None:
            file_name = cmd_file.name
            try:
                datos_cmds = json.loads(cmd_file.read()) 
            except Exception:
                typer.echo(f"** Error reading the json file {file_name}, check the syntax")
                raise typer.Exit(code=1)
            
            if "commands" not in datos_cmds.get(host):
                typer.echo(f"Error reading json file: commands key not found in {cmd_file.name} for host {host} or reading an incorrect json file {cmd_file.name}")
                raise typer.Exit(code=1)
            
            if datos_cmds.get(host) is None:
                typer.echo(f"Error reading json file: commands not found for host {host} or reading an incorrect json file {cmd_file.name}")
                raise typer.Exit(code=1)
            datos_cmds = datos_cmds.get(host).get('commands')
        
        else:        
            datos_cmds = commands

        datos = {
            "device": {
                    "host": host,
                    "username": user,
                    "password": password,
                    "secret": secret,
                    "device_type": device_type.value,
                    "port": port,
                    "global_delay_factor": global_delay,
                    "ssh_config_file": ssh_config
            },
            "commands": datos_cmds
        }

        inst_dict = {"verbose": verbose, "single_host": True, "logger": logger}
        if verbose == 2:
            print (f"--> data: {json.dumps(datos, indent=3)}")
        start = datetime.now()
        logger.info(f"Running SSH command onepush on device {host}")
        netm = AsyncNetmikoPush(inst_dict=inst_dict)
        result = await netm.run(data=datos)
        end = datetime.now()
        output.write(result)
        if verbose in [1,2]:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("pushconfig", short_help="Push config to multiple hosts", help="the commands must be provided through a JSON file", no_args_is_help=True)
def push_multiple_host(
        devices: Annotated[typer.FileText, typer.Option("--hosts", "-h", help="group of hosts", metavar="FILENAME Json file", rich_help_panel="Connection Parameters", case_sensitive=False)],
        cmd_file: Annotated[typer.FileText, typer.Option("--cmd", "-f", help="commands to configure the device", metavar="FILENAME Json file",rich_help_panel="Connection Parameters", case_sensitive=False)],
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional Parameters", min=0, max=2)] = 0,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", metavar="FILENAME Json file", rich_help_panel="Additional Parameters", case_sensitive=False)] = "output.json",

    ):

    async def process():
        datos = []
        file_name = devices.name
        try:
            datos_devices = json.loads(devices.read())
        except Exception:
            typer.echo(f"** Error reading the json file {file_name}, check the syntax")
            raise typer.Exit(code=1)
        
        if "devices" not in datos_devices:
            typer.echo(f"Error reading json file: devices key not found or reading an incorrect json file {devices.name}")
            raise typer.Exit(code=1)
        list_devices = datos_devices.get("devices")

        file_name = cmd_file.name
        try:
            datos_cmds = json.loads(cmd_file.read())
        except Exception:
            typer.echo(f"** Error reading the json file {file_name}, check the syntax")
            raise typer.Exit(code=1)
        
        for device in list_devices:
            if device.get("host") not in datos_cmds:
                typer.echo(f"Error reading json file: commands not found for host {device.get("host")} or reading an incorrect json file {cmd_file.name}")
                raise typer.Exit(code=1)
            else:
                if "commands" not in datos_cmds.get(device.get("host")):
                    typer.echo(f"Error reading json file: commands key not found in {cmd_file.name} for host {device.get('host')} or reading an incorrect json file {cmd_file.name}")
                    raise typer.Exit(code=1)
        
            dic = {
                "device": device,
                "commands": datos_cmds.get(device.get("host")).get('commands')
            }
            datos.append(dic)

        inst_dict = {"verbose": verbose, "single_host": False, "logger": logger}
        if verbose == 2:
            print (f"--> data: {json.dumps(datos, indent=3)}")
        start = datetime.now()
        logger.info(f"Running SSH command pushconfig on devices {devices.name}")
        netm = AsyncNetmikoPush(inst_dict=inst_dict)
        result = await netm.run(data=datos)
        end = datetime.now()
        output.write(result)
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
    
    typer.echo(f"-> About to execute sub-command: {ctx.invoked_subcommand}")
    
# if __name__ == "__main__":
#     app()