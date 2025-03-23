import logging
from typing import Any, Callable, Protocol, ClassVar, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from policy_inspector.models import SecurityRule

logger = logging.getLogger(__name__)


class Scenario(Protocol):
    checks: ClassVar[list[Callable]] = []

    def execute(self) -> Any: ...

    def analyze(self, results: dict[str, Any]) -> Any: ...


CheckCallable = TypeVar("CheckCallable", bound=Callable)


def run_checks(checks: list[CheckCallable], *rules: "SecurityRule") -> dict[str, Any]:
    results = {}
    for check in checks:
        try:
            results[check.__name__] = check(*rules)
        except Exception as ex:
            logger.exception(f"Error occur during running {check}. {ex}")  # noqa: TRY401
    return results
