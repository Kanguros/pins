# ruff: noqa: N802

import pytest

from policy_inspector.loader import load_model, load_csv
from policy_inspector.model.address_group import AddressGroup
from policy_inspector.model.address_object import AddressObject
from policy_inspector.model.security_rule import SecurityRule
from policy_inspector.utils import get_example_file_path
from tests.conftest import gather_data_files


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
    items = load_model(cls, file_path)
    assert all(isinstance(item, cls) for item in items)


def test_large_csv_address_object(tmp_path):
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

    models = load_model(AddressObject, file_path)
    count = rows * 3
    model_counts = len(models)
    assert count == model_counts


def test_large_csv_address_group(tmp_path):
    rows = 50000
    members = 50
    file_path = tmp_path / "address_groups_large.csv"
    with open(file_path, mode="w+") as f:
        f.write('"Name","Addresses","Tags"\r')
        for i in range(rows):
            addresses = ";".join([f"Mmbmr_{i}" for i in range(members)])
            f.write(f'"ObjGrp_{i}","{addresses}","t1;t2"\r')

    models = load_model(AddressGroup, file_path)
    models_count = len(models)
    assert rows == models_count


INVALID_CSV = gather_data_files("invalid*.csv")


# @pytest.mark.parametrize("file_path", INVALID_CSV)
# def test_invalid_csv(file_path):
#     # with pytest.raises(Exception):
#     data = load_csv(file_path)
#     print(data)

VALID_CSV = gather_data_files("valid*.csv")

@pytest.mark.parametrize("file_path", VALID_CSV)
def test_valid_csv(file_path):
    data = load_csv(file_path)
    assert data