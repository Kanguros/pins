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


class AdvancedShadowing(Shadowing):
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
        panorama: "PanoramaConnector",
        device_groups: list[str],
        **kwargs
    ):
        super().__init__(panorama=panorama, device_groups=device_groups, **kwargs)
        # For each device group, load address objects/groups and resolve rules
        self.address_objects_by_dg = self._load_address_objects_per_dg()
        self.address_groups_by_dg = self._load_address_groups_per_dg()
        self.resolvers_by_dg = {
            dg: self.resolver_cls(self.address_objects_by_dg[dg], self.address_groups_by_dg[dg])
            for dg in self.device_groups
        }
        self._resolve_rules_per_dg()
        self.rules_by_name_by_dg = {
            dg: {rule.name: rule for rule in rules}
            for dg, rules in self.security_rules_by_dg.items()
        }

    def _load_address_objects_per_dg(self) -> dict[str, list["AddressObject"]]:
        objs_by_dg = {}
        for device_group in self.device_groups:
            objs_by_dg[device_group] = self.panorama.get_address_objects(device_group=device_group)
        return objs_by_dg

    def _load_address_groups_per_dg(self) -> dict[str, list["AddressGroup"]]:
        grps_by_dg = {}
        for device_group in self.device_groups:
            grps_by_dg[device_group] = self.panorama.get_address_groups(device_group=device_group)
        return grps_by_dg

    def _resolve_rules_per_dg(self):
        logger.info("↺ Resolving Address Groups and Address Objects per device group")
        for dg, rules in self.security_rules_by_dg.items():
            resolver = self.resolvers_by_dg[dg]
            resolved = [self._resolve_rule(rule, resolver) for rule in rules]
            self.security_rules_by_dg[dg] = resolved

    def _resolve_rule(self, rule: "SecurityRule", resolver) -> AdvancedSecurityRule:
        params = {}
        src_addrs = rule.source_addresses
        if src_addrs and AnyObj not in src_addrs:
            params["resolved_source_addresses"] = resolver.resolve(src_addrs)
        dst_addrs = rule.destination_addresses
        if dst_addrs and AnyObj not in dst_addrs:
            params["resolved_destination_addresses"] = resolver.resolve(dst_addrs)
        return AdvancedSecurityRule.from_security_rule(rule, **params)
