import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".", "..")))
import typer
from typing_extensions import Annotated
import asyncio
from cli_automation.enums_srv import Logging
from cli_automation.progress_bar import ProgressBar
from cli_automation.templates_srv import Templates
from cli_automation.logging import Logger
from cli_automation.files_srv import ManageFiles
import json
from pathlib import Path

from cli_automation import telnet_app
from cli_automation import tunnel_app
from cli_automation import ssh_app
from cli_automation import templates_app

logger = Logger()

app = typer.Typer(no_args_is_help=True)

__version__ = ""

def check_version(value: bool):
    if value:
        validate_file()
        print (f"version: {__version__}")
        raise typer.Exit()


def validate_file():
    file_name = Path("config.json")
    if not file_name.exists():
        print(f"** File {file_name} not found. Please run the command 'cla templates -v' to create the file\n")
        raise SystemExit(1)
    else:
        # Read the file take version value
        with open(file_name, "r") as file:
            data = json.load(file)
            global __version__
            __version__ = data.get("version")
        pass


app.add_typer(ssh_app.app, name="ssh", rich_help_panel="Main Commands")
app.add_typer(telnet_app.app, name="telnet", rich_help_panel="Main Commands")
app.add_typer(tunnel_app.app, name="tunnel", rich_help_panel="Main Commands")
app.add_typer(templates_app.app, rich_help_panel="Main Commands")


@app.callback()
def main(ctx: typer.Context,
                version: Annotated[bool, 
                typer.Option("--version", "-V", 
                help="Get the app version", 
                rich_help_panel="Check the version",
                callback=check_version,
                is_eager=True)] = None):
    """
    CLA (Command Line interface Automation) is a Python-based application designed to automate infrastructure directly from the command line. 
    With CLA, there is no need to write a single line of code, users simply follow the options presented in the help menu. It was specifically 
    developed for networking engineers who have not yet advanced in programming knowledge.  
    LA version 1 focuses exclusively on Network Automation, while version 2 will introduce Cloud Automation capabilities.
    """
    if ctx.invoked_subcommand is None:
        typer.echo("Please specify a command, try --help")
        raise typer.Exit(1)
    typer.echo(f"-> About to execute command: {ctx.invoked_subcommand}")
