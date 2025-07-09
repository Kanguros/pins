import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING

from policy_inspector.scenario import Scenario
from policy_inspector.scenarios.shadowing.checks import (
    CheckFunction,
    CheckResult,
    check_action,
    check_application,
    check_destination_address,
    check_destination_zone,
    check_services,
    check_source_address,
    check_source_zone,
)

if TYPE_CHECKING:
    from policy_inspector.model.security_rule import SecurityRule
    from policy_inspector.panorama import PanoramaConnector

logger = logging.getLogger(__name__)


ChecksOutputs = dict[str, CheckResult]
"""Dict with check's name as keys and its output as value."""

PrecedingRulesOutputs = dict[str, ChecksOutputs]
"""Dict with Preceding Rule's name as keys and ChecksOutputs as its value."""

ExecuteResults = dict[str, PrecedingRulesOutputs]
"""Dict with Rule's name as keys and ``PrecedingRulesOutputs`` as value."""

AnalysisResult = list[tuple["SecurityRule", list["SecurityRule"]]]
"""List of two-element tuples where first element is a ``SecurityRule`` and second element is list of shadowing rules"""

AnalysisResults = dict[str, AnalysisResult]


def exclude_checks(
    checks: list[CheckFunction], keywords: Iterable[str]
) -> list[CheckFunction]:
    if not keywords:
        return []
    checks = checks.copy()
    logger.info(f"Excluding checks by keywords: {', '.join(keywords)}")
    for i, check in enumerate(checks):
        check_name = check.__name__
        if any(keyword in check_name for keyword in keywords):
            logger.info(f"✖ Check '{check_name}' excluded")
            checks.pop(i)
    return checks


def run_checks(checks, *rules: "SecurityRule") -> dict[str, CheckResult]:
    """
    Run all defined ``checks`` against the provided security rule or rules.

    Args:
        *rules: Security rules to evaluate.

    Notes:
        Logs exceptions if any check raises an error during execution.

    Returns:
        A dictionary mapping check function names to their results (status and message).
    """
    results = {}
    for check in checks:
        try:
            results[check.__name__] = check(*rules)
        except Exception as ex:  # noqa: BLE001
            logger.warning(f"☠ Error: {ex}")
            logger.warning(f"☠ Check function: '{check.__name__}'")
            for i, rule in enumerate(rules, start=1):
                logger.warning(f"☠ Rule {i}: {rule.name}")
                logger.debug(f"☠ Rule {i}: {rule.model_dump()}")
    return results


class Shadowing(Scenario):
    """Scenario for detecting shadowing rules in Palo Alto Panorama."""

    name: str = "Shadowing"
    checks: list[CheckFunction] = [
        check_action,
        check_application,
        check_services,
        check_source_zone,
        check_destination_zone,
        check_source_address,
        check_destination_address,
    ]

    def __init__(
        self,
        panorama: "PanoramaConnector" = None,
        device_groups: list[str] = None,
        security_rules_by_dg: dict[str, list["SecurityRule"]] = None,
        **kwargs,
    ):
        """
        Args:
            panorama: An instance of PanoramaConnector for API interaction.
            device_groups: A list of device groups to be analyzed.
            security_rules_by_dg: A dictionary of security rules by device group.
        """
        self.panorama = panorama
        self.device_groups = device_groups or []
        if security_rules_by_dg is not None:
            self.security_rules_by_dg = security_rules_by_dg
        else:
            self.security_rules_by_dg = self._load_security_rules_per_dg()

        self.rules_by_name_by_dg = {
            dg: {rule.name: rule for rule in rules}
            for dg, rules in self.security_rules_by_dg.items()
        }
        self.execution_results_by_dg: dict[str, ExecuteResults] = {}
        self.analysis_results_by_dg: dict[str, AnalysisResult] = {}

    def _load_security_rules_per_dg(self) -> dict[str, list["SecurityRule"]]:
        """Load security rules from Panorama for each device group separately."""
        rules_by_dg = {}
        for device_group in self.device_groups:
            rules_by_dg[device_group] = self._get_security_rules(device_group)
        return rules_by_dg

    def _get_security_rules(self, device_group: str) -> list["SecurityRule"]:
        pre_rules = self.panorama.get_security_rules(
            device_group=device_group, rulebase="pre"
        )
        post_rules = self.panorama.get_security_rules(
            device_group=device_group, rulebase="post"
        )
        return pre_rules + post_rules

    def execute(self) -> dict[str, ExecuteResults]:
        """Execute shadowing analysis for each device group separately."""
        results_by_dg = {}
        for dg, rules in self.security_rules_by_dg.items():
            results = {}
            for i, rule in enumerate(rules):
                output = {}
                for j in range(i):
                    preceding_rule = rules[j]
                    output[preceding_rule.name] = run_checks(
                        self.checks,
                        rule,
                        preceding_rule,
                    )
                results[rule.name] = output
            results_by_dg[dg] = results
        self.execution_results_by_dg = results_by_dg
        return results_by_dg

    def analyze(
        self, results_by_dg: dict[str, ExecuteResults]
    ) -> AnalysisResults:
        """Analyze shadowing results for each device group separately."""
        analysis_by_dg = {}
        for dg, results in results_by_dg.items():
            rules_by_name = self.rules_by_name_by_dg[dg]
            analysis_results = []
            for rule_name, rule_results in results.items():
                shadowing_rules = []
                for preceding_rule_name, checks_results in rule_results.items():
                    if all(
                        check_result[0]
                        for check_result in checks_results.values()
                    ):
                        shadowing_rules.append(
                            rules_by_name[preceding_rule_name]
                        )
                if shadowing_rules:
                    analysis_results.append(
                        (rules_by_name[rule_name], shadowing_rules)
                    )
            analysis_by_dg[dg] = analysis_results
        self.analysis_results_by_dg = analysis_by_dg
        return analysis_by_dg
