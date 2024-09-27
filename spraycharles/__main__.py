import typer
from spraycharles.commands import all

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='rich',
    context_settings={'help_option_names': ['-h', '--help']},
    pretty_exceptions_show_locals=False
)

for command in all:
    app.add_typer(
        command.app,
        name=command.COMMAND_NAME,
        help=command.HELP
    )


if __name__ == "__main__":
    app(prog_name="spraycharles")