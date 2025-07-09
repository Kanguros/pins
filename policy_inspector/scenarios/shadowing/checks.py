import logging
from typing import TYPE_CHECKING, Callable

from policy_inspector.model.base import AnyObj

if TYPE_CHECKING:
    from policy_inspector.model.security_rule import SecurityRule

logger = logging.getLogger(__name__)


CheckResult = tuple[bool, str]
"""
A tuple representing the result of a check function.

1. ``bool``: Indicates whether the check was fulfilled or not.
2. ``str``: A verbose message describing the result.
"""

CheckFunction = Callable[["SecurityRule", "SecurityRule"], CheckResult]
"""A callable type definition for a scenario check function."""


def check_action(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """
    Checks if both rules have the same action (like 'allow' or 'deny').
    If the actions are different, the first rule does not fully hide the second one.
    """
    result = rule.action == preceding_rule.action
    message = "Actions match" if result else "Actions differ"
    return result, message


def check_source_zone(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """
    Checks if the first rule covers all the same source zones as the second rule.
    If the first rule uses 'any' or all the same zones, it can hide the second rule.
    """
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
    """
    Checks if the first rule covers all the same destination zones as the second rule.
    If the first rule uses 'any' or all the same zones, it can hide the second rule.
    """
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
    """
    Checks if the first rule covers all the same source addresses (like IPs or groups).
    If the first rule uses 'any' or all the same addresses, it can hide the second rule.
    """
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
    """
    Checks if the first rule covers all the same destination addresses.
    If the first rule uses 'any' or all the same addresses, it can hide the second rule.
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
    """
    Checks if the first rule allows all the same applications as the second rule.
    If the first rule uses 'any' or all the same apps, it can hide the second rule.
    """
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
    """
    Checks if the first rule allows all the same network services or ports.
    If the first rule covers all the same services, it can hide the second rule.
    """
    if rule.services == preceding_rule.services:
        return True, "Preceding rule and rule's services are the same"

    if all(service in preceding_rule.services for service in rule.services):
        return True, "Preceding rule contains rule's applications"

    return False, "Preceding rule does not contain all rule's applications"
