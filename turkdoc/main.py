"""turkdoc CLI — explain Turkish government documents in plain language."""

from pathlib import Path
from typing import Optional

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from turkdoc import __version__
from turkdoc.explainer import explain_document, is_likely_turkish
from turkdoc.history import get_recent_history, save_to_history
from turkdoc.ocr import extract_text_from_image
from turkdoc.output import (
    console,
    print_error,
    print_explanation,
    print_history_entry,
    print_warning,
)

app = typer.Typer(
    name="turkdoc",
    help="Explain Turkish government documents in simple English or Arabic.",
    add_completion=False,
)

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
DEMO_FILE = EXAMPLES_DIR / "residence_permit.txt"


def _resolve_language(lang: str) -> str:
    normalized = lang.lower().strip()
    if normalized not in ("english", "arabic"):
        raise typer.BadParameter("Language must be 'english' or 'arabic'.")
    return normalized


def _run_explanation(text: str, language: str) -> None:
    if not text.strip():
        print_error("No text provided. Use --text or --image to supply document content.")
        raise typer.Exit(1)

    if not is_likely_turkish(text):
        print_warning(
            "The input text does not appear to be Turkish. "
            "Processing anyway, but results may be less accurate."
        )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Analyzing document...", total=None)
        result = explain_document(text, language)

    print_explanation(result, language)
    try:
        save_to_history(result.get("document_type", "Unknown"), result.get("urgency", "MEDIUM"))
    except OSError:
        print_warning("Could not save to history (check write permissions).")


@app.command()
def explain(
    text: Optional[str] = typer.Option(
        None, "--text", "-t", help="Turkish document text to explain."
    ),
    image: Optional[Path] = typer.Option(
        None, "--image", "-i", help="Path to an image or PDF of the document."
    ),
    lang: str = typer.Option(
        "english", "--lang", "-l", help="Output language: english or arabic."
    ),
) -> None:
    """Explain a Turkish government document."""
    language = _resolve_language(lang)

    if text and image:
        print_error("Please provide either --text or --image, not both.")
        raise typer.Exit(1)

    if not text and not image:
        print_error(
            "No input provided.\n\n"
            "Usage:\n"
            '  turkdoc explain --text "your Turkish text here"\n'
            "  turkdoc explain --image path/to/photo.jpg"
        )
        raise typer.Exit(1)

    if image:
        try:
            document_text = extract_text_from_image(str(image))
        except FileNotFoundError as exc:
            print_error(str(exc))
            raise typer.Exit(1) from exc
        except ValueError as exc:
            print_error(str(exc))
            raise typer.Exit(1) from exc
        except Exception as exc:
            print_error(f"Failed to process image: {exc}")
            raise typer.Exit(1) from exc
    else:
        document_text = text  # type: ignore[assignment]

    try:
        _run_explanation(document_text, language)
    except EnvironmentError as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc
    except TimeoutError as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc
    except Exception as exc:
        print_error(f"An unexpected error occurred: {exc}")
        raise typer.Exit(1) from exc


@app.command()
def demo() -> None:
    """Run turkdoc on a sample residence permit document."""
    if not DEMO_FILE.exists():
        print_error(f"Demo file not found: {DEMO_FILE}")
        raise typer.Exit(1)

    console.print("[bold cyan]🏛️  turkdoc Demo[/bold cyan]")
    console.print(f"[dim]Using sample document: {DEMO_FILE.name}[/dim]\n")

    sample_text = DEMO_FILE.read_text(encoding="utf-8")
    try:
        _run_explanation(sample_text, "english")
    except EnvironmentError as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc
    except TimeoutError as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc
    except Exception as exc:
        print_error(f"Demo failed: {exc}")
        raise typer.Exit(1) from exc


@app.command()
def history() -> None:
    """Show the last 10 explained documents."""
    entries = get_recent_history(limit=10)

    console.print()
    console.print("[bold cyan]📋 Explanation History (last 10)[/bold cyan]")
    console.print("[dim]Document text is not stored for privacy.[/dim]\n")

    if not entries:
        console.print("  [dim]No history yet. Run 'turkdoc explain' or 'turkdoc demo' first.[/dim]")
        console.print()
        return

    for i, entry in enumerate(entries, 1):
        print_history_entry(entry, i)

    console.print()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"turkdoc version {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True
    ),
) -> None:
    """Turkish Document Explainer — understand official documents with AI."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()
