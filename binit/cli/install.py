import click

from binit.installer import Installer


@click.command(name='install')
@click.option('--github-repo', '-r', required=True, help='GitHub repo as owner/repo or full URL')
def install(github_repo: str):
    '''Install a binary from the latest GitHub release'''
    try:
        tool = Installer(github_repo).run()
    except ValueError as e:
        raise click.BadParameter(str(e), param_hint='--github-repo')
