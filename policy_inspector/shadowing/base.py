import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, Callable, Literal, Optional

from policy_inspector.scenario import CheckResult, Scenario
from policy_inspector.shadowing.checks import (
    check_action,
    check_application,
    check_destination_address,
    check_destination_zone,
    check_services,
    check_source_address,
    check_source_zone,
)
from policy_inspector.shadowing.show import show_as_table, show_as_text

if TYPE_CHECKING:
    from policy_inspector.model.security_rule import SecurityRule

logger = logging.getLogger(__name__)


ShadowingCheckFunction = Callable[["SecurityRule", "SecurityRule"], CheckResult]


ChecksOutputs = dict[str, CheckResult]
"""Dict with check's name as keys and its output as value."""

PrecedingRulesOutputs = dict[str, ChecksOutputs]
"""Dict with Preceding Rule's name as keys and ChecksOutputs as its value."""

ExecuteResults = dict[str, PrecedingRulesOutputs]
"""Dict with Rule's name as keys and ``PrecedingRulesOutputs`` as value."""

AnalysisResults = list[tuple["SecurityRule", list["SecurityRule"]]]
"""List of two-element tuples where first element is a ``SecurityRule`` and second element is list of shadowing rules"""


class Shadowing(Scenario):
    """
    This scenario identifies when a rule is completely shadowed by a preceding rule.

    Shadowing occurs when a rule will never be matched
    because a rule earlier in the processing order would always match first.
    """

    name: str = "Shadowing"
    checks: list[ShadowingCheckFunction] = [
        check_action,
        check_application,
        check_services,
        check_source_zone,
        check_destination_zone,
        check_source_address,
        check_destination_address,
    ]

    show_map: dict[str, Callable] = {
        "text": show_as_text,
        "table": show_as_table,
    }

    def __init__(self, security_rules: list["SecurityRule"]):
        self.security_rules = security_rules
        self.rules_by_name = {rule.name: rule for rule in self.security_rules}
        self.execution_results: Optional[ExecuteResults] = None
        self.analysis_results: Optional[AnalysisResults] = None

    def execute(self) -> ExecuteResults:
        rules = self.security_rules
        results = {}
        for i, rule in enumerate(rules):
            output = {}
            for j in range(i):
                preceding_rule = rules[j]
                output[preceding_rule.name] = self.run_checks(
                    rule,
                    preceding_rule,
                )
            results[rule.name] = output
        self.execution_results = results
        return results

    def analyze(
        self,
        results: ExecuteResults,
    ) -> AnalysisResults:
        analysis_results = []
        for rule_name, rule_results in results.items():
            shadowing_rules = []
            for preceding_rule_name, checks_results in rule_results.items():
                if all(
                    check_result[0] for check_result in checks_results.values()
                ):
                    shadowing_rules.append(
                        self.rules_by_name[preceding_rule_name]
                    )
            if shadowing_rules:
                analysis_results.append(
                    (self.rules_by_name[rule_name], shadowing_rules)
                )
        self.analysis_results = analysis_results
        return analysis_results

    def show(
        self,
        analysis_results: AnalysisResults,
        formats: Iterable[Literal["text", "table"]],
    ):
        if not formats:
            logger.debug("No show format was provided.")
            return
        for format_ in formats:
            show_func = self.show_map.get(format_)
            if not show_func:
                logger.warning(f"Show format '{format_}' unknown!")
                continue
            try:
                show_func(analysis_results)
            except Exception as ex:
                logger.error(f"Failed to show {format_}. {ex}")
