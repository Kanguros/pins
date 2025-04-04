import logging
from typing import TYPE_CHECKING

from policy_inspector.models import AnyObj
from policy_inspector.resolve import resolve_rules_addresses
from policy_inspector.scenario.shadowing import (
    CheckResult,
    Shadowing,
    ShadowingCheckFunction,
    check_action,
    check_application,
    check_destination_address,
    check_destination_zone,
    check_services,
    check_source_zone,
)

if TYPE_CHECKING:
    from policy_inspector.models import (
        AddressGroup,
        AddressObject,
        SecurityRule,
    )

logger = logging.getLogger(__name__)


def check_services_and_application(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    pass


def check_source_addresses_by_ip(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    if rule.source_addresses == preceding_rule.source_addresses:
        return True, "Source addresses are the same"

    if AnyObj in preceding_rule.source_addresses:
        return True, "Preceding rule allows any source address"

    if AnyObj in rule.source_addresses:
        return False, "Rule not covered due to 'any' source"

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
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    check_by_name = check_destination_address(rule, preceding_rule)
    if check_by_name[0]:
        return check_by_name
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


class ShadowingByValue(Shadowing):
    checks: list[ShadowingCheckFunction] = [
        check_action,
        check_application,
        check_services,
        check_source_zone,
        check_destination_zone,
        check_source_addresses_by_ip,
        check_destination_addresses_by_ip,
    ]

    def __init__(
        self,
        security_rules: list["SecurityRule"],
        address_groups: list["AddressGroup"],
        address_objects: list["AddressObject"],
    ):
        security_rules = resolve_rules_addresses(
            security_rules,
            address_objects,
            address_groups,
        )
        super().__init__(security_rules)
