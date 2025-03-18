# ruff: noqa: N802

import pytest

from rules_check.models import (
    AddressGroup,
    AddressObject,
    SecurityRule,
)
from rules_check.tests.conftest import (
    get_example_address_groups_path,
    get_example_address_objects_path,
    get_example_security_rules_path,
)
from rules_check.utils import load_json

security_rules_data = load_json(get_example_security_rules_path())
address_objects_data = load_json(get_example_address_objects_path())
address_groups_data = load_json(get_example_address_groups_path())


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
