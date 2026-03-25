from pathlib import Path
from typing import Any

from binit.core.constants import DEFAULT_BASE_DIR
from binit.utils import ConfigManager, make_yaml_handler


def load_config() -> dict:
    config_file = DEFAULT_BASE_DIR / 'config.yaml'

    if not config_file.exists():
        raise FileNotFoundError('Config not found. Run `binit init` first.')

    config = ConfigManager(make_yaml_handler()).load_config(config_file)
    if not isinstance(config.get('installed_tools'), dict):
        config['installed_tools'] = {}
    return config


def write_config(data: Any, path: Path) -> None:
    ConfigManager(make_yaml_handler()).write_config(data, path)
