import logging
import platform
import shutil
from datetime import datetime, timezone
from pathlib import Path

import click

from binit.core.constants import ARCH_ALIASES, DEFAULT_BASE_DIR, VERSION
from binit.utils import ConfigManager, make_yaml_handler, os_arch_detect
from binit.logger import get_logger

logger = get_logger(__name__)


@click.command(name='init')
@click.option('--reinit', is_flag=True, default=False, help='Force re-initialisation from scratch')
@click.option('--base-dir', '-d', type=click.Path(), default=str(DEFAULT_BASE_DIR), help='Base directory for binit')
def init(reinit: bool, base_dir: str):
    '''Initialise binit directory structure'''
    root = logging.getLogger()
    for h in root.handlers[:]:
        if isinstance(h, logging.FileHandler):
            root.removeHandler(h)

    initialiser = Initialiser(reinit=reinit, base_dir=Path(base_dir).resolve())
    initialiser.run()


class Initialiser:
    '''Initialises .binit directory structure with bin and downloads subdirectories
    '''
    def __init__(self, base_dir: Path, reinit: bool = False):
        self.base_dir: Path = base_dir
        self.reinit: bool = reinit
        self.bin_dir: Path = self.base_dir / 'bin'
        self.log_dir: Path = self.base_dir / 'logs'
        self.downloads_dir: Path = self.base_dir / 'downloads'
        self.config_file: Path = self.base_dir / 'config.yaml'

        self.config_manager = ConfigManager(make_yaml_handler())


    def run(self):
        if self.reinit and self.base_dir.exists():
            logger.info(f'Reinitialising: deleting {self.base_dir} recusively')
            shutil.rmtree(self.base_dir)
        self.create_dirs()
        self.write_config()


    def create_dirs(self):
        for d in [self.base_dir, self.bin_dir, self.log_dir, self.downloads_dir]:
            if not d.exists() or self.reinit:
                d.mkdir(parents=True, exist_ok=True)
                logger.info(f'Created dir: {d}')
            else:
                logger.info(f'Dir already exists: {d}')


    def write_config(self):
        if self.config_file.exists() and not self.reinit:
            logger.info(f'Config already exists: {self.config_file}')
            return

        os_name, arch = os_arch_detect(
            platform.system().lower(),
            platform.machine().lower(),
            ARCH_ALIASES
        )

        config = {
            'binit_version': VERSION,
            'os': os_name,
            'arch': arch,
            'init_at': datetime.now(timezone.utc).astimezone().isoformat(),
            'base_dir': str(self.base_dir),
            'installed_tools': []
        }

        self.config_manager.write_config(config, self.config_file)
        logger.info(f'Config written: {self.config_file}')
