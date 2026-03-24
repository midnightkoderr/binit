import tarfile
import zipfile
from pathlib import Path

from binit.logger import get_logger
from binit.utils import FileKind, identify_filetype

logger = get_logger(__name__)


def extract(archive: Path, _depth: int = 0, _max_depth: int = 3) -> Path:
    if _depth >= _max_depth:
        logger.info(f'Max extraction depth ({_max_depth}) reached, stopping at {archive.name}')
        return archive

    kind = identify_filetype(archive)
    dest = archive.parent

    if kind == FileKind.BINARY:
        logger.info(f'{archive.name} is a binary, no extraction needed')
        return archive
    elif kind == FileKind.TAR:
        extracted = _extract_tar(archive, dest)
    elif kind == FileKind.ZIP:
        extracted = _extract_zip(archive, dest)
    else:
        logger.info(f'Unknown or unsupported file type for {archive.name}, skipping extraction')
        return archive

    for nested in extracted.iterdir():
        if nested == archive:
            continue
        if nested.is_file() and identify_filetype(nested) in (FileKind.TAR, FileKind.ZIP):
            extract(nested, _depth=_depth + 1, _max_depth=_max_depth)

    return extracted


def find_executable(directory: Path) -> Path | None:
    for f in directory.rglob('*'):
        if f.is_file() and identify_filetype(f) == FileKind.BINARY:
            logger.info(f'Found executable: {f}')
            return f
    logger.info(f'No executable found in {directory}')
    return None


def _extract_tar(archive: Path, dest: Path) -> Path:
    with tarfile.open(archive, 'r:*') as tar:
        tar.extractall(dest, filter='data')
    logger.info(f'Extracted {archive.name} to {dest}')
    return dest


def _extract_zip(archive: Path, dest: Path) -> Path:
    with zipfile.ZipFile(archive, 'r') as zf:
        zf.extractall(dest)
    logger.info(f'Extracted {archive.name} to {dest}')
    return dest
