import logging
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from policy_inspector.models import SecurityRule

logger = logging.getLogger(__name__)

ScenarioResults = TypeVar("ScenarioResults")

CheckResult = tuple[bool, str]
"""
A tuple representing the result of a check function.

1. ``bool``: Indicates whether the check was fulfilled or not.
2. ``str``: A verbose message describing the result.
"""

Check = Callable[[...], CheckResult]
"""A callable type definition for a scenario check function."""


class Scenario:
    """
    Base class for defining security scenarios and checks.

    Attributes:
        _scenarios: A set of all registered subclasses of Scenario.
        checks: A list of callable check functions to be executed on security rules.
    """

    _scenarios: set[type["Scenario"]] = set()

    checks: list[Check] = []

    def __init_subclass__(cls, **kwargs) -> None:
        """Registers subclasses automatically in the `scenarios` set."""
        super().__init_subclass__(**kwargs)
        cls._scenarios.add(cls)

    @classmethod
    def get_available(cls) -> set[type["Scenario"]]:
        """
        Retrieve all registered ``Scenario`` subclasses.

        Returns:
            A set containing all subclasses of ``Scenario``.
        """
        return cls._scenarios

    def execute(self) -> ScenarioResults:
        """
        Execute the scenario logic.

        Warnings:
            This method must be implemented by subclasses.

        Returns:
            The results of executing.
        """
        raise NotImplementedError

    def analyze(self, results: ScenarioResults) -> Any:
        """
        Analyze the results obtained from executing a scenario.

        Warnings:
            This method must be implemented by subclasses.

        Args:
            results: The results to analyze.

        Returns:
            The analysis outcome.
        """
        raise NotImplementedError

    def run_checks(self, *rules: "SecurityRule") -> dict[str, CheckResult]:
        """
        Run all defined ``checks`` against the provided security rule or rules.

        Args:
            *rules: Security rules to evaluate.

        Returns:
            A dictionary mapping check function names to their results (status and message).

        Logs exceptions if any check raises an error during execution.
        """
        results = {}
        for check in self.checks:
            try:
                results[check.__name__] = check(*rules)
            except Exception as ex:  # noqa: BLE001
                logger.exception(
                    f"Error '{ex}' occur during running: \n{check}\n{rules}. "  # noqa: TRY401
                )
        return results
