from dataclasses import dataclass
from pathlib import Path


@dataclass
class ToolModel:
    name: str
    repo: str
    asset: str
    release: str
    version: str
    homepage: str
    installed_at: str
    updated_at: str
    description: str
    license: str
    binary: Path


@dataclass
class ConfigModel:
    binit_version: str
    os: str
    arch: str
    init_at: str
    base_dir: Path
    installed_tools: dict[str, ToolModel]
