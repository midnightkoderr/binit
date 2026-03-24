import logging
import sys


def setup_console_logging(level: str = 'INFO'):
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stderr
    )


def get_logger(name: str = '') -> logging.Logger:
    return logging.getLogger(name)
