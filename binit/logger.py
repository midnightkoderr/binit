import logging
import logging.config
import sys
from pathlib import Path
from typing import Mapping, Optional


def setup_logging(config: dict):
    logging.config.dictConfig(config)


def setup_console_logging(level: str = 'INFO'):
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stderr
    )


def get_logger(name: str = '') -> logging.Logger:
    return logging.getLogger(name)


class LoggingConfig:
    def __init__(self, log_file: Path, formatters: Optional[Mapping[str, dict]] = None, log_level: str = 'INFO', file_level: str = 'DEBUG', mode: str = 'a', rotate: bool = False, when: str = 'midnight', backup_count: int = 7):
        self.log_file = log_file
        self.log_level = log_level
        self.file_level = file_level
        self.mode = mode
        self.rotate = rotate
        self.when = when
        self.backup_count = backup_count
        self.formatters = formatters or {
            'default': {
                'format': '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
        }


    def get_config(self) -> dict:
        handlers = {
            'stderr': {
                'class': 'logging.StreamHandler',
                'level': self.log_level,
                'formatter': 'default',
                'stream': 'ext://sys.stderr',
            }
        }

        file_handler: dict = {
            'level': self.file_level,
            'formatter': 'default',
            'filename': str(self.log_file),
            'encoding': 'utf-8',
        }

        if self.rotate:
            file_handler.update({
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'when': self.when,
                'backupCount': self.backup_count,
            })
        else:
            file_handler.update({
                'class': 'logging.FileHandler',
                'mode': self.mode,
            })

        handlers['file'] = file_handler

        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': self.formatters,
            'handlers': handlers,
            'root': {'level': 'DEBUG', 'handlers': list(handlers.keys())},
        }
