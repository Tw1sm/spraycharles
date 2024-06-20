from rich.console import Console
from rich.theme import Theme

__version__ = "1.0.10"

# Defining theme
custom_theme = Theme(
    {
        "info": "blue",
        "good": "bold bright_green",
        "warning": "bold yellow",
        "danger": "bold bright_red",
    }
)

console = Console(theme=custom_theme)
