import logging
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from policy_inspector.models import SecurityRule

logger = logging.getLogger(__name__)

ScenarioCheck = TypeVar("ScenarioCheck", bound=Callable)
ScenarioResults = TypeVar("ScenarioResults")


class Scenario:
    scenarios: set[type["Scenario"]] = set()

    checks: list[ScenarioCheck] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.scenarios.add(cls)

    @classmethod
    def get_args(cls) -> list[str]:
        """Get ``__init__`` arguments, except ``self``."""
        try:
            args = list(cls.__init__.__code__.co_varnames)
            return args[1:]
        except AttributeError:
            return []

    @classmethod
    def list(cls) -> set[type["Scenario"]]:
        return cls.scenarios

    def execute(self) -> ScenarioResults:
        raise NotImplementedError

    def analyze(self, results: ScenarioResults) -> Any:
        raise NotImplementedError

    def run_checks(self, *rules: "SecurityRule") -> dict[str, Any]:
        results = {}
        for check in self.checks:
            try:
                results[check.__name__] = check(*rules)
            except Exception as ex:
                logger.exception(
                    f"Error '{ex}' occur during running: \n{check}\n{rules}. "
                )  # noqa: TRY401
        return results
