# Managing SOCK5 Tunnel with Bastion Host Typer Application
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))

import typer
from typing_extensions import Annotated
from .svc_progress import ProgressBar
import asyncio
from .svc_tunnel import SetSocks5Tunnel
from . import logger, config_data

app = typer.Typer(no_args_is_help=True)

@app.command("setup", short_help="Setup a tunnel to the Bastion Host", no_args_is_help=True)
def set_tunnel(
        bastion_user: Annotated[str, typer.Option("--user", "-u", help="bastion host username", rich_help_panel="Tunnel Parameters", case_sensitive=False)],
        bastion_host: Annotated[str, typer.Option("--bastion", "-b", help="bastion name or ip address", rich_help_panel="Tunnel Parameters", case_sensitive=False)],
        local_port: Annotated[int, typer.Option("--port", "-p", help="local port", rich_help_panel="Tunnel Parameters", min=1000, max=1100)] = config_data.get("tunnel_local_port", 1080),
        timeout: Annotated[int, typer.Option("--timeout", "-t", help="timeout in seconds for the tunnel startup", rich_help_panel="Tunnel Parameters", min=3, max=25)] = config_data.get("tunnel_timeout", 10),
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional Parameters", min=0, max=2)] = 1,
    ):

    async def process():
        inst_dict = {"verbose": verbose, "logger": logger}
        tunnel = SetSocks5Tunnel(inst_dict)
        tunnel_pid, msg = await tunnel.start_tunnel(timeout=timeout, bastion_user=bastion_user, bastion_host=bastion_host, local_port=local_port)
        if tunnel_pid:    
            print (f"\n** Tunnel started successfully for user: {bastion_user}, bastion host: {bastion_host}, local-port: {local_port}, PID: {tunnel_pid}")
        else:
            print (f"\n** Tunnel failed to start for user: {bastion_user}, bastion host: {bastion_host}, local-port: {local_port}. \n{msg}")

    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.command("kill", short_help="Kill the tunnel to the bastion Host")
def kill_tunnel(
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional Parameters", min=0, max=2)] = 1,
    ):
   
    async def process():
        inst_dict = {"verbose": verbose, "logger": logger}
        tunnel = SetSocks5Tunnel(inst_dict)
        await tunnel.kill_tunnel()
        
    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))

@app.command("status", short_help="Check the tunnel status", no_args_is_help=True)
def check_tunnel(
        local_port: Annotated[int, typer.Option("--port", "-p", help="local port", rich_help_panel="Tunnel Parameters", min=1000, max=1100)] = config_data.get("tunnel_local_port", 1080),
        timeout: Annotated[int, typer.Option("--timeout", "-t", help="timeout in seconds for the tunnel return its status", rich_help_panel="Tunnel Parameters", min=3, max=20)] = config_data.get("tunnel_timeout", 10),
        test_port: Annotated[int, typer.Option("--test", "-r", help="remote port for testing the tunnel", rich_help_panel="Tunnel Parameters")] = config_data.get("tunnel_port_test", 22),
        verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="verbose level",rich_help_panel="Additional Parameters", min=0, max=2)] = 1,
    ):
    
    async def process():
        inst_dict = {"verbose": verbose, "logger": logger}
        tunnel = SetSocks5Tunnel(inst_dict)
        tunnel_status = await tunnel.tunnel_status(timeout=timeout,test_port=test_port, local_port=local_port)
        if tunnel_status:
            typer.echo (f"\n** Tunnel is running at local-port {local_port}")
        else:
            typer.echo (f"\n** Tunnel is not running at local-port {local_port}. Check the log file if you suspect inconsistencies")
      
    progress = ProgressBar()
    asyncio.run(progress.run_with_spinner(process))


@app.callback(invoke_without_command=True, short_help="Manage tunnel with Bastion Host")
def callback(ctx: typer.Context):
    """
    Sometimes, the machine running CLA doesn’t have direct access to the devices and must go through a Bastion Host or Jump Host. To connect via a Bastion Host, 
    you can either configure SSH specifically or set up a tunnel. Personally, I think creating a tunnel is more efficient since it avoids SSH configuration, 
    specially when using `Telnet` commands. 
    Using `cla tunnel`, you can create or remove a SOCKS5 tunnel. For `cla tunnel` to function properly, the host running CLA must have easy access to the 
    Bastion Host (it should be listed in the Bastion Host's known_hosts file). CLA constantly monitors the tunnel’s status, but you can also manually check it using 
    the Linux command `lsof -i:{local_port}`.
    """
    typer.echo(f"-> About to execute sub-command: {ctx.invoked_subcommand}")
    

# if __name__ == "__main__":
#     app()