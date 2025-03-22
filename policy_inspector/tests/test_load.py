# ruff: noqa: N802
import pytest

from policy_inspector.load import load_from_file
from policy_inspector.models import (
    AddressGroup,
    AddressObject,
    SecurityRule,
)
from policy_inspector.tests.conftest import (
    get_example_address_groups_path,
    get_example_address_objects_path,
    get_example_security_rules_path,
)


@pytest.mark.parametrize(
    "model,filepath",
    [
        (SecurityRule, get_example_security_rules_path()),
        (AddressGroup, get_example_address_groups_path()),
        (AddressObject, get_example_address_objects_path()),
    ],
)
def test_load_from_file(model, filepath):
    items = load_from_file(model, filepath)
    assert all(isinstance(item, model) for item in items)
