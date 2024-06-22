import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.console import Console
from rich.theme import Theme
from rich.highlighter import JSONHighlighter

OBJ_EXTRA_FMT = {
    "markup": True,
    "highlighter": False
}

JSON_FMT = {
    "highlighter": JSONHighlighter()
}

console = Console()
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
            "%(message)s",
            datefmt='[%X]'
        )
    )
    logger.addHandler(richHandler)