# ruff: noqa: N802
from pathlib import Path

import pytest

from rules_check.models import (
    AddressGroup,
    AddressObject,
    SecurityRule,
)
from rules_check.utils import load_json

data_dir = Path(__file__).parent / "data"
security_rules_data = load_json(data_dir / "security_rules.json")
address_objects_data = load_json(data_dir / "address_objects.json")
address_groups_data = load_json(data_dir / "address_groups.json")


@pytest.mark.parametrize("item", security_rules_data)
def test_security_rule_model(item):
    obj = SecurityRule(**item)
    assert isinstance(obj, SecurityRule)


@pytest.mark.parametrize("item", address_objects_data)
def test_address_object_model(item):
    obj = AddressObject(**item)
    assert isinstance(obj, AddressObject)


@pytest.mark.parametrize("item", address_groups_data)
def test_address_group_model(item):
    obj = AddressGroup(**item)
    assert isinstance(obj, AddressGroup)
