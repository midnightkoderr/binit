# API Reference

Internal Python module reference for binit. Useful if you are extending binit or importing its components into your own scripts.

## `binit.installer` — `Installer`

Core class that orchestrates downloading and installing a binary from a GitHub release.

```python
from binit.installer import Installer
```

### `Installer(github_repo, rename_to=None, name=None)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `github_repo` | `str` | GitHub repo as `owner/repo` or full URL |
| `rename_to` | `str \| None` | Rename the installed binary to this name |
| `name` | `str \| None` | Binary name to prefer when a repo ships multiple executables |

### `Installer.run() -> ToolModel | None`

Executes the full install pipeline:

1. Loads config, resolves OS and architecture
2. Fetches the latest release from the GitHub API
3. Matches the best release asset via `_match_asset`
4. Downloads the asset to `~/.binit/downloads/<tool>/`
5. Extracts the archive and locates the executable
6. Moves the binary to `~/.binit/bin/` with `chmod 755`
7. Writes updated config

Returns the `ToolModel` on success, or `None` if the installed release is already current.

### `Installer._score_asset(asset, os_name, arch_aliases) -> int`

Scores a single release asset for the current platform. Returns a negative number for disqualified assets.

| Condition | Effect |
|-----------|--------|
| `--name` given and filename does not start with `<name>_` or `<name>-<digit>` | Returns `−100` |
| Filename contains the OS name | `+4` |
| Filename contains an arch alias | `+3` |
| Filename is an archive format | `+2` |
| Filename starts with repo name (no `--name`) | `+2` |
| Filename has no extension | `+1` |
| Filename is a checksum or signature | `−10` |

Minimum score to be considered: **6** (`_MIN_SCORE`).

### `Installer._match_asset(assets, os_name, arch_aliases) -> object | None`

Selects the highest-scoring asset that meets the minimum threshold. Returns `None` if no asset qualifies.

### `Installer._download(url, downloads_dir, filename) -> Path`

Downloads the asset via HTTP streaming. Prompts to skip if the file already exists locally.

---

## `binit.extractor` — extraction helpers

```python
from binit.extractor import extract, find_executable
```

### `extract(archive, _depth=0, _max_depth=3) -> Path`

Extracts an archive file in-place (into the same directory as the archive). Handles nested archives recursively up to `_max_depth` levels.

Supported formats (detected by MIME type, not file extension):

- `tar.gz`, `tgz`
- `tar.bz2`
- `tar.xz`
- `zip`

If the file is detected as a binary (ELF), extraction is skipped and the file is returned as-is.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `archive` | `Path` | — | Path to the archive file |
| `_depth` | `int` | `0` | Current recursion depth (internal) |
| `_max_depth` | `int` | `3` | Maximum recursion depth |

Returns the path to the directory containing the extracted files.

### `find_executable(directory, preferred_name=None) -> Path | None`

Recursively searches `directory` for files with ELF magic bytes. If `preferred_name` is given, that file is returned first if found. Otherwise returns the first executable found.

Returns `None` if no executable is found.

---

## `binit.initialiser` — `Initialiser`

Creates the binit directory structure and writes the initial config.

```python
from binit.initialiser import Initialiser
```

### `Initialiser(base_dir=DEFAULT_BASE_DIR, reinit=False)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_dir` | `Path` | `~/.binit` | Root directory for binit files |
| `reinit` | `bool` | `False` | If `True`, delete the existing directory before creating |

### `Initialiser.run()`

Runs the full initialisation sequence: optionally removes the existing directory, creates subdirectories, writes `config.yaml`, and prints the PATH hint.

### `Initialiser.create_dirs()`

Creates `base_dir`, `bin/`, `logs/`, and `downloads/` if they do not already exist.

---

## `binit.models` — data models

```python
from binit.models import ToolModel, ConfigModel
```

### `ToolModel`

Dataclass representing an installed tool entry.

