# Progress Bar Service Class
# Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))

import asyncio
import typer

class ProgressBar():
    async def spinner_task(self, stop_event: asyncio.Event, message: str = None):
        spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        while not stop_event.is_set():
            for frame in spinner_frames:
                if message is None:
                    typer.echo(typer.style(f"\r{frame} Processing...", fg=typer.colors.BRIGHT_BLUE), nl=False)
                else:
                    typer.echo(typer.style(f"\r{frame} Processing {message}...", fg=typer.colors.BRIGHT_BLUE), nl=False)
                await asyncio.sleep(0.1)
                if stop_event.is_set():
                    break
        typer.echo(nl=True)


    async def run_with_spinner(self, func, message: str = None, *args, **kwargs):
        stop_event = asyncio.Event()
        spinner_task_coroutine = asyncio.create_task(self.spinner_task(stop_event, message))
        try:
            result = await func(*args, **kwargs)
        finally:
            stop_event.set()
            await spinner_task_coroutine
        
        return result