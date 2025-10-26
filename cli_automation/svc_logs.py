# Application for reading service logs files
# By Ed Scrimaglia

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ".")))

class ReadLogs():
    def __init__(self, inst_dict: dict):
        self.verbose = inst_dict.get('verbose')
        self.logger = inst_dict.get('logger')

   
    def read_log_file(self, file_path: str = "cla.log") -> str:
        try:
            with open(file_path, 'r') as log_file:
                content = log_file.read()
                if self.verbose in [1,2]:
                    print (f"-> Successfully read log file '{file_path}'")
                self.logger.info(f"Successfully read log file '{file_path}'")
                return content
        except Exception as error:
            if self.verbose in [1,2]:
                print (f"** Error reading log file '{file_path}': '{error}'")
            self.logger.error(f"Error reading log file '{file_path}': '{error}'")
            return None