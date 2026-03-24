from datetime import datetime, timezone
from pathlib import Path

import shutil

import click
import httpx
from ghapi.all import GhApi

from binit.core.config import load_config, write_config
from binit.core.constants import ARCH_ALIASES, DEFAULT_BASE_DIR
from binit.extractor import extract, find_executable
from binit.logger import get_logger
from binit.models import ToolModel
from binit.schema import ToolSchema
from binit.utils import parse_github_repo

logger = get_logger(__name__)


class Installer:
    '''Downloads and registers a binary from a GitHub release'''

    def __init__(self, github_repo: str):
        self.owner, self.repo = parse_github_repo(github_repo)
        self.api = GhApi()

    def run(self) -> ToolModel:
        config = load_config()

        os_name = config['os']
        arch = config['arch']
        arch_aliases = ARCH_ALIASES.get(arch, {arch})
        downloads_dir = Path(config['base_dir']) / 'downloads'
        bin_dir = Path(config['base_dir']) / 'bin'

        logger.info(f'Fetching latest release for {self.owner}/{self.repo}')
        release = self.api.repos.get_latest_release(owner=self.owner, repo=self.repo)
        repo_info = self.api.repos.get(owner=self.owner, repo=self.repo)

        asset = self._match_asset(release.assets, os_name, arch_aliases)
        if not asset:
            raise ValueError(f'No matching asset found for {os_name}/{arch}')

        logger.info(f'Matched asset: {asset.name}')
        asset_dir = downloads_dir / self.repo
        download_path = self._download(asset.browser_download_url, asset_dir, asset.name)
        extract(download_path)
        executable = find_executable(asset_dir)
        if not executable:
            raise ValueError(f'No executable found in extracted files for {self.repo}')
        bin_dir.mkdir(parents=True, exist_ok=True)
        binary_path = bin_dir / executable.name
        shutil.move(executable, binary_path)
        binary_path.chmod(0o755)
        logger.info(f'Moved binary to {binary_path}')

        version = release.tag_name.lstrip('v')
        license_name = repo_info.license.name if repo_info.get('license') else None

        updated_at = datetime.fromisoformat(release.published_at.replace('Z', '+00:00'))

        tool_model = ToolModel(
            name=self.repo,
            repo=f'https://github.com/{self.owner}/{self.repo}',
            asset=asset.name,
            release=release.tag_name,
            version=version,
            homepage=repo_info.get('homepage') or f'https://github.com/{self.owner}/{self.repo}',
            installed_at=datetime.now(timezone.utc).astimezone(),
            updated_at=updated_at,
            description=repo_info.get('description'),
            license=license_name,
            binary=binary_path
        )

        tool_dict = ToolSchema().dump(tool_model)
        config.setdefault('installed_tools', {})[self.repo] = tool_dict
        write_config(config, DEFAULT_BASE_DIR / 'config.yaml')
        logger.info(f'Installed {self.repo} v{version} → {binary_path}')

        return tool_model

    _PREFERRED_EXTENSIONS = ('.tar.gz', '.tgz', '.tar.bz2', '.tar.xz', '.zip')

    def _match_asset(self, assets, os_name: str, arch_aliases: set) -> object | None:
        candidates = [
            asset for asset in assets
            if os_name in asset.name.lower()
            and any(alias in asset.name.lower() for alias in arch_aliases)
        ]
        for ext in self._PREFERRED_EXTENSIONS:
            for asset in candidates:
                if asset.name.lower().endswith(ext):
                    return asset
        return None

    def _download(self, url: str, downloads_dir: Path, filename: str) -> Path:
        downloads_dir.mkdir(parents=True, exist_ok=True)
        dest = downloads_dir / filename
        if dest.exists():
            if not click.confirm(f'{filename} already exists. Re-download?', default=False):
                logger.info(f'Skipped download, using existing file: {dest}')
                return dest
        with httpx.stream('GET', url, follow_redirects=True) as response:
            response.raise_for_status()
            with dest.open('wb') as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
        logger.info(f'Downloaded to {dest}')
        return dest
