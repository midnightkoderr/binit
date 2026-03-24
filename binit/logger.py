import logging
import sys
from datetime import date
from pathlib import Path


def setup_console_logging(level: str = 'INFO'):
    logging.basicConfig(
        level=level,
        format='[%(levelname)s] %(name)s: %(message)s',
        stream=sys.stderr
    )


def setup_file_logging(log_dir: Path, level: str = 'INFO'):
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'binit_{date.today()}.log'
    handler = logging.FileHandler(log_file, encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logging.getLogger().addHandler(handler)


def get_logger(name: str = '') -> logging.Logger:
    return logging.getLogger(name)
