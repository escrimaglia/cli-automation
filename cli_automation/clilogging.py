import logging
import logging.handlers

# class CliLogging:
#     def __init__(self, logging_level: str):
#         self.logging = logging_level
    
#     def set_logging(self):
#         logger = logging.getLogger("cla")
#         if self.logging is not None:
#             logging.basicConfig(filename='cla.log', level=getattr(logging, self.logging.upper(), None))
#             logger.info(f"CLA log entry created at {dt.now()}")
        
#         return logger
    
class Logger:
    def __init__(self, log_file: str = "app.log", level: str = "INFO"):
        self.level = level
        self.log_file = log_file
        self.logger = logging.getLogger("ClaLogger")
        self.logger.setLevel(getattr(logging, self.level.upper(), logging.INFO))
        

    def set_logger(self):
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        file_handler = logging.handlers.RotatingFileHandler(self.log_file, maxBytes=5*1024*1024, backupCount=5)
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        return self.logger

    