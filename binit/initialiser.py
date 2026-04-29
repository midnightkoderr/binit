import platform
import shutil
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import click

from binit.core.config import write_config
from binit.core.constants import ARCH_ALIASES, DEFAULT_BASE_DIR
from binit.logger import get_logger
from binit.utils import os_arch_detect

logger = get_logger(__name__)


class Initialiser:
    '''Initialises binit directory structure with bin, logs, and downloads subdirectories'''

    def __init__(self, base_dir: Path = DEFAULT_BASE_DIR, reinit: bool = False):
        self.base_dir = base_dir
        self.reinit = reinit
        self.config_dir = base_dir
        self.config_file = base_dir / 'config.yaml'
        self.bin_dir = base_dir / 'bin'
        self.log_dir = base_dir / 'logs'
        self.downloads_dir = base_dir / 'downloads'


    def run(self):
        if self.reinit and self.base_dir.exists():
            logger.info(f'Reinitialising: deleting {self.base_dir} recursively')
            shutil.rmtree(self.base_dir)
        self.create_dirs()
        self._write_config()
        self._print_path_hint()


    def _print_path_hint(self):
        bin_dir = self.bin_dir
        click.echo('')
        click.echo(click.style('  binit initialised successfully!', fg='green', bold=True))
        click.echo('')
        click.echo('  Add the bin directory to your PATH:')
        click.echo('')
        click.echo(click.style(f'    export PATH="{bin_dir}:$PATH"', fg='cyan'))
        click.echo('')
        click.echo('  To persist it, add the line above to your shell config (~/.bashrc, ~/.zshrc, etc.)')
        click.echo('')


    def create_dirs(self):
        for d in [self.config_dir, self.base_dir, self.bin_dir, self.log_dir, self.downloads_dir]:
            if not d.exists():
                d.mkdir(parents=True, exist_ok=True)
                logger.info(f'Created dir: {d}')
            else:
                logger.info(f'Dir already exists: {d}')


    def _write_config(self):
        if self.config_file.exists() and not self.reinit:
            logger.info(f'Config already exists: {self.config_file}')
            return

        os_name, arch = os_arch_detect(platform.system().lower(), platform.machine().lower(), ARCH_ALIASES)

        config = {
            'binit_version': version('binit'),
            'os': os_name,
            'arch': arch,
            'init_at': datetime.now(timezone.utc).astimezone().isoformat(),
            'base_dir': str(self.base_dir),
            'installed_tools': {}
        }

        write_config(config, self.config_file)
        logger.info(f'Config written: {self.config_file}')
