from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass
from time import perf_counter

from ..protocols import CommandProtocol, CommandResult, LoggingProtocol
from ..utils import Tracer, duration_from_perfcounters


@dataclass
class BaseCommand(ABC, CommandProtocol):
    _: KW_ONLY
    logger: LoggingProtocol
    tracer: Tracer

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def execute_command(self) -> None: ...

    def execute(self) -> CommandResult:
        start_counter = perf_counter()
        try:
            self.execute_command()
        except Exception as e:
            self.tracer.log_exception(e, self.name())
            self.logger.report_exception(self.name(), e)
            return CommandResult.FAILURE
        end_counter = perf_counter()
        self.tracer.add_context("cmd_duration", duration_from_perfcounters(start_counter, end_counter))
        self.tracer.log(self.name())
        return CommandResult.SUCCESS
