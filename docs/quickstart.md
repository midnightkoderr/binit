# Quickstart

Get binit installed and your first binary downloaded in under two minutes.

## Requirements

- Linux (only supported platform)
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Install binit

```bash
git clone https://github.com/midnightkoderr/binit
cd binit
uv pip install -e .
```

Verify the install:

```bash
binit --version
```

## Initialise

```bash
binit init
```

This creates `~/.binit/` with the following layout:

```
~/.binit/
├── bin/          # installed binaries land here
├── downloads/    # cached release archives
├── logs/         # daily log files
└── config.yaml   # binit configuration
```

It also detects your OS and CPU architecture and writes them to `config.yaml`.

## Add bin to PATH

```bash
export PATH="$HOME/.binit/bin:$PATH"
```

Persist it by adding the line above to your shell config (`~/.bashrc`, `~/.zshrc`, etc.).

## Install your first binary

```bash
binit tool install -r anchore/grant
```

binit fetches the latest GitHub release, picks the right asset for your platform, extracts the archive, and places the binary in `~/.binit/bin/`.

For repos that ship multiple binaries, use `--name`/`-n` to pick one:

```bash
binit tool install -r ahmetb/kubectx -n kubens
```

## Shell completion

```bash
# bash — add to ~/.bashrc
eval "$(binit completion bash)"

# zsh — add to ~/.zshrc
eval "$(binit completion zsh)"

# fish — add to ~/.config/fish/config.fish
binit completion fish | source
```

`binit completion <shell>` prints the completion script for the given shell. Piping it through `eval` (or `source` for fish) activates it for the current session; adding it to your shell config makes it permanent.

## What's next

- [Usage guide](usage.md) — all commands with examples
- [Configuration reference](configuration.md) — config file fields explained
