import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.console import Console
from rich.theme import Theme

OBJ_EXTRA_FMT = {
    "markup": True,
    "highlighter": False
}

FORMAT = "%(message)s"

# 
# Defining theme / console
#
custom_theme = Theme(
    {
        "info": "blue",
        "good": "bold bright_green",
        "warning": "bold yellow",
        "danger": "bold bright_red",
    }
)

console = Console(theme=custom_theme)


logger = logging.getLogger(__name__)

#
# custom logger
#
def init_logger(debug):
    richHandler = RichHandler(
        omit_repeated_times=False,
        show_path=False,
        keywords=[],
        console=console
    )
    
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    richHandler.setFormatter(
        logging.Formatter(
            FORMAT,
            datefmt='[%X]'
        )
    )
    logger.addHandler(richHandler)