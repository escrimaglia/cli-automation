import json
from pathlib import Path
import logging
import logging.handlers


DATA = {
    "tunnel": False,
    "version": "1.1.0 - XXI - By Ed Scrimaglia",
    "app": "cla",
    "log_file": "cla.log",
    "telnet_prompts": [">", "#", "(config)#", "(config-if)#", "$", "%", "> (doble)","# (doble)", "?", ")", "!", "*", "~", ":]", "]", ">", "##"],
    "proxy_port_test": 22,
    "proxy_timeout_test": 10
}
class ClaConfig():
    def __init__(self):
        self.data = DATA
        self.config_path = Path(__file__).parent / "config.json"

    def load_config(self):
        try:
            with open(self.config_path, "r") as read_file:
                return json.load(read_file)
        except FileNotFoundError:
            with open(self.config_path, "w") as write_file:
                json.dump(DATA, write_file, indent=3)
                return self.data

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
        self.index = Path("navigate.html")
        self.cla = Path("cla.html")

    def create_html(self):
        if not self.index.exists():
            if self.cla.exists():
                data = self.cla.read_text()
                self.index.write_text(data)

config_data = ClaConfig().load_config()
logger = Logger().get_logger()
html = Html().create_html()