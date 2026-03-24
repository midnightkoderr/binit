import click

from binit.core.config import load_config
from binit.schema import ConfigSchema


@click.command(name='config')
@click.option('--print', '-p', 'do_print', is_flag=True, default=False, help='Print current configuration')
@click.option('--check', '-c', is_flag=True, default=False, help='Validate configuration against schema')
@click.pass_context
def config(ctx: click.Context, do_print: bool, check: bool):
    '''Print or validate binit configuration'''
    if not do_print and not check:
        click.echo(ctx.get_help())
        return

    try:
        cfg = load_config()
    except FileNotFoundError as e:
        raise click.ClickException(str(e))

    if do_print:
        for key, value in cfg.items():
            click.echo(f'{key}: {value}')

    if check:
        errors = ConfigSchema().validate(cfg)
        if errors:
            for field, msg in errors.items():
                click.echo(f'  {field}: {msg}', err=True)
            raise click.ClickException('Config validation failed')
        click.echo('Config is valid')
