import logging
from typing import TYPE_CHECKING, Any, Callable, ClassVar, TypeVar, Self

if TYPE_CHECKING:
    from policy_inspector.models import SecurityRule

logger = logging.getLogger(__name__)

ScenarioCheck = TypeVar("ScenarioCheck", bound=Callable)
ScenarioResults = TypeVar("ScenarioResults")


class Scenario:
    scenarios: ClassVar[set[type[Self]]] = {}

    checks: list[ScenarioCheck] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.scenarios.add(cls)

    @classmethod
    def list(cls) -> set[type[Self]]:
        return cls.scenarios

    def execute(self) -> ScenarioResults:
        raise NotImplementedError

    def analyze(self, results: ScenarioResults) -> Any:
        raise NotImplementedError

    def run_checks(self,
                   *rules: "SecurityRule"
                   ) -> dict[str, Any]:
        results = {}
        for check in self.checks:
            try:
                results[check.__name__] = check(*rules)
            except Exception as ex:
                logger.exception(f"Error occur during running {check}. {ex}")  # noqa: TRY401
        return results
