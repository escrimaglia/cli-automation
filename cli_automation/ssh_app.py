# SSH Access Typer Aplication
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))
import typer
from typing_extensions import Annotated
from .ssh_srv import AsyncNetmikoPull, AsyncNetmikoPush
import asyncio
from typing import List
from .enums_srv import Logging
import json
from .progress_bar import ProgressBar
from datetime import datetime
#from .logging import Logger
from . import logger

app = typer.Typer(no_args_is_help=True)
#logger = Logger()


@app.command("pullconfig", help="Pull configurations from Hosts", no_args_is_help=True)
def pull_multiple_host(
        devices: Annotated[typer.FileText, typer.Option("--hosts", "-h", help="group of hosts", metavar="FILENAME Json file", rich_help_panel="Hosts File Parameter", case_sensitive=False)],
        commands: Annotated[List[str], typer.Option("--cmd", "-c", help="commands to execute on device", rich_help_panel="Device Commands Parameter", case_sensitive=False)],
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters", max=2)] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=False)] = Logging.info.value,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", metavar="FILENAME Json file", rich_help_panel="Additional parameters", case_sensitive=False)] = "output.json",

    ):
    
    async def process():
        datos = json.loads(devices.read())
        if "devices" not in datos:
            typer.echo("Error reading json file: devices key not found or reading an incorrect json file")
            raise typer.Exit(code=1)
        
        datos["commands"] = commands
        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "single_host": False, "logger": logger}
        if verbose == 2:
            print (f"--> data: {json.dumps(datos, indent=3)}")  
        start = datetime.now()
        netm = AsyncNetmikoPull(set_verbose=set_verbose)
        result = await netm.run(datos)
        end = datetime.now()
        output.write(result)
        logger.logger.info(f"File {output.name} created")
        if verbose in [1,2]:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")
    
    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("pushconfig", help="Push configuration file to Hosts", no_args_is_help=True)
def push_multiple_host(
        devices: Annotated[typer.FileText, typer.Option("--hosts", "-h", help="group of hosts", metavar="FILENAME Json file", rich_help_panel="Hosts File Parameters", case_sensitive=False)],
        cmd_file: Annotated[typer.FileText, typer.Option("--cmd", "-c", help="commands to configure on device", metavar="FILENAME Json file",rich_help_panel="Configuration File Parameters", case_sensitive=False)],
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters", max=2)] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=False)] = Logging.info.value,
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


@app.callback(invoke_without_command=True, help="Access devices using SSH protocol")
def callback(ctx: typer.Context):
    """
    Access network devices using SSH protocol for automation
    """
    typer.echo(f"-> About to execute {ctx.invoked_subcommand} sub-command")
    

# if __name__ == "__main__":
#     app()