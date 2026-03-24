import click
from rich.console import Console
from rich.table import Table

from binit.core.config import load_config
from binit.installer import Installer

console = Console()


def _list_installed_callback(ctx: click.Context, _, value):
    if not value or ctx.resilient_parsing:
        return
    try:
        cfg = load_config()
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    tools = cfg.get('installed_tools', {})
    if not tools:
        click.echo('No tools installed.')
    else:
        table = Table(show_header=True, header_style='bold cyan')
        table.add_column('Tool', style='bold')
        table.add_column('Version')
        table.add_column('Release')
        table.add_column('Binary')
        for name, t in tools.items():
            table.add_row(name, t.get('version', '-'), t.get('release', '-'), t.get('binary', '-'))
        console.print(table)
    ctx.exit()


@click.group(name='tool')
@click.option('--list-installed', is_flag=True, is_eager=True, expose_value=False,
               callback=_list_installed_callback, help='List all installed tools')
def tool():
    '''Manage installed tools'''


@tool.command(name='install')
@click.option('--github-repo', '-r', required=True, help='GitHub repo as owner/repo or full URL')
def install(github_repo: str):
    '''Install a binary from the latest GitHub release'''
    try:
        Installer(github_repo).run()
    except ValueError as e:
        raise click.BadParameter(str(e), param_hint='--github-repo')
