import aiofiles
import sys
from .clilogging import Logger

class CreateFile():
    def __init__(self, set_verbose: dict):
        self.logging = set_verbose.get('logging')
        self.logger = Logger("cla.log",self.logging).set_logger()
        
    async def create_file(self, file_name: str, content: dict) -> None:
        result = {"result": f"File '{file_name}' created"}
        try:
            async with aiofiles.open(file_name, "w") as file:
                await file.write(content)
            self.logger.info(f"File {file_name} created")
            return result
        except Exception as error:
            self.logger.error(f"File {file_name} not created, error {error}")
            print (f"** File '{file_name}' not created, error: {error}")
            sys.exit(1)
