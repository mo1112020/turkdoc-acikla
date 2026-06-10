"""Rich terminal output formatting for turkdoc explanations."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

URGENCY_STYLES = {
    "LOW": ("🟢", "green", "LOW"),
    "MEDIUM": ("🟡", "yellow", "MEDIUM"),
    "HIGH": ("🔴", "red", "HIGH"),
}


def _urgency_panel(urgency: str, reason: str) -> Panel:
    icon, color, label = URGENCY_STYLES.get(urgency.upper(), URGENCY_STYLES["MEDIUM"])
    content = Text()
    content.append(f"{icon} {label}", style=f"bold {color}")
    if reason:
        content.append(f"\n{reason}", style=color)
    return Panel(content, title="[bold]Urgency[/bold]", border_style=color)


def print_explanation(result: dict, language: str) -> None:
    """Render a parsed explanation with rich formatting."""
    urgency = result.get("urgency", "MEDIUM").upper()
    _, color, _ = URGENCY_STYLES.get(urgency, URGENCY_STYLES["MEDIUM"])

    console.print()
    console.print(
        Panel(
            f"[bold]{result.get('document_type', 'Unknown Document')}[/bold]\n"
            f"[dim]Sent by:[/dim] {result.get('sent_by', 'Unknown')}",
            title="[bold cyan]📄 Document[/bold cyan]",
            border_style="cyan",
        )
    )

    console.print()
    console.print(
        Panel(
            result.get("explanation", "No explanation available."),
            title=f"[bold]Explanation ({language.title()})[/bold]",
            border_style="blue",
        )
    )

    console.print()
    console.print(_urgency_panel(urgency, result.get("reason", "")))

    deadlines = result.get("deadlines", "No deadline detected.")
    console.print()
    console.print(
        Panel(
            deadlines,
            title="[bold]📅 Deadlines[/bold]",
            border_style="magenta",
        )
    )

    steps = result.get("next_steps", [])
    if steps:
        steps_text = "\n".join(f"  [bold]{i}.[/bold] {step}" for i, step in enumerate(steps, 1))
    else:
        steps_text = "  No specific steps identified."
    console.print()
    console.print(
        Panel(
            steps_text,
            title="[bold]✅ What You Should Do[/bold]",
            border_style="green",
        )
    )

    contacts = result.get("contacts", "")
    if contacts:
        console.print()
        console.print(
            Panel(
                contacts,
                title="[bold]📞 Important Contacts[/bold]",
                border_style="cyan",
            )
        )

    disclaimer = result.get(
        "disclaimer",
        "This is an AI explanation, not legal advice. "
        "Consult a professional for important matters.",
    )
    console.print()
    console.print(
        Panel(
            f"[dim italic]{disclaimer}[/dim italic]",
            border_style="dim",
        )
    )
    console.print()


def print_warning(message: str) -> None:
    console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")


def print_error(message: str) -> None:
    console.print(f"[bold red]❌ {message}[/bold red]")


def print_history_entry(entry: dict, index: int) -> None:
    urgency = entry.get("urgency", "MEDIUM").upper()
    icon, color, _ = URGENCY_STYLES.get(urgency, URGENCY_STYLES["MEDIUM"])
    console.print(
        f"  [bold]{index}.[/bold] [{color}]{icon}[/{color}] "
        f"[bold]{entry.get('document_type', 'Unknown')}[/bold] "
        f"[dim]({entry.get('timestamp', '')})[/dim]"
    )
