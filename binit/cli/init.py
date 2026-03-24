import logging
import click

from binit.initialiser import Initialiser


@click.command(name='init')
@click.option('--reinit', is_flag=True, default=False, help='Force re-initialisation from scratch')
def init(reinit: bool):
    '''Initialise binit directory structure'''
    root = logging.getLogger()
    for h in root.handlers[:]:
        if isinstance(h, logging.FileHandler):
            root.removeHandler(h)

    Initialiser(reinit=reinit).run()
