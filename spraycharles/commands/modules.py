import typer
from rich.table import Table
from rich.padding import Padding
from spraycharles.lib.logger import console
from spraycharles.targets import all as all_modules

app = typer.Typer()
COMMAND_NAME = 'modules'
HELP = 'List spraying modules'

@app.callback(invoke_without_command=True)
def main():

    module_table = Table(
        show_header=True,
        show_footer=False,
        min_width=61,
        title="Spraying Modules",
        title_justify="left",
        title_style="bold reverse",
    )
    module_table.add_column("Module", style="bold")
    module_table.add_column("Description")

    for module in all_modules:
        module_table.add_row(f"[blue]{module.NAME}[/blue]", f"[yellow]{module.DESCRIPTION}[/yellow]")

    console.print(Padding(module_table, (1, 1)))