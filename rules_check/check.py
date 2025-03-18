import logging
from typing import Any, Callable, Union

from rules_check.models import AnyObj, SecurityRule

CheckOutput = tuple[Union[None, bool], str]
"""Return data format of a ``RuleCheckFunction``.

1. Status ``Union[None, bool]`` - Whether the rules pair fulfill a check.
2. Message ``str`` - Verbose message.
"""

RuleCheckFunction = Callable[[SecurityRule, SecurityRule], CheckOutput]
"""Definition of typing for a check type of function."""

logger = logging.getLogger(__name__)


def check_action(
    rule: SecurityRule, preceding_rule: SecurityRule
) -> CheckOutput:
    """Check if the action is the same in both rules."""
    result = rule.action == preceding_rule.action
    message = "Actions match" if result else "Actions differ"
    return result, message


def check_source_zone(
    rule: SecurityRule, preceding_rule: SecurityRule
) -> CheckOutput:
    """Checks the source zones of the preceding rule."""
    if rule.source_zones == preceding_rule.source_zones:
        return True, "Source zones are the same"

    if preceding_rule.source_zones.issubset(rule.source_zones):
        return True, "Preceding rule source zones cover rule's source zones"

    if AnyObj in preceding_rule.source_zones:
        return True, "Preceding rule source zones is 'any'"

    return False, "Source zones differ"


def check_destination_zone(
    rule: SecurityRule, preceding_rule: SecurityRule
) -> CheckOutput:
    """Checks the destination zones of the preceding rule."""
    if rule.destination_zones == preceding_rule.destination_zones:
        return True, "Source zones are the same"

    if preceding_rule.destination_zones.issubset(rule.destination_zones):
        return True, "Preceding rule source zones cover rule's source zones"

    if AnyObj in preceding_rule.destination_zones:
        return True, "Preceding rule source zones is 'any'"

    return False, "Source zones differ"


def check_source_address(
    rule: SecurityRule, preceding_rule: SecurityRule
) -> CheckOutput:
    """Checks the source addresses of the preceding rule's addresses."""
    if AnyObj in preceding_rule.source_addresses:
        return True, "Preceding rule allows any source address"

    if rule.source_addresses == preceding_rule.source_addresses:
        return True, "Source addresses are the same"

    if preceding_rule.source_addresses.issubset(rule.source_addresses):
        return (
            True,
            "Preceding rule source addresses cover rule's source addresses",
        )

    return False, "Source addresses not covered at all"


def check_destination_address(
    rule: SecurityRule, preceding_rule: SecurityRule
) -> CheckOutput:
    """Checks if the destination addresses are
    identical, allow any, or are subsets of the preceding rule's addresses."""
    if AnyObj in preceding_rule.destination_addresses:
        return True, "Preceding rule allows any destination address"

    if rule.source_addresses == preceding_rule.destination_addresses:
        return True, "Destination addresses are the same"

    if preceding_rule.destination_addresses.issubset(
        rule.destination_addresses
    ):
        return (
            True,
            "Preceding rule destination addresses cover rule's source addresses",
        )

    return False, "Destination addresses not covered at all"


def check_application(
    rule: SecurityRule, preceding_rule: SecurityRule
) -> CheckOutput:
    """Checks the applications of the preceding rule."""
    rule_apps = rule.applications
    preceding_apps = preceding_rule.applications

    if AnyObj in preceding_apps:
        return True, "Preceding rule allows any application"

    if AnyObj in rule_apps:
        return "any" in preceding_apps, "Rule allows any application"

    if all(rule_app in preceding_apps for rule_app in rule_apps):
        return True, "Preceding rule contains rule's applications"

    return False, "Preceding rule does not contain all rule's applications"


def check_services(
    rule: SecurityRule, preceding_rule: SecurityRule
) -> CheckOutput:
    """Checks if the rule's ports are the same
    or a subset of the preceding rule's ports."""
    if rule.services == preceding_rule.services:
        return True, "Preceding rule and rule's services are the same"

    if all(service in preceding_rule.services for service in rule.services):
        return True, "Preceding rule contains rule's applications"

    return False, "Preceding rule does not contain all rule's applications"


SIMPLE_CHECKS: list[RuleCheckFunction] = [
    check_action,
    check_application,
    check_services,
    check_source_zone,
    check_destination_zone,
    check_source_address,
    check_destination_address,
]


def check_services_and_application(
    rule: SecurityRule, preceding_rule: SecurityRule
) -> CheckOutput:
    pass


def check_source_addresses_by_ip(
    rule: SecurityRule, preceding_rule: SecurityRule
) -> CheckOutput:
    for addr in rule.source_addresses_ip:
        if not any(
            addr.subnet_of(net) for net in preceding_rule.source_addresses_ip
        ):
            return (
                False,
                f"Source ip address {addr} is not covered by preceding rule",
            )

    return True, "Preceding rule covers all source ip addresses"


def check_destination_addresses_by_ip(
    rule: SecurityRule, preceding_rule: SecurityRule
) -> CheckOutput:
    for addr in rule.destination_addresses_ip:
        if not any(
            addr.subnet_of(net)
            for net in preceding_rule.destination_addresses_ip
        ):
            return (
                False,
                f"Destination ip address {addr} is not covered by preceding rule",
            )

    return True, "Preceding rule covers all destination ip addresses"


COMPLEX_CHECKS: list[RuleCheckFunction] = [
    check_action,
    check_application,
    check_services,
    check_source_zone,
    check_destination_zone,
    check_source_addresses_by_ip,
    check_destination_addresses_by_ip,
]

ChecksOutputs = dict[str, CheckOutput]
"""Dict with checks function name as keys and its output as value."""

PrecedingRulesOutputs = dict[str, ChecksOutputs]
"""Dict with Preceding Rule's name as keys and ChecksOutputs as its value."""

RulesChecksResults = dict[str, PrecedingRulesOutputs]


def run_checks_on_rules(
    rules: list[SecurityRule], checks: list[RuleCheckFunction]
) -> RulesChecksResults:
    results = {}
    rules_count = len(rules)

    for i, rule in enumerate(rules):
        cid = f"[{i + 1}/{rules_count}][{rule.name}]"
        logger.info(f"{cid} Checking rule against {i} preceding Rules")

        output = {}
        for j in range(i):
            preceding_rule = rules[j]
            output[preceding_rule.name] = run_checks(
                checks, rule, preceding_rule
            )

        logger.info(f"{cid} Checking rule finished.")
        results[rule.name] = output

    logger.info("Shadowed rules detection complete")
    return results


def run_checks(
    checks: list[RuleCheckFunction], *rules: SecurityRule
) -> dict[str, Any]:
    results = {}
    for check in checks:
        try:
            results[check.__name__] = check(*rules)
        except Exception as ex:  # noqa: BLE001
            logger.exception(f"Error occur during running {check}. {ex}")  # noqa: TRY401
    return results
