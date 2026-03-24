import logging
from pathlib import Path

import click

from binit.core.constants import DEFAULT_BASE_DIR
from binit.initialiser import Initialiser


@click.command(name='init')
@click.option('--reinit', is_flag=True, default=False, help='Force re-initialisation from scratch')
@click.option('--base-dir', '-d', type=click.Path(), default=str(DEFAULT_BASE_DIR), help='Base directory for binit')
def init(reinit: bool, base_dir: str):
    '''Initialise binit directory structure'''
    root = logging.getLogger()
    for h in root.handlers[:]:
        if isinstance(h, logging.FileHandler):
            root.removeHandler(h)

    Initialiser(base_dir=Path(base_dir).resolve(), reinit=reinit).run()
