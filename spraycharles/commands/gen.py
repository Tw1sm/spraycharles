import typer
from spraycharles.utils.make_list import main as make_list

app = typer.Typer()
COMMAND_NAME = 'gen'
HELP =  'Generate custom password lists from JSON file'

@app.callback(no_args_is_help=True, invoke_without_command=True)
def main(
    infile: str = typer.Argument(..., exists=True, help="Filepath of the JSON file"),
    outfile: str = typer.Argument(..., writable=True, help="Name and path of the output file")
):
    make_list(infile, outfile)
