import typer
from spraycharles.lib.utils import make_list
from spraycharles.lib.logger import init_logger

app = typer.Typer()
COMMAND_NAME = 'gen'
HELP =  'Generate custom password lists from JSON file'

@app.callback(no_args_is_help=True, invoke_without_command=True)
def main(
    infile: str = typer.Argument(..., exists=True, help="Filepath of the JSON file"),
    outfile: str = typer.Argument(..., writable=True, help="Name and path of the output file")):
    
    init_logger(False)
    make_list(infile, outfile)