| Field | Type |
|-------|------|
| `name` | `str` |
| `repo` | `str` |
| `asset` | `str` |
| `release` | `str` |
| `version` | `str` |
| `homepage` | `str \| None` |
| `installed_at` | `datetime \| None` |
| `updated_at` | `datetime` |
| `description` | `str \| None` |
| `license` | `str \| None` |
| `binary` | `Path` |
| `rename_to` | `str \| None` |

### `ConfigModel`

Dataclass representing the top-level config file.

| Field | Type |
|-------|------|
| `binit_version` | `str` |
| `os` | `str` |
| `arch` | `str` |
| `init_at` | `str` |
| `installed_tools` | `dict[str, ToolModel]` |

---

## `binit.schema` — marshmallow schemas

```python
from binit.schema import ToolSchema, ConfigSchema
```

### `ToolSchema`

Validates and deserialises tool config entries. Unknown fields are preserved (`INCLUDE`). The `rename_to` field is dropped from serialised output when `None`.

Key validations:

- `repo` and `homepage` must be valid URLs
- `version` must match `^\d+(\.\d+)+` (numeric dot-separated, e.g. `1.2.3`)
- `updated_at` and `installed_at` are `DateTime` fields

`@post_load` returns a `ToolModel` instance.

### `ConfigSchema`

Validates the top-level config structure. Unknown fields are preserved.

Key validations:

- `os` must be one of `SUPPORTED_PLATFORMS`
- `arch` must be a key in `ARCH_ALIASES`
- `installed_tools` values are nested `ToolSchema`

`@post_load` returns a `ConfigModel` instance.

---

## `binit.utils` — utilities

```python
from binit.utils import parse_github_repo, os_arch_detect, identify_filetype, FileKind
```

### `parse_github_repo(repo_ref) -> tuple[str, str]`

Parses a GitHub repo reference and returns `(owner, repo)`.

Accepts:

- `owner/repo`
- `https://github.com/owner/repo`
- `https://github.com/owner/repo.git`

Raises `ValueError` if the format is not recognised.

### `os_arch_detect(os_name, machine, arch_aliases) -> tuple[str, str]`

Normalises raw `platform.system()` and `platform.machine()` values to canonical binit names.

Returns `(os_name, canonical_arch)`. Raises `ValueError` if the architecture is not in `arch_aliases`.

### `identify_filetype(path) -> FileKind`

Detects the file type of `path` using MIME magic bytes.

### `FileKind`

Enum of file kinds used by the extractor.

| Member | Description |
|--------|-------------|
| `FileKind.BINARY` | ELF executable |
| `FileKind.TAR` | tar archive (any compression) |
| `FileKind.ZIP` | zip archive |
| `FileKind.UNKNOWN` | unrecognised or unsupported |

---

## `binit.core.config` — config I/O

```python
from binit.core.config import load_config, write_config
```

### `load_config() -> dict`

Reads and returns `~/.binit/config.yaml` as a plain dictionary. Raises `FileNotFoundError` if the file does not exist.

### `write_config(config, path)`

Writes `config` (a plain dict) to `path` as YAML, preserving comments where possible (uses `ruamel.yaml`).

---

## `binit.logger` — logging

```python
from binit.logger import get_logger
```

### `get_logger(name) -> logging.Logger`

Returns a logger that writes to both:

- **stderr** at INFO level
- **`~/.binit/logs/binit_<YYYY-MM-DD>.log`** at DEBUG level

All binit modules call `get_logger(__name__)` for consistent log context.

---

## `binit.core.constants`

```python
from binit.core.constants import SUPPORTED_PLATFORMS, ARCH_ALIASES, DEFAULT_BASE_DIR
```

| Name | Value |
|------|-------|
| `SUPPORTED_PLATFORMS` | `{'linux'}` |
| `ARCH_ALIASES` | Dict mapping canonical arch names to sets of alias strings |
| `DEFAULT_BASE_DIR` | `Path.home() / '.binit'` |
