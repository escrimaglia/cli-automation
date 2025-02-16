import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".", "..")))
import typer
from typing_extensions import Annotated

from cli_automation import netmiko_app
from cli_automation import scrapli_app

__version__ = "1.0.4"

def check_version(value: bool):
    if value:
        print (f"version: {__version__}")
        raise typer.Exit()

app = typer.Typer(no_args_is_help=True)
app.add_typer(netmiko_app.app, name="netmiko")
app.add_typer(scrapli_app.app, name="scrapli")


@app.callback(invoke_without_command=True) 
def get_version(ctx: typer.Context,version: Annotated[bool, typer.Option("--version", "-V", help="Get the app version", rich_help_panel="Check the version",callback=check_version, is_eager=True)] = None):
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


# if __name__ == "__main__":
#     app()