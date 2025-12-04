import sys
import re
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from .agent import create_agent


console = Console()


def remove_markdown_syntax(text: str) -> str:
    """
    Remove markdown syntax from text for cleaner console output.

    Args:
        text: Text with markdown syntax

    Returns:
        Clean text without markdown formatting
    """
    # Remove bold **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    # Remove italic *text*
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    # Remove headers ###
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove inline code `code`
    text = re.sub(r"`(.*?)`", r"\1", text)
    # Remove links [text](url)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)

    return text


def format_output(text: str) -> Text:
    """
    Format output text with colors and styling for rich console.

    Args:
        text: Text to format

    Returns:
        Formatted Rich Text object
    """
    # Remove markdown syntax first
    clean_text = remove_markdown_syntax(text)

    # Create Rich Text object
    formatted = Text()

    # Split by lines and add colored formatting
    for line in clean_text.split("\n"):
        if ":" in line and not line.strip().startswith("http"):
            # Highlight key-value pairs
            parts = line.split(":", 1)
            if len(parts) == 2:
                formatted.append(parts[0] + ":", style="bold cyan")
                formatted.append(parts[1] + "\n")
            else:
                formatted.append(line + "\n")
        else:
            formatted.append(line + "\n")

    return formatted


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        Dictionary with parsed arguments
    """
    verbose = False

    for arg in sys.argv[1:]:
        if arg in ["--verbose", "-v"]:
            verbose = True

    return {"verbose": verbose}


def main():
    args = parse_arguments()
    verbose = args["verbose"]

    console.print("[bold green]🎬 Запуск AI Агента-Киноэксперта...[/bold green]")

    try:
        agent = create_agent(verbose=verbose)
        console.print(
            "[bold green]✅ Агент готов! Задавайте вопросы о фильмах (или 'выход' для завершения)[/bold green]\n"
        )
    except Exception as e:
        console.print(f"[bold red]❌ Ошибка инициализации агента: {e}[/bold red]")
        return

    while True:
        try:
            user_input = console.input("[bold yellow]Вы:[/bold yellow] ")

            if user_input.lower() in ["выход", "exit", "quit"]:
                console.print("\n[bold blue]👋 До встречи![/bold blue]")
                break

            if not user_input.strip():
                continue

            # Show loading animation
            with Live(
                Spinner("dots", text="[cyan]Обрабатываю запрос...[/cyan]"),
                console=console,
                refresh_per_second=10,
            ):
                response = agent.invoke({"input": user_input})

            # Format and display output
            output = response.get("output", "Нет ответа")

            if verbose:
                # In verbose mode, show raw output
                console.print(f"\n[bold green]Агент:[/bold green] {output}\n")
            else:
                # In normal mode, show formatted output without markdown
                formatted_output = format_output(output)
                console.print(
                    Panel(
                        formatted_output,
                        title="[bold green]Агент[/bold green]",
                        border_style="green",
                    )
                )
                console.print()

        except KeyboardInterrupt:
            console.print("\n[bold blue]👋 До встречи![/bold blue]")
            break
        except Exception as e:
            console.print(f"[bold red]❌ Ошибка: {e}[/bold red]\n")
            if verbose:
                import traceback

                console.print("[dim]" + traceback.format_exc() + "[/dim]")


if __name__ == "__main__":
    main()
