# ruff: noqa: N802

import pytest

from policy_inspector.loader import Loader
from policy_inspector.model.address_group import AddressGroup
from policy_inspector.model.address_object import AddressObject
from policy_inspector.model.security_rule import SecurityRule
from policy_inspector.utils import get_example_file_path


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
    items = Loader.load_model(cls, file_path)
    assert all(isinstance(item, cls) for item in items)


@pytest.fixture
def temp_address_objects_and_count(tmp_path):
    rows = 15000
    file_path = tmp_path / "address_objects_large.csv"
    addr_types = [
        ("IP Address", "10.0.0.1"),
        ("IP Range", "10.0.0.1-10.0.0.100"),
        ("FQDN", "internal.net.com"),
    ]
    with open(file_path, mode="w+") as f:
        f.write('"Name","Type","Address","Tags"\r')
        for i in range(rows):
            for addr_type, addr_value in addr_types:
                f.write(f'"ObjName_{i}","{addr_type}","{addr_value}","t1;t2"\r')
        return file_path, rows * 3


@pytest.fixture
def temp_address_groups_and_count(tmp_path):
    rows = 50000
    members = 50
    file_path = tmp_path / "address_groups_large.csv"
    with open(file_path, mode="w+") as f:
        f.write('"Name","Addresses","Tags"\r')
        for i in range(rows):
            addresses = ";".join([f"Mmbmr_{i}" for i in range(members)])
            f.write(f'"ObjGrp_{i}","{addresses}","t1;t2"\r')
        return file_path, rows


def test_load_large_csv_address_object(temp_address_objects_and_count):
    temp_address_objects, count = temp_address_objects_and_count
    models = Loader.load_model(AddressObject, temp_address_objects)
    count = len(models)
    assert count == count


def test_load_large_csv_address_group(temp_address_groups_and_count):
    temp_address_groups, count = temp_address_groups_and_count
    models = Loader.load_model(AddressGroup, temp_address_groups)
    count = len(models)
    assert count == count
