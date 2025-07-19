import logging

from policy_inspector.model.address_object import AddressObjectFQDN
from policy_inspector.model.base import AnyObj
from policy_inspector.model.security_rule import AdvancedSecurityRule
from policy_inspector.resolver import Resolver
from policy_inspector.scenarios.shadowing.scenario import (
    CheckFunction,
    CheckResult,
    Shadowing,
    check_action,
    check_application,
    check_destination_zone,
    check_services,
    check_source_zone,
    run_checks,
)

logger = logging.getLogger(__name__)


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

    def __init__(
        self,
        panorama=None,
        device_groups=None,
        **kwargs,
    ):
        super().__init__(
            panorama=panorama,
            device_groups=device_groups,
            **kwargs,
        )
        self.address_objects_by_dg = {}
        self.address_groups_by_dg = {}
        # Store test-provided address objects/groups for merging logic
        self._address_objects_by_dg = kwargs.get("address_objects_by_dg")
        self._address_groups_by_dg = kwargs.get("address_groups_by_dg")

    def prepare_address_objects_and_groups(self):
        """Prepare address objects/groups from scenario attributes if present."""
        address_objects_by_dg = getattr(self, "_address_objects_by_dg", None)
        address_groups_by_dg = getattr(self, "_address_groups_by_dg", None)
        self.address_objects_by_dg = {}
        self.address_groups_by_dg = {}
        address_objects_by_dg = address_objects_by_dg or {}
        address_groups_by_dg = address_groups_by_dg or {}
        shared_objects = address_objects_by_dg.get("shared", [])
        shared_groups = address_groups_by_dg.get("shared", [])

        def to_obj_dict(objs):
            if isinstance(objs, dict):
                return objs
            return {obj.name: obj for obj in objs}

        for dg in self.device_groups:
            dg_objects = address_objects_by_dg.get(dg, [])
            dg_groups = address_groups_by_dg.get(dg, [])
            all_objects = list(shared_objects) + list(dg_objects)
            self.address_objects_by_dg[dg] = to_obj_dict(all_objects)
            self.address_groups_by_dg[dg] = list(shared_groups) + list(
                dg_groups
            )

    def execute(self) -> dict[str, dict[str, dict[str, CheckResult]]]:
        logger.info(
            "↺ Resolving Address Groups and Address Objects per device group"
        )
        self.prepare_address_objects_and_groups()
        for dg in self.device_groups:
            address_objects_dict = self.address_objects_by_dg.get(dg, {})
            address_objects_list = list(address_objects_dict.values())
            resolver = Resolver(
                address_objects=address_objects_list,
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

        # Custom execute logic to use self.checks
        results_by_dg = {}
        for dg, rules in self.security_rules_by_dg.items():
            results = {}
            for i, rule in enumerate(rules):
                output = {}
                for j in range(i):
                    preceding_rule = rules[j]
                    output[preceding_rule.name] = run_checks(
                        self.checks, rule, preceding_rule
                    )
                results[rule.name] = output
            results_by_dg[dg] = results
        self.execution_results_by_dg = results_by_dg
        return results_by_dg
