import logging
from typing import Any, Callable, Protocol

logger = logging.getLogger(__name__)


class Scenario(Protocol):
    checks: list[Callable] = []

    def execute(self) -> Any: ...

    def analyze(self, results: dict[str, Any]) -> Any: ...
