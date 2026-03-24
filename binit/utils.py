from enum import Enum, auto
from pathlib import Path
from typing import IO, Any, Optional
from urllib.parse import urlparse

import filetype
from ruamel.yaml import YAML

from binit.core.exceptions import YamlError
from binit.core.protocols import YamlProtocol


class FileKind(Enum):
    TAR = auto()
    ZIP = auto()
    BINARY = auto()
    UNKNOWN = auto()


_TAR_MIMES = {
    'application/gzip',
    'application/x-bzip2',
    'application/x-xz',
    'application/x-tar'
}

_BINARY_MIMES = {
    'application/x-executable',   # ELF (Linux)
    'application/x-mach-binary',  # Mach-O (macOS)
    'application/x-msdownload',   # PE (.exe, Windows)
}


def identify_filetype(path: Path) -> FileKind:
    kind = filetype.guess(str(path))
    if kind is None:
        return FileKind.UNKNOWN
    if kind.mime in _TAR_MIMES:
        return FileKind.TAR
    if kind.mime == 'application/zip':
        return FileKind.ZIP
    if kind.mime in _BINARY_MIMES:
        return FileKind.BINARY
    return FileKind.UNKNOWN


def make_yaml_handler() -> 'YamlHandler':
    loader = YAML(typ='safe')
    writer = YAML()
    writer.default_flow_style = False
    writer.indent(mapping=2, sequence=4, offset=2)
    writer.width = 4096
    return YamlHandler(loader, writer)


class YamlHandler:
    def __init__(self, yaml_loader: YamlProtocol, yaml_writer: YamlProtocol):
        self.yaml_loader = yaml_loader
        self.yaml_writer = yaml_writer

    def load(self, stream: IO[str]) -> Optional[dict]:
        try:
            return self.yaml_loader.load(stream)
        except Exception as e:
            raise YamlError(f'Invalid YAML format in file: {stream}') from e

    def dump(self, data: Any, stream: IO[str]) -> None:
        try:
            self.yaml_writer.dump(data, stream)
        except Exception as e:
            raise YamlError(f'Error writing YAML to stream: {e}') from e


class ConfigManager:
    def __init__(self, yaml_handler: YamlHandler):
        self.yaml_handler = yaml_handler

    def config_exists(self, path: Path) -> bool:
        return path.exists()

    def load_config(self, path: Path) -> dict:
        if not self.config_exists(path):
            return {}
        with path.open(encoding='utf-8') as f:
            return self.yaml_handler.load(f) or {}

    def write_config(self, data: Any, path: Path) -> None:
        with path.open('w', encoding='utf-8') as f:
            self.yaml_handler.dump(data, f)


def os_arch_detect(os_name: str, arch: str, arch_aliases: dict[str, set[str]]) -> tuple[str, str]:
    if os_name.startswith('linux'):
        os_name = 'linux'

    canonical_arch = None
    for canon, aliases in arch_aliases.items():
        if arch in aliases:
            canonical_arch = canon
            break

    if not canonical_arch:
        canonical_arch = arch

    return os_name, canonical_arch


def parse_github_repo(value: str) -> tuple[str, str]:
    if value.startswith('http'):
        parts = urlparse(value).path.strip('/').split('/')
    else:
        parts = value.strip('/').split('/')

    if len(parts) < 2:
        raise ValueError(f'Invalid GitHub repo: {value!r}. Expected owner/repo or full URL.')

    return parts[0], parts[1]
