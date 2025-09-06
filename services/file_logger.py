import logging
from pathlib import Path

class FileLoggerService:
    def __init__(self, log_file: str):
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.Logger("command_file_logger", level=logging.DEBUG)
        self.logger.propagate = False

        handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def info(self, message: str):
        self.logger.info(message)