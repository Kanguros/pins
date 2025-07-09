# ruff: noqa: N802

import pytest

from policy_inspector.model.address_group import AddressGroup
from policy_inspector.model.address_object import AddressObject
from policy_inspector.model.security_rule import SecurityRule
from policy_inspector.utils import get_example_file_path, load_json


@pytest.mark.parametrize(
    "model_with_path",
    [
        (SecurityRule, "1/policies.json"),
        (SecurityRule, "2/policies.json"),
        (AddressGroup, "1/address_groups.json"),
        (AddressGroup, "2/address_groups.json"),
        (AddressObject, "1/address_objects.json"),
        (AddressObject, "2/address_objects.json"),
    ],
)
def test_load_from_example_file(model_with_path):
    cls, file_path = model_with_path
    file_path = get_example_file_path(file_path)
    file_data = load_json(file_path)
    items = cls.parse_json(file_data)
    assert all(isinstance(item, cls) for item in items)
