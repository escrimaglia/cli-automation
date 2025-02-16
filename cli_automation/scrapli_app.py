import sys
import os

from .progress_bar import ProgressBar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))
import typer
from typing_extensions import Annotated
from .service_classes import SyncScrapliPull, AsyncScrapliPull, ManageOutput
import asyncio
import json
from datetime import datetime
from typing import List
from enum import Enum

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
        scra = AsyncScrapliPull(set_verbose)
        start = datetime.now()
        results = await scra.device_connect(datos_devices)
        end = datetime.now()
        set_verbose = {"verbose": verbose, "result": results, "time": end - start}
        mgmt = ManageOutput(set_verbose=set_verbose)
        await mgmt.create_file()
        mgmt.print_verbose()

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))

@app.command("push-data", help="Push data to devices")
def push_data():
    pass

@app.callback(invoke_without_command=True, help="Telnet, SSH or NETCONF library for network automation. Yet under development")
def main(ctx: typer.Context):
    """
    Telnet, SSH or NETCONF library for network automation. Yet under development
    """
    print(f"About to execute command: {ctx.invoked_subcommand}")