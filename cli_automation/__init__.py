import json
from pathlib import Path
import logging
import logging.handlers
from cli_automation.config_srv import *
import os

DATA = {
    "tunnel": False,
    "app": "cla",
}
__version__ = "1.8.4 - XXI - By Ed Scrimaglia"

class ClaConfig():
    def __init__(self):
        self.data = DATA
        self.config_path = Path("config.json")
        self.config = CONFIG_PARAMS

    def load_config(self):
        try:
            self.data.update(self.config)
            with open(self.config_path, "r") as read_file:
                file_read = json.load(read_file)
                return file_read
        except FileNotFoundError:
            with open(self.config_path, "w") as write_file:
                json.dump(self.data, write_file, indent=3)
                return self.data
        except Exception:
            print ("** Error creating the configuration file")
            SystemExit(1)

class Logger():
    def __init__(self):
        self.log_dir = Path(__file__).parent / "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        os.environ["PATH_LOG"] = str(self.log_dir)
        self.logger = logging.getLogger("ClaLogger")
        self.logger.setLevel(logging.DEBUG)
        self.log_file = self.log_dir / DATA.get("log_file")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.handlers.TimedRotatingFileHandler(
                filename=self.log_file,
                when='midnight',
                interval=1,
                backupCount=7,
                encoding='utf-8',
                utc=False
            )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
    

config_data = ClaConfig().load_config()
logger = Logger().get_logger()
