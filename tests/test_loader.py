# ruff: noqa: N802

import pytest

from policy_inspector.loader import Loader
from policy_inspector.models import (
    AddressGroup,
    AddressObject,
    SecurityRule,
)
from policy_inspector.utils import get_example_file_path


@pytest.fixture(
    params=[
        (SecurityRule, "1/policies.json"),
        (AddressGroup, "1/address_groups.json"),
        (AddressObject, "1/address_objects.json"),
        (SecurityRule, "2/policies.json"),
    ]
)
def model_with_path(request):
    cls, file_path = request.param
    return cls, get_example_file_path(file_path)


def test_load_from_file(model_with_path):
    cls, file_path = model_with_path
    items = Loader.load_model(cls, file_path)
    assert all(isinstance(item, cls) for item in items)


@pytest.fixture
def temp_address_objects(tmp_path):
    rows = 50000
    file_path = tmp_path / "address_objects_large.csv"
    with open(file_path, mode="w+") as f:
        f.write('"Name","Address","Tags"\r')
        for i in range(rows):
            f.write(f'"ObjName_{i}","8.8.8.8","t1;t2"\r')
        return file_path


@pytest.fixture
def temp_address_groups(tmp_path):
    rows = 50000
    members = 50
    file_path = tmp_path / "address_groups_large.csv"
    with open(file_path, mode="w+") as f:
        f.write('"Name","Addresses","Tags"\r')
        for i in range(rows):
            addresses = ";".join([f"Mmbmr_{i}" for i in range(members)])
            f.write(f'"ObjGrp_{i}","{addresses}","t1;t2"\r')
        return file_path


def test_load_large_csv_address_object(temp_address_objects):
    models = Loader.load_model(AddressObject, temp_address_objects)
    count = len(models)
    assert count == 50000


def test_load_large_csv_address_group(temp_address_groups):
    models = Loader.load_model(AddressGroup, temp_address_groups)
    count = len(models)
    assert count == 50000
