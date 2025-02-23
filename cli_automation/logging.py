import logging
import logging.handlers


# class Logger:
#     def __init__(self, log_file: str = "cla.log", level: str = "INFO"):
#         self.level = level
#         self.log_file = log_file
#         self.logger = logging.getLogger("ClaLogger")
#         self.logger.setLevel(getattr(logging, self.level.upper(), logging.INFO))
        

#     def set_logger(self):
#         log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#         file_handler = logging.handlers.RotatingFileHandler(self.log_file, maxBytes=5*1024*1024, backupCount=5)
#         file_handler.setFormatter(log_format)
#         file_handler.setLevel(getattr(logging, self.level.upper(), logging.INFO))
#         # console_handler = logging.StreamHandler()
#         # console_handler.setFormatter(log_format)
#         # console_handler.setLevel(getattr(logging, self.level.upper(), logging.INFO))
        
#         self.logger.addHandler(file_handler)
#         #self.logger.addHandler(console_handler)

#         return self.logger
    
class Logger:
    def __init__(self, log_file: str = "cla.log", level: str = "INFO"):
        self.level = level
        self.log_file = log_file
        self.logger = logging.getLogger("ClaLogger")
        self._set_log_level()  # Centralizamos la configuración del nivel de log

        # Evitar duplicados si ya existe un handler
        if not self.logger.hasHandlers():
            self.set_logger()

    def _set_log_level(self):
        """Configura el nivel de log del logger de manera centralizada."""
        log_level = getattr(logging, self.level.upper(), logging.INFO)
        self.logger.setLevel(log_level)

    def set_logger(self):
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Manejador de archivo
        file_handler = logging.handlers.RotatingFileHandler(self.log_file, maxBytes=5*1024*1024, backupCount=5)
        file_handler.setFormatter(log_format)
        file_handler.setLevel(self.logger.level)

        self.logger.addHandler(file_handler)

        # Si quieres agregar consola, descomenta el siguiente bloque
        # console_handler = logging.StreamHandler()
        # console_handler.setFormatter(log_format)
        # console_handler.setLevel(self.logger.level)
        # self.logger.addHandler(console_handler)

        return self.logger
    