import logging
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from policy_inspector.models import SecurityRule

logger = logging.getLogger(__name__)

ScenarioResults = TypeVar("ScenarioResults")

CheckResult = tuple[bool, str]
"""Return format from a check function.`.

1. Status ``bool`` - Whether the rules pair fulfill a check.
2. Message ``str`` - Verbose message.
"""

Check = Callable[[...], CheckResult]
"""Definition of typing for a scenario type of function."""


class Scenario:
    scenarios: set[type["Scenario"]] = set()

    checks: list[Check] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.scenarios.add(cls)

    @classmethod
    def list(cls) -> set[type["Scenario"]]:
        return cls.scenarios

    def execute(self) -> ScenarioResults:
        raise NotImplementedError

    def analyze(self, results: ScenarioResults) -> Any:
        raise NotImplementedError

    def run_checks(self, *rules: "SecurityRule") -> dict[str, CheckResult]:
        results = {}
        for check in self.checks:
            try:
                results[check.__name__] = check(*rules)
            except Exception as ex:  # noqa: BLE001
                logger.exception(
                    f"Error '{ex}' occur during running: \n{check}\n{rules}. "  # noqa: TRY401
                )
        return results
