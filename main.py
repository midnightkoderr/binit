from binit.cli import cli
from binit.logger import setup_console_logging


def main():
    setup_console_logging()
    cli()


if __name__ == '__main__':
    main()
