from __future__ import annotations

from importlib.metadata import PackageNotFoundError, metadata
from importlib.metadata import version as dist_version

import typer
from dotenv import load_dotenv
from rich.console import Console

from ..commands.test_command import TestCommand
from ..protocols import CommandProtocol, CompositeLogger, LoggingProtocol
from ..utils import Tracer, common_paths, initialize_request, initialize_tracing
from .file_logging_protocol import FileLogger
from .rich_logging_protocol import RichConsoleLogger


app = typer.Typer(
    name="rpggeek-mcp",
    add_completion=True,
    help="CLI for rpggeek-mcp",
)


def create_logger() -> tuple[LoggingProtocol, Tracer]:
    console = Console()
    console_logger: RichConsoleLogger = RichConsoleLogger(console)
    file_logger: FileLogger = FileLogger(common_paths.logfile_path())

    initialize_tracing(common_paths.tracefile_path())
    request_id: str = initialize_request()

    logger = CompositeLogger([console_logger, file_logger])
    logger.report_message(f"[blue]Session id: {request_id}[/blue]")
    return logger, Tracer()


@app.command("test")
def test() -> None:
    """Simple smoke command."""
    logger, tracer = create_logger()
    command: CommandProtocol = TestCommand(logger=logger, tracer=tracer)
    command.execute()


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if not value:
        return

    # IMPORTANT: distribution name (pyproject.toml [project].name), often hyphenated.
    # Example: "my-tool" even if your import package is "my_tool".
    DIST_NAME = "rpggeek-mcp"

    console = Console()

    try:
        pkg_version = dist_version(DIST_NAME)
        md = metadata(DIST_NAME)
        try:
            pkg_name = md["Name"]
        except KeyError:
            pkg_name = DIST_NAME

        console.print(f"{pkg_name} {pkg_version}")
    except PackageNotFoundError:
        # Running from source without an installed distribution
        console.print(f"{DIST_NAME} 0.0.0+unknown")

    raise typer.Exit()


@app.callback()
def _callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Root command group for reddit_rpg_miner."""
    # Intentionally empty: this forces Typer to keep subcommands like `test`.
    load_dotenv()


if __name__ == "__main__":
    app()
