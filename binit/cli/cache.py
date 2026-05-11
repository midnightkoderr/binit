import shutil
from pathlib import Path

import click

from binit.cli._command import Command
from binit.core.config import load_config


@click.command(name='cache', cls=Command)
@click.option('--clean', '-c', is_flag=True, help='Delete all cached downloaded archives')
@click.option('--logs', '-l', is_flag=True, help='Delete all log files')
def cache(clean: bool, logs: bool):
    '''Manage binit cache and logs'''
    if not clean and not logs:
        raise click.UsageError('Provide at least one option. See --help.')

    try:
        cfg = load_config()
    except FileNotFoundError as e:
        raise click.ClickException(str(e))

    base_dir = cfg.get('base_dir', '')
    if not base_dir:
        raise click.ClickException('base_dir not set in config.')

    if clean:
        downloads_dir = Path(base_dir) / 'downloads'
        if not downloads_dir.exists():
            click.echo('Downloads cache is already empty.')
        else:
            shutil.rmtree(downloads_dir)
            downloads_dir.mkdir(parents=True, exist_ok=True)
            click.echo(f'Cleared {downloads_dir}.')

    if logs:
        logs_dir = Path(base_dir) / 'logs'
        if not logs_dir.exists():
            click.echo('Logs directory is already empty.')
        else:
            shutil.rmtree(logs_dir)
            logs_dir.mkdir(parents=True, exist_ok=True)
            click.echo(f'Cleared {logs_dir}.')
