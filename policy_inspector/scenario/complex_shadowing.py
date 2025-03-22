import logging
from typing import TYPE_CHECKING

from policy_inspector.resolve import resolve_rules_addresses
from policy_inspector.scenario.shadowing import (
    CheckOutput,
    ShadowingCheckFunction,
    ShadowingScenario,
    check_action,
    check_application,
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
    rule: "SecurityRule", preceding_rule: "SecurityRule"
) -> CheckOutput:
    pass


def check_source_addresses_by_ip(
    rule: "SecurityRule", preceding_rule: "SecurityRule"
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
    rule: "SecurityRule", preceding_rule: "SecurityRule"
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


class ComplexShadowing(ShadowingScenario):
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
            security_rules, address_objects, address_groups
        )
        self.security_rules = security_rules
