import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".", "..")))

import typer
from typing_extensions import Annotated
from cli_automation import config_data
from cli_automation.svc_progress import ProgressBar
from cli_automation.svc_templates import Templates
import asyncio
from cli_automation import logger

from cli_automation import app_telnet
from cli_automation import app_tunnel
from cli_automation import app_ssh


app = typer.Typer(no_args_is_help=True, pretty_exceptions_short=True)

def check_version(value: bool):
    if value:
        typer.echo (f"version: {config_data.get("version")}")
        raise typer.Exit()

app.add_typer(app_ssh.app, name="ssh", rich_help_panel="Main Commands")
app.add_typer(app_telnet.app, name="telnet", rich_help_panel="Main Commands")
app.add_typer(app_tunnel.app, name="tunnel", rich_help_panel="Main Commands")


@app.command("templates", 
            short_help="Create examples of configuration files", 
            help="""The cla templates command generates example files, which can be used to create working files, both 
            for connection parameters and for device configuration commands""", 
            rich_help_panel="Main Commands", 
            no_args_is_help=True
            )
def download_templates(
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters", min=0, max=2)] = 1,
        #log: Annotated[Logging, typer.Option("--log", "-l", help="Log level", rich_help_panel="Additional parameters", case_sensitive=False)] = Logging.info.value,
    ):
   
    async def process():
        inst_dict = {"logger": logger, "verbose": verbose}
        template = Templates(inst_dict=inst_dict)
        try:
            await template.create_template()
        except Exception as error:
            print (f"** Error creating templates, check the log file and json syntax")
            logger.error(f"Error creating the templates: {error}")
            sys.exit(1)
        print ("\n** All the templates have been successfully created")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.callback(
        short_help="Runs the Application commands",
        help="""The CLA `Command Line interface Automation` is an Async Typer Python-based application designed to automate infrastructure directly from the command line. With CLA,
        there is no need to write a single line of code, users simply follow the options presented in the help menu. When I thought about building CLA, I considered those
        network engineers who have not yet acquired the necessary software knowledge, so `CLA was specifically designed to enable engineers who have not yet acquired software 
        knowledge to progress in the practice of automation`. CLA lets you both extract configurations and set up networking devices. You can enter 
        connection and configuration parameters either via the command line or using JSON files. Another reason I decided to develop CLA is to enable its commands to be invoked 
        from any programming language, once again, without requiring a single line of code for automation. CLA version 1.X.X focuses exclusively on Network Automation, while version 
        2.X.X will introduce Cloud Automation capabilities.
        """
    )
def main(ctx: typer.Context,
            version: Annotated[bool, 
            typer.Option("--version", "-V", 
            rich_help_panel="Check the version",
            callback=check_version,
            is_eager=True)] = None):
    
    if ctx.invoked_subcommand is None:
        typer.echo("Please specify a command, try --help")
        raise typer.Exit(1)
    typer.echo (f"-> About to execute command: {ctx.invoked_subcommand}")


# if __name__ == "__main__":  
#     app()