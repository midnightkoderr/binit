import click
from importlib.metadata import version

from binit.cli import config, init, tool


@click.group(invoke_without_command=True)
@click.version_option(version=version('binit'), prog_name='binit')
@click.pass_context
def cli(ctx: click.Context):
    '''binit - minimal binary installer'''
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


cli.add_command(init.init)
cli.add_command(config.config)
cli.add_command(tool.tool)
