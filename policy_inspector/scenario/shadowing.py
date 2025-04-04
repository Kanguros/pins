import logging
from typing import TYPE_CHECKING, Callable

from policy_inspector.models import AnyObj
from policy_inspector.scenario.base import CheckResult, Scenario

if TYPE_CHECKING:
    from policy_inspector.models import SecurityRule

logger = logging.getLogger(__name__)

ShadowingCheckFunction = Callable[["SecurityRule", "SecurityRule"], CheckResult]

ChecksOutputs = dict[str, CheckResult]
"""Dict with check's name as keys and its output as value."""

PrecedingRulesOutputs = dict[str, ChecksOutputs]
"""Dict with Preceding Rule's name as keys and ChecksOutputs as its value."""


def check_action(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """Check if the action is the same in both rules."""
    result = rule.action == preceding_rule.action
    message = "Actions match" if result else "Actions differ"
    return result, message


def check_source_zone(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """Checks the source zones of the preceding rule."""
    if rule.source_zones == preceding_rule.source_zones:
        return True, "Source zones are the same"

    if preceding_rule.source_zones.issubset(rule.source_zones):
        return True, "Preceding rule source zones cover rule's source zones"

    if AnyObj in preceding_rule.source_zones:
        return True, "Preceding rule source zones is 'any'"

    return False, "Source zones differ"


def check_destination_zone(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """Checks the destination zones of the preceding rule."""
    if rule.destination_zones == preceding_rule.destination_zones:
        return True, "Destination zones are the same"

    if rule.destination_zones.issubset(preceding_rule.destination_zones):
        return (
            True,
            "Preceding rule destination zones cover rule's destination zones",
        )

    if AnyObj in preceding_rule.destination_zones:
        return True, "Preceding rule destination zones is 'any'"

    return False, "Destination zones differ"


def check_source_address(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """Checks the source addresses of the preceding rule's addresses."""
    if rule.source_addresses == preceding_rule.source_addresses:
        return True, "Source addresses are the same"

    if AnyObj in preceding_rule.source_addresses:
        return True, "Preceding rule allows any source address"

    if AnyObj in rule.source_addresses:
        return False, "Rule not covered due to 'any' source"

    if rule.source_addresses.issubset(preceding_rule.source_addresses):
        return (
            True,
            "Preceding rule source addresses cover rule's source addresses",
        )

    return False, "Source addresses not covered at all"


def check_destination_address(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """Checks if the destination addresses are
    identical, allow any, or are subsets of the preceding rule's addresses.
    """
    if AnyObj in preceding_rule.destination_addresses:
        return True, "Preceding rule allows any destination address"

    if rule.destination_addresses == preceding_rule.destination_addresses:
        return True, "Destination addresses are the same"

    if rule.destination_addresses.issubset(
        preceding_rule.destination_addresses,
    ):
        return (
            True,
            "Preceding rule destination addresses cover rule's destination addresses",
        )

    return False, "Destination addresses not covered at all"


def check_application(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """Checks the applications of the preceding rule."""
    rule_apps = rule.applications
    preceding_apps = preceding_rule.applications

    if rule_apps == preceding_apps:
        return True, "The same applications"

    if AnyObj in preceding_apps:
        return True, "Preceding rule allows any application"

    if rule_apps.issubset(preceding_apps):
        return True, "Preceding rule contains rule's applications"

    return False, "Rule doesn't cover"


def check_services(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """Checks if the rule's ports are the same
    or a subset of the preceding rule's ports.
    """
    if rule.services == preceding_rule.services:
        return True, "Preceding rule and rule's services are the same"

    if all(service in preceding_rule.services for service in rule.services):
        return True, "Preceding rule contains rule's applications"

    return False, "Preceding rule does not contain all rule's applications"


class Shadowing(Scenario):
    """
    This scenario identifies when a rule is completely shadowed by a
    preceding rule. Shadowing occurs when a rule will never be matched
    because a rule earlier in the processing order would always match
    first.
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

    def __init__(self, security_rules: list["SecurityRule"]):
        self.security_rules = security_rules

    def execute(self) -> dict[str, PrecedingRulesOutputs]:
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
        return results

    def analyze(
        self,
        results: dict[str, PrecedingRulesOutputs],
    ):
        for rule_name, rule_results in results.items():
            shadowing_rules = []
            for preceding_rule_name, checks_results in rule_results.items():
                if all(
                    check_result[0] for check_result in checks_results.values()
                ):
                    shadowing_rules.append(preceding_rule_name)

            if shadowing_rules:
                logger.info(f"✖ '{rule_name}' shadowed by:")
                for rule in shadowing_rules:
                    logger.info(f"   • {rule}")
            else:
                logger.debug(f"✔ '{rule_name}' not shadowed")
