from pathlib import Path
import warnings

import click
from ghapi.all import GhApi
from rich.console import Console
from rich.table import Table

from binit.core.config import load_config, write_config
from binit.core.constants import DEFAULT_BASE_DIR
from binit.installer import Installer
from binit.utils import parse_github_repo

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
@click.option('--list-installed', is_flag=True, is_eager=True, expose_value=False, callback=_list_installed_callback, help='List all installed tools')
def tool():
    '''Manage installed tools'''


@tool.command(name='install')
@click.option('--github-repo', '-r', required=True, help='GitHub repo as owner/repo or full URL')
@click.option('--name', '-n', default=None, help='Name of the binary to install (for repos with multiple binaries)')
def install(github_repo: str, name: str):
    '''Install a binary from the latest GitHub release'''
    try:
        Installer(github_repo, name=name).run()
    except ValueError as e:
        raise click.BadParameter(str(e), param_hint='--github-repo')


def _update_tool(name: str, tool_cfg: dict):
    installed_release = tool_cfg.get('release')
    repo_url = tool_cfg.get('repo')

    owner, repo = parse_github_repo(repo_url)

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        api = GhApi()

    latest = api.repos.get_latest_release(owner=owner, repo=repo)
    latest_release = latest.tag_name

    if latest_release == installed_release:
        click.echo(f'{name} is already up to date ({installed_release}).')
        return

    click.echo(f'Updating {name}: {installed_release} → {latest_release}')
    Installer(repo_url, rename_to=tool_cfg.get('rename_to')).run()


@tool.command(name='update')
@click.option('--name', '-n', default=None, help='Name of the installed tool to update')
@click.option('--all', '-a', 'update_all', is_flag=True, default=False, help='Update all installed tools')
def update(name: str, update_all: bool):
    '''Check for and apply updates to an installed tool'''
    if not name and not update_all:
        raise click.UsageError('Provide --name or --all.')

    try:
        cfg = load_config()
    except FileNotFoundError as e:
        raise click.ClickException(str(e))

    tools = cfg.get('installed_tools', {})

    if update_all:
        if not tools:
            click.echo('No tools installed.')
            return

        for tool_name, tool_cfg in tools.items():
            try:
                _update_tool(tool_name, tool_cfg)
            except ValueError as e:
                raise click.ClickException(str(e))
        return

    if name not in tools:
        raise click.ClickException(f'Tool "{name}" is not installed.')

    try:
        _update_tool(name, tools[name])
    except ValueError as e:
        raise click.ClickException(str(e))


@tool.command(name='uninstall')
@click.option('--name', '-n', required=True, help='Name of the installed tool to uninstall')
def uninstall(name: str):
    '''Uninstall an installed tool and remove its binary'''
    try:
        cfg = load_config()
    except FileNotFoundError as e:
        raise click.ClickException(str(e))

    tools = cfg.get('installed_tools', {})
    if name not in tools:
        raise click.ClickException(f'Tool "{name}" is not installed.')

    binary = tools[name].get('binary')
    if binary and (p := Path(binary)).exists():
        p.unlink()

    del tools[name]
    write_config(cfg, DEFAULT_BASE_DIR / 'config.yaml')
    click.echo(f'Uninstalled {name}.')
