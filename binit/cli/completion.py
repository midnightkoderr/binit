import click
from click.shell_completion import BashComplete, FishComplete, ZshComplete


_CLASSES = {
    'bash': BashComplete,
    'zsh': ZshComplete,
    'fish': FishComplete,
}


@click.command(name='completion')
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish']))
def completion(shell: str):
    '''Output shell completion script for SHELL.

    \b
    Add to your shell config:
      bash:  eval "$(binit completion bash)"
      zsh:   eval "$(binit completion zsh)"
      fish:  binit completion fish | source
    '''
    from binit.cli import cli
    comp = _CLASSES[shell](cli, {}, 'binit', '_BINIT_COMPLETE')
    click.echo(comp.source())
