from binit.cli import cli
from binit.core.constants import DEFAULT_BASE_DIR
from binit.logger import setup_console_logging, setup_file_logging


def main():
    setup_console_logging()
    setup_file_logging(DEFAULT_BASE_DIR / 'logs')
    cli()
