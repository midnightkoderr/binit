import click

from binit.cli import init
from binit.core.constants import VERSION


@click.group()
@click.version_option(version=VERSION, prog_name='binit')
def cli():
    '''binit - minimal binary installer'''
    pass


cli.add_command(init.init)
