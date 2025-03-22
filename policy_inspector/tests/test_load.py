# ruff: noqa: N802
import pytest

from policy_inspector.load import load_from_file, get_example_file_path
from policy_inspector.models import (
    AddressGroup,
    AddressObject,
    SecurityRule,
)


@pytest.mark.parametrize(
    "model,example_name",
    [
        (SecurityRule, "example1"),
        (AddressGroup, "example1"),
        (AddressObject, "example1"),
    ],
)
def test_load_from_file(model, example_name):
    file_path = get_example_file_path(model, example_name)
    items = load_from_file(model, file_path)
    assert all(isinstance(item, model) for item in items)
