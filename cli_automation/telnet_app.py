# Telnet Access Typer Aplication
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))
import typer
from typing_extensions import Annotated
from typing import List
from .enums_srv import Logging
from .progress_bar import ProgressBar
from datetime import datetime
from .telnet_srv import AsyncNetmikoTelnet
import asyncio
import json
from .logging import Logger
from pathlib import Path

app = typer.Typer(no_args_is_help=True)
logger = Logger()

def validate_file():
    file_name = Path("config.json")
    if not file_name.exists():
        print(f"** File {file_name} not found. Please run the command 'cla templates -v' to create the file\n")
        raise SystemExit(1) 

@app.command("pullsingle", help="Pull data from a Single Host", no_args_is_help=True)
def pull_single_host(
        host: Annotated[str, typer.Option("--host", "-h", help="host ip address", rich_help_panel="Connection Parameters", case_sensitive=False)],
        user: Annotated[str, typer.Option("--user", "-u", help="username", rich_help_panel="Connection Parameters", case_sensitive=False)],
        password: Annotated[str, typer.Option(prompt=True, help="password", metavar="password must be provided by keyboard",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)],
        command: Annotated[str, typer.Option("--cmd", "-c", help="commands to execute on device", rich_help_panel="Device Commands Parameter", case_sensitive=False)],
        secret: Annotated[str, typer.Option(prompt=True, help="secret", metavar="password must be provided by keyboard to raise privileges",rich_help_panel="Connection Parameters", case_sensitive=False, hide_input=True, hidden=True)] = None,
        device_type: Annotated[str, typer.Option("--type", "-t", help="device type", rich_help_panel="Connection Parameters", case_sensitive=False)] = "generic_telnet",
        port: Annotated[int, typer.Option("--port", "-p", help="port", rich_help_panel="Connection Parameters", case_sensitive=False)] = 23,
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters")] = 0,
        log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=True)] = Logging.info.value,
        output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", rich_help_panel="Additional parameters", case_sensitive=False)] = "output.json",
        global_delay: Annotated[float, typer.Option("--delay", "-d", help="port", rich_help_panel="Connection Parameters", case_sensitive=False)] = 0.1,
    ):

    async def process():
        datos = {
            "devices": [
                {
                    "host": host,
                    "username": user,
                    "password": password,
                    "device_type": device_type,
                    "port": port,
                    "secret": secret,
                    "session_log": "cla.log",
                    "global_delay_factor": global_delay
                }
            ],
            "command": command
        }

        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "logger": logger.logger}
        if verbose == 2:
            print (f"--> Parameters: {datos}")
            print (f"--> Verbose: {set_verbose}")
        start = datetime.now()
        device = AsyncNetmikoTelnet(set_verbose)
        result = await device.run(datos)
        end = datetime.now()
        output.write(result)
        logger.logger.info(f"File {output.name} created")
        if verbose in [1,2]:
            print (f"{result}")  
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("pullmultiple", help="Pull data from Multiple Hosts", no_args_is_help=True)
def pull_multiple_host(
    devices: Annotated[typer.FileText, typer.Option("--hosts", "-h", help="group of hosts", metavar="FILENAME Json file", rich_help_panel="Hosts File Parameter", case_sensitive=False)],
    command: Annotated[str, typer.Option("--cmd", "-c", help="commands to execute on device", rich_help_panel="Device Commands Parameter", case_sensitive=False)],
    verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters")] = 0,
    log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=False)] = Logging.info.value,
    output: Annotated[typer.FileTextWrite, typer.Option("--output", "-o", help="output file", rich_help_panel="Additional parameters", case_sensitive=False)] = "output.json",
    ):

    async def process():
        datos = json.loads(devices.read())
        if "devices" not in datos:
            typer.echo("Error reading json file: devices key not found or reading an incorrect json file")
            raise typer.Exit(code=1)
        
        datos["command"] = command
        set_verbose = {"verbose": verbose, "logging": log.value if log != None else None, "logger": logger.logger}
        if verbose == 2:
            print (f"--> Parameters: {datos}")
            print (f"--> Verbose: {set_verbose}")
        start = datetime.now()
        device = AsyncNetmikoTelnet(set_verbose)
        result = await device.run(datos)
        end = datetime.now()
        output.write(result)
        logger.logger.info(f"File {output.name} created")
        if verbose in [1,2]:
            print (f"{result}")  
            print (f"-> Execution time: {end - start}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))

@app.command("push-single", help="Push configuration to a Single Host", no_args_is_help=True)
def push_single_host():
    pass


@app.command("push-multiple", help="Push configuration file to Multiple Hosts", no_args_is_help=True)
def puh_multiple_host():
    pass


@app.callback(invoke_without_command=True, help="Access devices using Telnet protocol")
def callback(ctx: typer.Context):
    """
    Access devices using Telnet protocol
    """
    validate_file()
    typer.echo(f"-> About to execute {ctx.invoked_subcommand} sub-command")

# if __name__ == "__main__":
#     app()