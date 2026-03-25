from datetime import datetime, timezone
from pathlib import Path
import warnings

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

    def __init__(self, github_repo: str, rename_to: str | None = None, name: str | None = None):
        self.owner, self.repo = parse_github_repo(github_repo)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            self.api = GhApi()

        self._rename_to = rename_to
        self._name = name

    def run(self) -> ToolModel | None:
        config = load_config()

        os_name = config['os']
        arch = config['arch']
        arch_aliases = ARCH_ALIASES.get(arch, {arch})
        downloads_dir = Path(config['base_dir']) / 'downloads'
        bin_dir = Path(config['base_dir']) / 'bin'

        tool_key = self._name or self.repo
        existing_tool = config.get('installed_tools', {}).get(tool_key)
        if self._rename_to is None and existing_tool and existing_tool.get('rename_to'):
            self._rename_to = existing_tool['rename_to']

        logger.info(f'Fetching latest release for {self.owner}/{self.repo}')
        release = self.api.repos.get_latest_release(owner=self.owner, repo=self.repo)
        repo_info = self.api.repos.get(owner=self.owner, repo=self.repo)

        if existing_tool and existing_tool.get('release') == release.tag_name:
            logger.info(f'{tool_key} {release.tag_name} is already installed, skipping.')
            return None

        asset = self._match_asset(release.assets, os_name, arch_aliases)
        if not asset:
            raise ValueError(f'No matching asset found for {os_name}/{arch}')

        logger.info(f'Matched asset: {asset.name}')
        lookup_name = (self._name or self.repo).lower()
        if lookup_name not in asset.name.lower():
            if not click.confirm(
                f'Asset "{asset.name}" doesn\'t match "{self._name or self.repo}". Install anyway?',
                default=False,
            ):
                raise click.Abort()
        asset_dir = downloads_dir / tool_key
        download_path = self._download(asset.browser_download_url, asset_dir, asset.name)
        extract(download_path)
        executable = find_executable(asset_dir, preferred_name=self._name)
        if not executable:
            raise ValueError(f'No executable found in extracted files for {tool_key}')
        original_name = executable.name
        if self._rename_to is not None:
            rename_to = self._rename_to
        elif self._name and original_name != self._name:
            # --name was given and binary doesn't already match — rename automatically
            rename_to = self._name
        elif original_name != self.repo and ('-' in original_name or '_' in original_name):
            rename_to = click.prompt(
                f'Rename binary "{original_name}"? (leave blank to keep as-is)',
                default='',
                show_default=False,
            ).strip() or None
        else:
            rename_to = None

        bin_dir.mkdir(parents=True, exist_ok=True)
        final_name = rename_to if rename_to else original_name
        binary_path = bin_dir / final_name
        shutil.move(executable, binary_path)
        binary_path.chmod(0o755)
        logger.info(f'Moved binary to {binary_path}')

        version = release.tag_name.lstrip('v')
        license_name = repo_info.license.name if repo_info.get('license') else None

        updated_at = datetime.fromisoformat(release.published_at.replace('Z', '+00:00'))

        tool_model = ToolModel(
            name=tool_key,
            repo=f'https://github.com/{self.owner}/{self.repo}',
            asset=asset.name,
            release=release.tag_name,
            version=version,
            homepage=repo_info.get('homepage') or f'https://github.com/{self.owner}/{self.repo}',
            installed_at=datetime.now(timezone.utc).astimezone(),
            updated_at=updated_at,
            description=repo_info.get('description'),
            license=license_name,
            binary=binary_path,
            rename_to=rename_to,
        )

        tool_dict = ToolSchema().dump(tool_model)
        config.setdefault('installed_tools', {})[tool_key] = tool_dict
        write_config(config, DEFAULT_BASE_DIR / 'config.yaml')
        logger.info(f'Installed {tool_key} v{version} → {binary_path}')

        return tool_model

    _ARCHIVE_EXTENSIONS = ('.tar.gz', '.tgz', '.tar.bz2', '.tar.xz', '.zip')
    _CHECKSUM_EXTENSIONS = ('.sha256', '.sha512', '.md5', '.sha1', '.sig', '.asc', '.pem', '.sbom', '.txt')
    _MIN_SCORE = 6

    def _score_asset(self, asset, os_name: str, arch_aliases: set) -> int:
        name = asset.name.lower()
        score = 0
        if self._name:
            if self._name.lower() not in name:
                return -100
        else:
            if self.repo.lower() in name:
                score += 2
        if os_name in name:
            score += 4
        if any(alias in name for alias in arch_aliases):
            score += 3
        if any(name.endswith(ext) for ext in self._ARCHIVE_EXTENSIONS):
            score += 2
        if not Path(asset.name).suffix:
            score += 1
        if any(name.endswith(ext) for ext in self._CHECKSUM_EXTENSIONS):
            score -= 10
        return score

    def _match_asset(self, assets, os_name: str, arch_aliases: set) -> object | None:
        scored = [
            (asset, self._score_asset(asset, os_name, arch_aliases))
            for asset in assets
        ]
        candidates = [(asset, score) for asset, score in scored if score >= self._MIN_SCORE]
        if not candidates:
            return None
        return max(candidates, key=lambda x: x[1])[0]

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
