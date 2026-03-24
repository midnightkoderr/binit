from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class ToolModel:
    name: str
    repo: str
    asset: str
    release: str
    version: str
    homepage: Optional[str]
    installed_at: Optional[datetime]
    updated_at: datetime
    description: Optional[str]
    license: Optional[str]
    binary: Path


@dataclass
class ConfigModel:
    binit_version: str
    os: str
    arch: str
    init_at: str
    installed_tools: dict[str, ToolModel]
