# ruff: noqa: N802
from pathlib import Path

import rich
from load import load_json

from policy_inspector.models import (
    AddressGroup,
    AddressObject,
    SecurityRule,
)
from policy_inspector.resolve import resolve_rules_addresses
from policy_inspector.shadowing import SIMPLE_CHECKS, run_checks_on_rules

data_dir = Path(__file__).parent.parent / "example"
security_rules_data = load_json(data_dir / "securityrule.example1.json")
address_objects_data = load_json(data_dir / "addressobject.example1.json")
address_groups_data = load_json(data_dir / "addressgroup.example1.json")


def test_resolver():
    security_rules = SecurityRule.load_many(security_rules_data)
    address_objects = AddressObject.load_many(address_objects_data)
    address_groups = AddressGroup.load_many(address_groups_data)

    resolved_security_rules = resolve_rules_addresses(
        security_rules, address_objects, address_groups
    )
    for resolved_rule in resolved_security_rules:
        rich.print(resolved_rule)


def test_run_default_checks_on_rules():
    security_rules = SecurityRule.load_many(security_rules_data)
    checks_results = run_checks_on_rules(security_rules, SIMPLE_CHECKS)
    rich.print(checks_results)
    assert checks_results
