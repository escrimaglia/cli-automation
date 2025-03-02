# Telnet Access Typer Aplication
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))

import typer
from typing_extensions import Annotated
from .svc_enums import Logging
from .svc_progress import ProgressBar
from datetime import datetime
from .svc_telnet import AsyncNetmikoTelnetPull, AsyncNetmikoTelnetPush
import asyncio
import json
from . import logger

app = typer.Typer(no_args_is_help=True)

@app.command("pullconfig", help="Pull config from multiple hosts", no_args_is_help=True)
def pull_multiple_host(
        devices: Annotated[typer.FileText, typer.Option("--hosts", "-h", help="group of hosts", metavar="FILENAME Json file", rich_help_panel="Hosts File Parameter", case_sensitive=False)],
        command: Annotated[str, typer.Option("--cmd", "-c", help="commands to execute on the device", rich_help_panel="Device Commands Parameter", case_sensitive=False)],
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional parameters", min=0, max=2)] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="log level", rich_help_panel="Additional parameters", case_sensitive=False)] = Logging.info.value,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", metavar="FILENAME text file",rich_help_panel="Additional parameters", case_sensitive=False)] = "output.txt",
    ):

    async def process():
        datos = json.loads(devices.read())
        if "devices" not in datos:
            typer.echo("Error reading json file: devices key not found or reading an incorrect json file")
            raise typer.Exit(code=1)
        
        datos["command"] = command
        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "logger": logger}
        if verbose == 2:
            print (f"--> data: {json.dumps(datos, indent=3)}")
        start = datetime.now()
        device = AsyncNetmikoTelnetPull(set_verbose)
        result = await device.run(datos)
        end = datetime.now()
        output.write(result)
        logger.info(f"File {output.name} created")
        if verbose in [1,2]:
            print (f"{result}")  
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))

@app.command("pushconfig", help="Push config file to multiple hosts", no_args_is_help=True)
def push_multiple_host(
        devices: Annotated[typer.FileText, typer.Option("--hosts", "-h", help="group of hosts", metavar="FILENAME Json file", rich_help_panel="Hosts File Parameters", case_sensitive=False)],
        cmd_file: Annotated[typer.FileText, typer.Option("--cmd", "-c", help="commands to configure on the device", metavar="FILENAME Json file",rich_help_panel="Configuration File Parameters", case_sensitive=False)],
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional parameters", min=0, max=2)] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="log level", rich_help_panel="Additional parameters", case_sensitive=False)] = Logging.info.value,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", metavar="FILENAME text file", rich_help_panel="Additional parameters", case_sensitive=False)] = "output.json",
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
        netm = AsyncNetmikoTelnetPush(set_verbose=set_verbose)
        result = await netm.run(datos)
        end = datetime.now()
        output.write(result)
        logger.logger.info(f"File {output.name} created")
        if verbose in [1,2]:
            print (f"\n{result}")
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.callback(invoke_without_command=True, short_help="Accesses devices via the Telnet protocol")
def callback(ctx: typer.Context):
    """
    Telnet was added to CLA to access older devices that, for some reason, do not support SSH. Telnet operates in a generic way,
     and configuration commands must follow the structure explained in the `example_telnet_commands_structure.json file`, file generated by the `cla templates` command. 
    However, whenever possible, SSH remains the preferred protocol.
    """
    typer.echo(f"-> About to execute {ctx.invoked_subcommand} sub-command")

# if __name__ == "__main__":
#     app()