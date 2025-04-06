from ipaddress import IPv4Network

import pytest

from policy_inspector.model.address_group import AddressGroup
from policy_inspector.model.address_object import AddressObjectIPNetwork
from policy_inspector.resolver import AddressResolver


@pytest.fixture
def address_objects_ipnetwork():
    return [
        AddressObjectIPNetwork(name="web1", value="192.168.1.1/32"),
        AddressObjectIPNetwork(name="web2", value="192.168.1.2/32"),
        AddressObjectIPNetwork(name="web3", value="222.222.222.222/32"),
        AddressObjectIPNetwork(name="web4_TEMP", value="10.10.1.10/32"),
    ]


@pytest.fixture
def address_groups():
    return [
        AddressGroup(name="web-servers", static={"web1", "web2"}),
        AddressGroup(name="nested-group", static={"web-servers", "web4_TEMP"}),
    ]


@pytest.fixture
def objects_and_groups(address_objects_ipnetwork, address_groups):
    return address_objects_ipnetwork, address_groups


def test_resolve_address_object(address_objects_ipnetwork):
    resolver = AddressResolver(address_objects_ipnetwork, [])
    result = resolver.resolve({"web1"})
    assert result == {IPv4Network("192.168.1.1/32")}


def test_undefined_reference(address_objects_ipnetwork):
    resolver = AddressResolver(address_objects_ipnetwork, [])
    with pytest.raises(ValueError) as excinfo:
        resolver.resolve({"undefined"})
    assert "Unknown address object/group: undefined" in str(excinfo.value)


def test_resolve_address_group(objects_and_groups):
    resolver = AddressResolver(*objects_and_groups)
    result = resolver.resolve({"web-servers"})
    assert result == {
        IPv4Network("192.168.1.1/32"),
        IPv4Network("192.168.1.2/32"),
    }


def test_resolve_nested_address_group(objects_and_groups):
    resolver = AddressResolver(*objects_and_groups)
    result = resolver.resolve({"nested-group"})
    assert result == {
        IPv4Network("192.168.1.1/32"),
        IPv4Network("192.168.1.2/32"),
        IPv4Network("10.10.1.10/32"),
    }


def test_circular_dependency():
    groups = [
        AddressGroup(name="groupA", static={"groupB"}),
        AddressGroup(name="groupB", static={"groupA"}),
    ]
    resolver = AddressResolver([], groups)

    with pytest.raises(RecursionError) as excinfo:
        resolver.resolve({"groupA"})
    assert "maximum recursion depth" in str(excinfo.value)


def test_cache_usage(address_objects_ipnetwork, address_groups):
    resolver = AddressResolver(address_objects_ipnetwork, address_groups)
    resolver.resolve({"web-servers"})
    assert "web-servers" in resolver.cache
    assert len(resolver.cache["web-servers"]) == 2


def test_complex_hierarchy():
    objects = [
        AddressObjectIPNetwork(name="db1", value="10.0.0.5/32"),
        AddressObjectIPNetwork(name="db2", value="10.0.0.6/32"),
        AddressObjectIPNetwork(name="web1", value="192.168.1.1/32"),
        AddressObjectIPNetwork(name="web2", value="192.168.1.2/32"),
    ]
    groups = [
        AddressGroup(name="databases", static={"db1", "db2"}),
        AddressGroup(name="app-tier", static={"web-servers", "databases"}),
        AddressGroup(name="web-servers", static={"web1", "web2"}),
    ]

    resolver = AddressResolver(objects, groups)
    result = resolver.resolve({"app-tier"})
    assert result == {
        IPv4Network("10.0.0.5/32"),
        IPv4Network("10.0.0.6/32"),
        IPv4Network("192.168.1.1/32"),
        IPv4Network("192.168.1.2/32"),
    }


def test_empty_resolution():
    resolver = AddressResolver([], [])
    resolved = resolver.resolve(set())
    assert resolved == set()


def test_duplicate_entries(address_objects_ipnetwork):
    groups = [
        AddressGroup(name="dupes", static={"web1"}),
    ]
    resolver = AddressResolver(address_objects_ipnetwork, groups)
    result = resolver.resolve({"dupes"})
    assert len(result) == 1
