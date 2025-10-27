import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".", "..")))

import typer
from typing_extensions import Annotated
from cli_automation import config_data
from cli_automation.svc_progress import ProgressBar
from cli_automation.svc_templates import Templates
import asyncio
from cli_automation import logger, __version__
from cli_automation import app_telnet
from cli_automation import app_tunnel
from cli_automation import app_ssh
from cli_automation.svc_logs import ReadLogs

app = typer.Typer(no_args_is_help=True, pretty_exceptions_short=True)

app.add_typer(app_ssh.app, name="ssh", rich_help_panel="Main Commands")
app.add_typer(app_telnet.app, name="telnet", rich_help_panel="Main Commands")
app.add_typer(app_tunnel.app, name="tunnel", rich_help_panel="Main Commands")

def complete_log_files(incomplete: str):
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.exists(logs_dir):
        return []
    try:
        log_files = []
        for file in os.listdir(logs_dir):
            file_path = os.path.join(logs_dir, file)
            if os.path.isfile(file_path):
                log_files.append(file)        
        if incomplete:
            log_files = [f for f in log_files if f.lower().startswith(incomplete.lower())]
        
        return sorted(log_files)
    except (OSError, PermissionError):
        return []

def check_version(value: bool):
    if value:
        typer.echo (f"version: {__version__}")
        logger.info(f"Checked version: {__version__}")
        raise typer.Exit()


@app.command("templates", 
            short_help="Create examples of configuration files", 
            help="""The cla templates command generates example files, which can be used to create working files, both 
            for connection parameters and for device configuration commands""", 
            rich_help_panel="Main Commands", 
            no_args_is_help=True
            )
def download_templates(
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level",rich_help_panel="Additional parameters", min=0, max=2)] = 1,
    ):
   
    async def process():
        inst_dict = {"logger": logger, "verbose": verbose}
        template = Templates(inst_dict=inst_dict)
        try:
            await template.create_template()
        except Exception as error:
            print (f"** Error creating templates, check the log file and json syntax")
            logger.error(f"Error creating the templates: '{error}'")
            sys.exit(1)
        print ("\n** All the templates have been successfully created")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("logs", short_help="Read logs file", help="Read service logs from the specified log file. By default, it reads from 'cla.log'", rich_help_panel="Main Commands", no_args_is_help=True)
def read_logs(
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Verbose level", rich_help_panel="Additional parameters", min=0, max=2)] = 1,
        log_file: Annotated[str, typer.Option("--log-file", "-l", help="Path to the log file (use Tab for completion)", rich_help_panel="Additional parameters", autocompletion=complete_log_files)] = "cla.log",
    ):
    async def process():
        inst_dict = {"logger": logger, "verbose": verbose}
        log_reader = ReadLogs(inst_dict=inst_dict)
        log_content = log_reader.read_log_file(file_path="logs/" + log_file)
        if verbose in [1,2]:
            if log_content:
                print (log_content)
                logger.info(f"Displayed log content from file {log_file}")
            else:
                logger.error(f"No log content to display in file {log_file}")
                print (f"** No log content to display in file {log_file}")

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
