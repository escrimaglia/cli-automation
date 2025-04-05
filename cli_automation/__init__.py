import json
from pathlib import Path
import logging
import logging.handlers
from cli_automation.config_srv import *

DATA = {
    "tunnel": False,
    "app": "cla",
}
class ClaConfig():
    def __init__(self):
        self.data = DATA
        self.config_path = Path("config.json")
        self.config = CONFIG_PARAMS
        self.version = "1.4.1 - XXI - By Ed Scrimaglia"

    def load_config(self):
        try:
            self.data.update(self.config)
            with open(self.config_path, "r") as read_file:
                file_read = json.load(read_file)
                file_read["version"] = self.version
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
        self.logger = logging.getLogger("ClaLogger")
        self.logger.setLevel(logging.DEBUG)
        self.log_file = DATA.get("log_file")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.handlers.RotatingFileHandler(self.log_file, maxBytes=5*1024*1024, backupCount=5)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
    
class Html():
    def __init__(self):
        self.nav = Path("navigate.html")
        self.cla = Path("cla.html")

    def create_html(self):
        if not self.nav.exists():
            if self.cla.exists():
                data = self.cla.read_text()
                self.index.write_text(data)

config_data = ClaConfig().load_config()
logger = Logger().get_logger()
Html().create_html()