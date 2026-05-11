import click
from click import Option
from click.core import ParameterSource
from click.shell_completion import CompletionItem


class Command(click.Command):
    '''click.Command that also suggests options when Tab is pressed with no prefix typed.'''

    def shell_complete(self, ctx: click.Context, incomplete: str) -> list[CompletionItem]:
        completions = super().shell_complete(ctx, incomplete)
        if not incomplete:
            for param in self.get_params(ctx):
                if (
                    not isinstance(param, Option)
                    or param.hidden
                    or (
                        not param.multiple
                        and ctx.get_parameter_source(param.name)
                        is ParameterSource.COMMANDLINE
                    )
                ):
                    continue
                completions.extend(
                    CompletionItem(name, help=param.help)
                    for name in [*param.opts, *param.secondary_opts]
                )
        return completions
