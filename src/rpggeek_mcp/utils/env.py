from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


def load_dotenv_from(caller_file: str) -> None:
    """Walk up from caller_file's directory until a .env is found, then load it."""
    start = Path(caller_file).parent
    for directory in [start, *start.parents]:
        candidate = directory / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return
