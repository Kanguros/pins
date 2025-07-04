import logging
from typing import TYPE_CHECKING

from policy_inspector.model.address_object import AddressObjectFQDN
from policy_inspector.model.base import AnyObj
from policy_inspector.model.security_rule import (
    AdvancedSecurityRule,
    SecurityRule,
)
from policy_inspector.resolver import Resolver
from policy_inspector.scenarios.shadowing.base import (
    CheckFunction,
    CheckResult,
    Shadowing,
    check_action,
    check_application,
    check_destination_zone,
    check_services,
    check_source_zone,
)

if TYPE_CHECKING:
    from policy_inspector.model.address_group import AddressGroup
    from policy_inspector.model.address_object import AddressObject
    from policy_inspector.panorama import PanoramaConnector


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
        return True, "Source addresses are identical"

    if AnyObj in preceding_rule.resolved_source_addresses:
        return True, "Preceding rule allows any source"

    if AnyObj in rule.resolved_source_addresses:
        return False, "Current rule allows any source (too broad)"

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
                f"Source {addr_obj.name} ({addr_obj.value}) not covered by preceding rule",
            )

    if fqdn_count == len(rule.resolved_source_addresses):
        logger.debug("All source addresses are FQDNs - comparison skipped")
        return True, "FQDN source addresses excluded from coverage check"

    return (
        True,
        "All non-FQDN source addresses are covered by preceding rule(s)",
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

    if AnyObj in preceding_rule.resolved_destination_addresses:
        return True, "Preceding rule allows any destination"

    if AnyObj in rule.resolved_destination_addresses:
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

    if fqdn_count == len(rule.resolved_destination_addresses):
        logger.debug("All destination addresses are FQDNs - comparison skipped")
        return True, "FQDN destinations excluded from coverage check"

    return (
        True,
        "All non-FQDN destination addresses are covered by preceding rule(s)",
    )


class AdvancedShadowing(Shadowing):
    """Advanced scenario for detecting shadowing rules with IP address resolution."""

    checks: list[CheckFunction] = [
                check_source_zone,
                check_destination_zone,
                check_source_addresses_by_ip,
                check_destination_addresses_by_ip,
                check_services,
                check_application,
                check_action,
            ]

    def execute(self) -> dict[str, dict[str, dict[str, CheckResult]]]:
        logger.info("↺ Resolving Address Groups and Address Objects per device group")
        for dg in self.device_groups:
            resolver = Resolver(
                address_objects=self.address_objects_by_dg.get(dg, []),
                address_groups=self.address_groups_by_dg.get(dg, []),
            )
            rules = self.security_rules_by_dg.get(dg, [])
            advanced_rules = []
            for rule in rules:
                advanced_rule = AdvancedSecurityRule(**rule.model_dump())
                advanced_rule.resolved_source_addresses = resolver.resolve(
                    rule.source_addresses
                )
                advanced_rule.resolved_destination_addresses = resolver.resolve(
                    rule.destination_addresses
                )
                advanced_rules.append(advanced_rule)
            self.security_rules_by_dg[dg] = advanced_rules

        return super().execute()
