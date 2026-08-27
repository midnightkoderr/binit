# binit

A minimal GitHub release binary installer and manager.

## Installation

```bash
uv tool install git+https://github.com/midnightkoderr/binit
```

Or use local clone of the repo and install with uv:

```bash
git clone https://github.com/midnightkoderr/binit
cd binit
uv tool install -e .
```

## Setup

Initialise binit and create the required directory structure:

```bash
binit init
```

This creates `~/.binit/` with the following layout:

```
~/.binit/
├── bin/          # installed binaries
├── downloads/    # cached release archives
├── logs/         # log files
└── config.yaml   # binit configuration
```

After init, add the bin directory to your PATH:

```bash
export PATH="$HOME/.binit/bin:$PATH"
```

To persist it, add the line above to your shell config (`~/.bashrc`, `~/.zshrc`, etc.).

To reinitialise from scratch:

```bash
binit init --reinit
```

## Shell Completion

```bash
# bash — add to ~/.bashrc
eval "$(binit completion bash)"

# zsh — add to ~/.zshrc
eval "$(binit completion zsh)"

# fish — add to ~/.config/fish/config.fish
binit completion fish | source
```

## Commands

### `binit tool install`

Install a binary from the latest GitHub release.

```bash
binit tool install -r <owner/repo>
binit tool install -r <https://github.com/owner/repo>
```

For repos that ship multiple binaries, use `--name`/`-n` to pick one:

```bash
binit tool install -r <owner/repo> -n <binary>
```

**Examples:**

```bash
binit tool install -r anchore/grant
binit tool install -r ahmetb/kubectx           # installs kubectx
binit tool install -r ahmetb/kubectx -n kubens # installs kubens
```

binit automatically matches the correct release asset for your OS and architecture, extracts the archive, and places the binary in `~/.binit/bin/`.

---

### `binit tool update`

Update an installed tool to its latest release.

```bash
# Update a single tool
binit tool update --name <tool>
binit tool update -n <tool>

# Update all installed tools
binit tool update --all
binit tool update -a
```

**Examples:**

```bash
binit tool update -n gitleaks
binit tool update --all
```

---

### `binit tool uninstall`

Remove an installed tool and delete its binary.

```bash
binit tool uninstall --name <tool>
binit tool uninstall -n <tool>
```

---

### `binit tool --list-installed`

Print a table of all installed tools with their version, release tag, and binary path.

```bash
binit tool --list-installed
```

---

### `binit config`

Print or validate the binit configuration.

```bash
# Print current config
binit config --print
binit config -p

# Validate config against schema
binit config --check
binit config -c
```

---

## Configuration

binit stores its configuration at `~/.binit/config.yaml`. It is written automatically during `binit init` and updated after each install.

```yaml
binit_version: 0.1.0
os: linux
arch: amd64
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
```

## Supported Platforms

| OS    | Architectures                              |
|-------|--------------------------------------------|
| Linux | amd64, arm64, armv7, armv6, 386, ppc64le, s390x |

## Logs

Logs are written to `~/.binit/logs/binit_<date>.log`.
