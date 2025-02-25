import json
from pathlib import Path
import logging
import logging.handlers

json_path = Path(__file__).parent / "config.json"

class ClaConfig():
    def __init__(self):
        try:
            with open(json_path, "r") as read_file:
                self.config_data = json.load(read_file)
        except FileNotFoundError as error:
            print(f"** File config.json not found. Please run the command 'cla templates -v' to create the file\n")
            exit(1)

    def get_config(self):
        return self.config_data

class Logger:
    def __init__(self):
        self.logger = logging.getLogger("ClaLogger")
        self.logger.setLevel(logging.DEBUG)
        self.log_file = "cla.log"
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #handler = logging.StreamHandler()
        #handler.setFormatter(formatter)
        file_handler = logging.handlers.RotatingFileHandler(self.log_file, maxBytes=5*1024*1024, backupCount=5)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        #self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger
    
config_data = ClaConfig().get_config()
logger = Logger().get_logger()