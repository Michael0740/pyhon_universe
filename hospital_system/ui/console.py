"""
Rich console wrapper providing formatted tables, banners, badges, and user prompts.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from typing import Optional, List, Any

console = Console()


def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Prints a styled hospital header banner."""
    content = f"[bold cyan]{title}[/bold cyan]"
    if subtitle:
        content += f"\n[dim]{subtitle}[/dim]"
    console.print(Panel(content, border_style="cyan", padding=(0, 2)))


def print_success(message: str) -> None:
    """Prints a green success message."""
    console.print(f"[bold green]✔ SUCCESS:[/bold green] {message}")


def print_error(message: str) -> None:
    """Prints a red error message."""
    console.print(f"[bold red]✖ ERROR:[/bold red] {message}")


def print_warning(message: str) -> None:
    """Prints a yellow warning message."""
    console.print(f"[bold yellow]⚠ WARNING:[/bold yellow] {message}")


def print_info(message: str) -> None:
    """Prints a blue informational message."""
    console.print(f"[bold blue]ℹ INFO:[/bold blue] {message}")


def prompt_string(label: str, default: Optional[str] = None, allow_empty: bool = False) -> str:
    """Prompts the user for a text string."""
    while True:
        val = Prompt.ask(f"[bold white]{label}[/bold white]", default=default or "")
        val = val.strip()
        if val or allow_empty or default:
            return val if val else (default or "")
        print_error("This field cannot be empty. Please try again.")


def prompt_int(label: str, min_val: Optional[int] = None) -> int:
    """Prompts the user for a valid integer."""
    while True:
        val_str = Prompt.ask(f"[bold white]{label}[/bold white]")
        try:
            val = int(val_str.strip())
            if min_val is not None and val < min_val:
                print_error(f"Value must be at least {min_val}.")
                continue
            return val
        except ValueError:
            print_error("Please enter a valid whole number.")


def prompt_float(label: str, min_val: Optional[float] = None) -> float:
    """Prompts the user for a valid decimal number."""
    while True:
        val_str = Prompt.ask(f"[bold white]{label}[/bold white]")
        try:
            val = float(val_str.strip())
            if min_val is not None and val < min_val:
                print_error(f"Value must be at least {min_val}.")
                continue
            return val
        except ValueError:
            print_error("Please enter a valid decimal number (e.g. 15.50).")


def prompt_confirm(label: str, default: bool = True) -> bool:
    """Prompts user for confirmation (Y/n)."""
    return Confirm.ask(f"[bold yellow]{label}[/bold yellow]", default=default)

