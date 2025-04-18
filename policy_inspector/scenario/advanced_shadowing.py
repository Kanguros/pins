import logging
from typing import TYPE_CHECKING

from policy_inspector.model.address_object import AddressObjectFQDN
from policy_inspector.model.base import AnyObj
from policy_inspector.model.security_rule import (
    AdvancedSecurityRule,
    SecurityRule,
)
from policy_inspector.resolver import Resolver
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

if TYPE_CHECKING:
    from policy_inspector.model.address_group import AddressGroup
    from policy_inspector.model.address_object import AddressObject


logger = logging.getLogger(__name__)


def check_services_and_application(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    pass


def check_source_addresses_by_ip(
    rule: "AdvancedSecurityRule",
    preceding_rule: "AdvancedSecurityRule",
) -> CheckResult:
    """Check if rule's source IP addresses are covered by preceding rule.

    Excludes FQDN address objects from comparison and logs warnings when encountered.
    """
    if rule.source_addresses == preceding_rule.source_addresses:
        return True, "Destination addresses are identical"

    if AnyObj in preceding_rule.source_addresses:
        return True, "Preceding rule allows any destination"

    if AnyObj in rule.source_addresses:
        return False, "Current rule allows any destination (too broad)"

    fqdn_count = 0
    for addr_obj in rule.resolved_source_addresses:
        if isinstance(addr_obj, AddressObjectFQDN):
            logger.debug(
                f"Skipping FQDN comparison for {addr_obj.name}={addr_obj.value}"
            )
            fqdn_count += 1
            continue

        if not any(
            addr_obj.is_covered_by(preceding_addr_obj)
            for preceding_addr_obj in preceding_rule.resolved_source_addresses
            if not isinstance(preceding_addr_obj, AddressObjectFQDN)
        ):
            return (
                False,
                f"Destination {addr_obj.name} ({addr_obj.value}) not covered by preceding rule",
            )

    if fqdn_count == len(rule.resolved_source_addresses):
        logger.debug("All destination addresses are FQDNs - comparison skipped")
        return True, "FQDN destinations excluded from coverage check"

    return (
        True,
        "All non-FQDN destination addresses are covered by preceding rule(s)",
    )


def check_destination_addresses_by_ip(
    rule: "AdvancedSecurityRule",
    preceding_rule: "AdvancedSecurityRule",
) -> CheckResult:
    """Check if rule's destination IP addresses are covered by preceding rule.

    Excludes FQDN address objects from comparison and logs warnings when encountered.
    """
    if rule.destination_addresses == preceding_rule.destination_addresses:
        return True, "Destination addresses are identical"

    if AnyObj in preceding_rule.destination_addresses:
        return True, "Preceding rule allows any destination"

    if AnyObj in rule.destination_addresses:
        return False, "Current rule allows any destination (too broad)"

    fqdn_count = 0
    for addr_obj in rule.resolved_destination_addresses:
        if isinstance(addr_obj, AddressObjectFQDN):
            logger.debug(
                f"Skipping FQDN comparison for {addr_obj.name}={addr_obj.value}"
            )
            fqdn_count += 1
            continue

        if not any(
            addr_obj.is_covered_by(preceding_addr_obj)
            for preceding_addr_obj in preceding_rule.resolved_destination_addresses
            if not isinstance(preceding_addr_obj, AddressObjectFQDN)
        ):
            return (
                False,
                f"Destination {addr_obj.name} ({addr_obj.value}) not covered by preceding rule",
            )

    # Handle case where all addresses were FQDNs
    if fqdn_count == len(rule.resolved_destination_addresses):
        logger.debug("All destination addresses are FQDNs - comparison skipped")
        return True, "FQDN destinations excluded from coverage check"

    return (
        True,
        "All non-FQDN destination addresses are covered by preceding rule(s)",
    )


class ShadowingByValue(Shadowing):
    name = "Advanced Shadowing"
    checks: list[ShadowingCheckFunction] = [
        check_action,
        check_application,
        check_services,
        check_source_zone,
        check_destination_zone,
        check_source_addresses_by_ip,
        check_destination_addresses_by_ip,
    ]
    resolver_cls: type[Resolver] = Resolver

    def __init__(
        self,
        security_rules: list["SecurityRule"],
        address_objects: list["AddressObject"],
        address_groups: list["AddressGroup"],
    ):
        self.security_rules = security_rules
        self.address_objects = address_objects
        self.address_groups = address_groups
        self.resolver = self.resolver_cls(address_objects, address_groups)
        self.resolve_rules()
        self.rules_by_name = {rule.name: rule for rule in self.security_rules}


    def resolve_rules(self):
        resolved = []
        logger.info("↺ Resolving Address Groups and Address Objects")
        for security_rule in self.security_rules:
            resolved.append(self.resolve_rule(security_rule))
        self.security_rules = resolved

    def resolve_rule(self, rule: "SecurityRule") -> AdvancedSecurityRule:
        params = {}
        src_addrs = rule.source_addresses
        if src_addrs and AnyObj not in src_addrs:
            params["resolved_source_addresses"] = self.resolver.resolve(
                src_addrs
            )

        dst_addrs = rule.destination_addresses
        if dst_addrs and AnyObj not in dst_addrs:
            params["resolved_destination_addresses"] = self.resolver.resolve(
                dst_addrs
            )
        return AdvancedSecurityRule.from_security_rule(rule, **params)
