# Configuration

binit stores all state in a single YAML file at `~/.binit/config.yaml`. It is created automatically by `binit init` and updated after each install or uninstall.

## File location

```
~/.binit/config.yaml
```

The base directory can be inspected (but not changed) via `binit config --print`.

## Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `binit_version` | string | Version of binit that initialised this config |
| `os` | string | Host operating system (`linux`) |
| `arch` | string | Canonical CPU architecture (see [Architectures](#architectures)) |
| `init_at` | ISO 8601 datetime | When `binit init` was first run |
| `base_dir` | string | Absolute path to the binit directory (default `~/.binit`) |
| `installed_tools` | map | Dictionary of installed tool entries, keyed by tool name |

## Tool entry fields

Each key under `installed_tools` maps to an object with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Tool name (matches the key in `installed_tools`) |
| `repo` | URL | Yes | Full GitHub repository URL |
| `asset` | string | Yes | Filename of the release asset that was downloaded |
| `release` | string | Yes | GitHub release tag (e.g. `v8.30.1`) |
| `version` | string | Yes | Numeric version extracted from the tag (e.g. `8.30.1`) |
| `binary` | string | Yes | Absolute path to the installed binary |
| `updated_at` | ISO 8601 datetime | Yes | When the GitHub release was published |
| `installed_at` | ISO 8601 datetime | No | When the tool was installed by binit |
| `homepage` | URL | No | Project homepage (falls back to repo URL) |
| `description` | string | No | GitHub repo description |
| `license` | string | No | License name from GitHub (e.g. `MIT License`) |
| `rename_to` | string | No | Custom binary name if the original was renamed during install |

## Example

```yaml
binit_version: 0.1.0
os: linux
arch: amd64
init_at: '2026-03-24T11:00:00+05:30'
base_dir: /home/user/.binit
installed_tools:
  gitleaks:
    name: gitleaks
    repo: https://github.com/gitleaks/gitleaks
    asset: gitleaks_8.30.1_linux_x64.tar.gz
    release: v8.30.1
    version: 8.30.1
    homepage: https://gitleaks.io
    updated_at: '2026-03-21T02:17:58+00:00'
    installed_at: '2026-03-24T16:49:52.016934+05:30'
    description: Find secrets with Gitleaks 🔑
    license: MIT License
    binary: /home/user/.binit/bin/gitleaks
  bao:
    name: bao
    repo: https://github.com/openbao/openbao
    asset: bao_2.5.3_linux_amd64.tar.gz
    release: v2.5.3
    version: 2.5.3
    homepage: https://openbao.org
    updated_at: '2026-04-10T14:00:00+00:00'
    installed_at: '2026-04-12T09:20:00+05:30'
    description: OpenBao — open source Vault fork
    license: Mozilla Public License 2.0
    binary: /home/user/.binit/bin/bao
    rename_to: bao
```

## Architectures

binit detects the CPU architecture at init time and normalises it to one of the canonical names below. The alias set is what binit matches against in release asset filenames.

| Canonical name | Aliases matched in asset names |
|----------------|-------------------------------|
| `amd64` | `amd64`, `x86_64`, `x64`, `x86-64`, `64bit`, `64-bit` |
| `386` | `386`, `i386`, `i686`, `x86`, `32bit`, `32-bit` |
| `arm64` | `arm64`, `aarch64`, `armv8` |
| `armv7` | `armv7`, `armhf` |
| `armv6` | `armv6` |
| `ppc64le` | `ppc64le` |
| `s390x` | `s390x` |

## Supported platforms

| OS | Value in config |
|----|----------------|
| Linux | `linux` |

## Validation

Run `binit config --check` to validate the config file against the schema. Errors are printed to stderr with the field name and message.

The version field inside each tool entry must be a numeric dot-separated string (e.g. `1.2.3`, `5.8.1`). GitHub tags with namespaced prefixes like `kustomize/v5.8.1` are automatically stripped to `5.8.1` during install.

## Manual edits

The config file is plain YAML and can be edited by hand. After editing, run `binit config --check` to verify the result is valid.

> **Warning:** Removing a tool entry from `installed_tools` does not delete the binary from `~/.binit/bin/`. Delete the binary manually or use `binit tool uninstall` instead.
