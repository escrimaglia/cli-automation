import typer
from typing_extensions import Annotated
from .enums_srv import Logging
from .progress_bar import ProgressBar
from .templates_srv import Templates
import asyncio
from . import logger

app = typer.Typer(no_args_is_help=True)

@app.command("create-files", help="Download templates to create the working files", rich_help_panel="Main Commands", no_args_is_help=True)
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


@app.callback(invoke_without_command=True, help="Create examples of working files")
def callback(ctx: typer.Context):
    """
    Download templates to create the working files. The templates are examples of the working files.
    """
    typer.echo(f"-> About to execute {ctx.invoked_subcommand} sub-command")

# if __name__ == "__main__":
#     app()