import sys
import os
import typer
from typing_extensions import Annotated
from cli_automation import config_data
from cli_automation.enums_srv import Logging
from cli_automation.progress_bar import ProgressBar
from cli_automation.templates_srv import Templates
import asyncio
from cli_automation import logger

from cli_automation import telnet_app
from cli_automation import tunnel_app
from cli_automation import ssh_app
#from cli_automation import templates_app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".", "..")))

app = typer.Typer()

def check_version(value: bool):
    if value:
        typer.echo (f"version: {config_data.get("version")}")
        raise typer.Exit()

app.add_typer(ssh_app.app, name="ssh", rich_help_panel="Main Commands")
app.add_typer(telnet_app.app, name="telnet", rich_help_panel="Main Commands")
app.add_typer(tunnel_app.app, name="tunnel", rich_help_panel="Main Commands")
#app.add_typer(templates_app.app, name="files", rich_help_panel="Main Commands")


@app.command("templates", short_help="Create working files", 
            help="Download templates to create the working files", 
            rich_help_panel="Main Commands", 
            no_args_is_help=True
            )
def download_templates(
    verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters")] = 0,
    log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=False)] = Logging.info.value,
    ):
   
    async def process():
        set_verbose = {"logging": log.value if log != None else None, "logger": logger}
        template = Templates(set_verbose=set_verbose)
        await template.create_template(file_name=None)
        if verbose in [1,2]:
            print ("\nAll the templates have been successfully created")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


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
    typer.echo (f"-> About to execute command: {ctx.invoked_subcommand}")

if __name__ == "__main__":  
    app()