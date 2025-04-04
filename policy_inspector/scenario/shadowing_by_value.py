import logging
from typing import TYPE_CHECKING

from policy_inspector.models import AnyObj
from policy_inspector.resolver import AddressResolver
from policy_inspector.scenario.shadowing import (
    CheckResult,
    Shadowing,
    ShadowingCheckFunction,
    check_action,
    check_application,
    check_destination_zone,
    check_services,
    check_source_zone,
)

from .shadowing import PrecedingRulesOutputs

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
    if rule.destination_addresses == preceding_rule.destination_addresses:
        return True, "Source addresses are the same"

    if AnyObj in preceding_rule.destination_addresses:
        return True, "Preceding rule allows any source address"

    if AnyObj in rule.destination_addresses:
        return False, "Rule not covered due to 'any' source"

    for addr in rule.destination_addresses_ip:
        if not any(
            addr.subnet_of(net)
            for net in preceding_rule.destination_addresses_ip
        ):
            return (
                False,
                f"Source ip address {addr} is not covered by preceding rule",
            )

    return True, "Preceding rule covers all source ip addresses"


class ShadowingByValue(Shadowing):
    name = "Shadowing with addresses"
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
        address_objects: list["AddressObject"],
        address_groups: list["AddressGroup"],
        lookup_class: type = AddressResolver,
    ):
        self.address_objects = address_objects
        self.address_groups = address_groups
        self.resolver = lookup_class(address_objects, address_groups)
        super().__init__(security_rules)

    def execute(self) -> dict[str, PrecedingRulesOutputs]:
        self.resolve_addresses()
        return super().execute()

    def resolve_addresses(
        self,
    ) -> None:
        """Resolve Security Rules ``source_addresses`` and ``destination_addresses`` values
        of Address Objects and Address Groups to an actual IP addresses.
        """
        logger.info(
            "↺ Resolving Address Groups and Address Objects actual IP addresses"
        )
        errors = []
        attr_pairs = (
            ("source_addresses", "source_addresses_ip"),
            ("destination_addresses", "destination_addresses_ip"),
        )
        for rule in self.security_rules:
            for origin_attr, desire_attr in attr_pairs:
                current_value = getattr(rule, origin_attr)
                if not current_value or AnyObj in current_value:
                    continue
                try:
                    resolved_value = self.resolver.resolve(current_value)
                    if resolved_value:
                        setattr(rule, desire_attr, resolved_value)
                except ValueError as ex:
                    logger.debug(ex)
                    errors.append(
                        f"rule={rule.name} {origin_attr}={current_value}"
                    )

        if errors:
            raise ValueError(
                f"Failed to resolve rules addresses: {' | '.join(errors)}",
            )
