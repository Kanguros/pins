# ruff: noqa: N802
from pathlib import Path

import rich

from rules_check.check import SIMPLE_CHECKS, run_checks_on_rules
from rules_check.models import (
    AddressGroup,
    AddressObject,
    SecurityRule,
)
from rules_check.resolve import resolve_rules_addresses
from rules_check.utils import load_json

data_dir = Path(__file__).parent.parent / "data"
security_rules_data = load_json(data_dir / "security_rules.json")
address_objects_data = load_json(data_dir / "address_objects.json")
address_groups_data = load_json(data_dir / "address_groups.json")


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
