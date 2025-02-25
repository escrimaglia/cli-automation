import aiofiles
import sys
from . import logger

class ManageFiles():
    def __init__(self):
        self.logger = logger
        
    async def create_file(self, file_name: str, content: str) -> None:
        try:
            async with aiofiles.open(file_name, "w") as file:
                await file.write(content)
            self.logger.info(f"File {file_name} created")
        except Exception as error:
            self.logger.error(f"File {file_name} not created, error {error}")
            print (f"\n** File {file_name} not created, error: {error}")
            sys.exit(1)

    async def read_file(self, file_name: str) -> str:
        try:
            async with aiofiles.open(file_name, "r") as file:
                content = await file.read()
            self.logger.info(f"File {file_name} read")
            return content
        except Exception as error:
            self.logger.error(f"File {file_name} not read, error {error}")
            print (f"\n** File {file_name} not read, error: {error}")
            return None
            