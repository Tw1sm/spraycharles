import typer
from spraycharles.lib.utils import ntlm_challenger

app = typer.Typer()
COMMAND_NAME = 'parse'
HELP =  'Parse NTLM over HTTP and SMB endpoints to collect domain information'

@app.callback(no_args_is_help=True, invoke_without_command=True)
def main(
    url: str = typer.Argument(..., help="URL to parse"),
    smbv1: bool = typer.Option(False, '--smbv1', help="Use SMBv1 protocol")):

    ntlm_challenger(url, smbv1)

