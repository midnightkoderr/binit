# Usage

Complete reference for all binit commands.

## Command overview

```
binit [--version] [--help]
binit init [--reinit]
binit tool install  -r <repo> [-n <name>]
binit tool update   [-n <name>] [--all]
binit tool uninstall -n <name>
binit tool --list-installed
binit config     [--print] [--check]
binit cache      [--clean] [--logs]
binit completion  bash | zsh | fish
```

---

## `binit init`

Initialise binit and create the directory structure under `~/.binit/`.

```bash
binit init
```

On first run this:

1. Creates `~/.binit/bin/`, `~/.binit/downloads/`, `~/.binit/logs/`
2. Detects the host OS and architecture
3. Writes `~/.binit/config.yaml`
4. Prints the PATH export hint

**Flags**

| Flag | Description |
|------|-------------|
| `--reinit` | Delete the existing `~/.binit/` directory and start fresh. All installed binaries and config are lost. |

```bash
binit init --reinit
```

> **Note:** `--reinit` is destructive. Back up anything in `~/.binit/bin/` that you care about before running it.

---

## `binit tool install`

Download and install a binary from the latest GitHub release.

```bash
binit tool install -r <owner/repo>
binit tool install -r <https://github.com/owner/repo>
```

**Flags**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--github-repo` | `-r` | Yes | GitHub repo as `owner/repo` or full URL |
| `--name` | `-n` | No | Binary name to select when a repo ships multiple binaries |

**What it does**

1. Calls the GitHub API to get the latest release and repo metadata.
2. Scores every release asset against your OS and architecture (see [Asset matching](#asset-matching)).
3. Downloads the best-scoring asset to `~/.binit/downloads/<tool>/`.
4. Extracts the archive (supports `.tar.gz`, `.tgz`, `.tar.bz2`, `.tar.xz`, `.zip`).
5. Finds the executable inside the extracted files (detected by ELF magic bytes).
6. Optionally prompts to rename the binary.
7. Moves the binary to `~/.binit/bin/` and sets `chmod 755`.
8. Updates `~/.binit/config.yaml` with tool metadata.

**Examples**

```bash
# Simple install
binit tool install -r gitleaks/gitleaks

# Full URL also works
binit tool install -r https://github.com/anchore/grant

# Pick a specific binary from a multi-binary repo
binit tool install -r ahmetb/kubectx -n kubens

# Use a short name that differs from the repo name
binit tool install -r openbao/openbao -n bao
```

**Re-install**

If the installed release matches the latest, binit skips the download. To force a re-install, uninstall first and then install again.

**Re-download prompt**

If the archive already exists in the downloads cache, binit asks whether to re-download. Answer `n` to reuse the cached file.

**Asset matching**

binit scores each release asset and selects the highest-scoring one that meets the minimum threshold. The scoring rules are:

| Condition | Score |
|-----------|-------|
| Filename starts with `<name>_` or `<name>-<digit>` | Required (−100 if missing when `--name` given) |
| Filename contains OS name | +4 |
| Filename contains an arch alias | +3 |
| File is an archive (`.tar.gz`, `.zip`, etc.) | +2 |
| Filename starts with repo name (bonus, no `--name`) | +2 |
| File has no extension (likely a raw binary) | +1 |
| File is a checksum/signature (`.sha256`, `.sig`, etc.) | −10 |

A minimum score of 6 is required. If no asset meets the threshold, the install fails.

When `--name` is given, binit requires the filename to start with `<name>_` or `<name>-<digit>` (word-boundary match) to avoid picking compound names — e.g. `-n bao` will not match `bao-hsm_2.5.3_linux_amd64.tar.gz`.

---

## `binit tool update`

Check for a newer release and update the installed binary if one exists.

```bash
# Update one tool
binit tool update -n gitleaks

# Update all installed tools
binit tool update --all
```

**Flags**

| Flag | Short | Description |
|------|-------|-------------|
| `--name` | `-n` | Name of the tool to update |
| `--all` | `-a` | Update every installed tool |

At least one of `--name` or `--all` is required.

If the installed release already matches the latest, binit prints a message and skips the tool.

---

## `binit tool uninstall`

Remove a tool: deletes the binary from `~/.binit/bin/` and removes the entry from `config.yaml`.

```bash
binit tool uninstall -n gitleaks
```

**Flags**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--name` | `-n` | Yes | Name of the installed tool to remove |

The downloads cache for that tool is not deleted. Use `binit cache --clean` to clear it.

---

## `binit tool --list-installed`

Print a table of all installed tools.

```bash
binit tool --list-installed
```

**Output columns**

| Column | Description |
|--------|-------------|
| Tool | Registered tool name |
| Version | Semantic version (e.g. `8.30.1`) |
| Release | GitHub tag (e.g. `v8.30.1`) |
| Binary | Absolute path to the installed binary |

---

## `binit config`

Inspect or validate the binit configuration file.

```bash
# Print all config key/value pairs
binit config --print
binit config -p

# Validate config against the schema
binit config --check
binit config -c
```

**Flags**

| Flag | Short | Description |
|------|-------|-------------|
| `--print` | `-p` | Print each key and value from `config.yaml` |
| `--check` | `-c` | Validate `config.yaml` against the marshmallow schema and report errors |

Without any flag, the help text is shown.

---

## `binit cache`

Manage cached files to free disk space.

```bash
# Delete all downloaded archives
binit cache --clean
binit cache -c

# Delete all log files
binit cache --logs
binit cache -l

# Delete both
binit cache --clean --logs
```

**Flags**

| Flag | Short | Description |
|------|-------|-------------|
| `--clean` | `-c` | Remove everything in `~/.binit/downloads/` (directory is recreated empty) |
| `--logs` | `-l` | Remove everything in `~/.binit/logs/` (directory is recreated empty) |

At least one flag is required. If a directory does not exist, binit reports it as already empty.

---

## `binit completion`

Print a shell completion script and activate it.

```bash
# bash — add to ~/.bashrc
eval "$(binit completion bash)"

# zsh — add to ~/.zshrc
eval "$(binit completion zsh)"

# fish — add to ~/.config/fish/config.fish
binit completion fish | source
```

**Arguments**

| Argument | Choices | Description |
|----------|---------|-------------|
| `SHELL` | `bash`, `zsh`, `fish` | Shell to generate the completion script for |

The command outputs the raw completion script to stdout. Running it through `eval` (or `source` for fish) registers tab-completion for the current session. Add it to your shell config to make it permanent.

---

## Logs

binit writes two log streams simultaneously:

- **Console** (stderr): INFO level and above
- **File**: `~/.binit/logs/binit_<YYYY-MM-DD>.log` — one file per day

Use `binit cache --logs` to purge old log files.
