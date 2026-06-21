from __future__ import annotations

from enum import IntEnum
from typing import Protocol


class CommandResult(IntEnum):
    SUCCESS = 0
    FAILURE = 1


class CommandProtocol(Protocol):
    def execute(self) -> CommandResult: ...
