# ruff: noqa: N802
import pytest

from policy_inspector.loader import FileHandler
from policy_inspector.models import (
    AddressGroup,
    AddressObject,
    SecurityRule,
)
from policy_inspector.utils import get_example_file_path


@pytest.fixture(
    params=[
        (SecurityRule, "1/policies.json"),
        (AddressGroup, "1/addressgroup.json"),
        (AddressObject, "1/addressobject.json"),
        (SecurityRule, "2/policies.json"),
    ]
)
def model_with_path(request):
    cls, file_path = request.param
    return cls, get_example_file_path(file_path)


def test_load_from_file(model_with_path):
    cls, file_path = model_with_path
    items = FileHandler.load_for_model(cls, file_path)
    assert all(isinstance(item, cls) for item in items)
