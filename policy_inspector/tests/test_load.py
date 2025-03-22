# ruff: noqa: N802
import pytest

from policy_inspector.load import get_example_file_path, load_from_file
from policy_inspector.models import (
    AddressGroup,
    AddressObject,
    SecurityRule,
)


@pytest.mark.parametrize(
    "model,example_id",
    [
        (SecurityRule, "1"),
        (AddressGroup, "1"),
        (AddressObject, "1"),
    ],
)
def test_load_from_file(model, example_id):
    file_path = get_example_file_path(model, example_id)
    items = load_from_file(model, file_path)
    assert all(isinstance(item, model) for item in items)
