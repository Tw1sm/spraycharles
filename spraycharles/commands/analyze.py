import typer
from enum import Enum

from spraycharles.lib.analyze import Analyzer
from spraycharles.lib.logger import init_logger
from spraycharles.lib.utils import HookSvc

app = typer.Typer()
COMMAND_NAME = 'analyze'
HELP =  'Analyze CSV files for potential spray hits'


@app.callback(no_args_is_help=True, invoke_without_command=True)
def main(
    infile: str = typer.Argument(..., help="Filepath of the CSV file"),
    notify: HookSvc = typer.Option(None, case_sensitive=False, help="Enable notifications for Slack, Teams or Discord."),
    webhook: str = typer.Option(False, help="Webhook used for specified notification module."),
    host: str = typer.Option(False, help="Target host associated with CSV file.")):
    
    init_logger(False)
    
    analyzer = Analyzer(infile, notify, webhook, host)
    analyzer.analyze()

