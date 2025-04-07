from ipaddress import IPv4Address, IPv4Network

import pytest

from policy_inspector.model.address_group import AddressGroup
from policy_inspector.model.address_object import (
    AddressObjectIPNetwork,
    AddressObjectIPRange,
)
from policy_inspector.resolver import AddressResolver


@pytest.fixture
def address_objects():
    return [
        AddressObjectIPNetwork(name="web1", value="192.168.1.1/32"),
        AddressObjectIPNetwork(name="web2", value="192.168.1.2/32"),
        AddressObjectIPNetwork(name="web3", value="222.222.222.222/32"),
        AddressObjectIPNetwork(name="web4_TEMP", value="10.10.1.10/32"),
        AddressObjectIPRange(name="web5", value="10.10.1.10-10.10.1.15"),
        AddressObjectIPNetwork(name="db1", value="10.0.0.5/32"),
        AddressObjectIPNetwork(name="db2", value="10.0.0.6/32"),
        AddressObjectIPNetwork(name="web1", value="192.168.1.1/32"),
        AddressObjectIPNetwork(name="web2", value="192.168.1.2/32"),
    ]


@pytest.fixture
def address_groups():
    return [
        AddressGroup(name="web-servers", static={"web1", "web2"}),
        AddressGroup(
            name="nested-group", static={"web-servers", "web4_TEMP", "web5"}
        ),
        AddressGroup(name="databases", static={"db1", "db2"}),
        AddressGroup(
            name="app-tier", static={"web-servers", "databases", "web5"}
        ),
    ]


@pytest.fixture
def objects_and_groups(address_objects, address_groups):
    return address_objects, address_groups


def test_resolve_address_object(address_objects):
    resolver = AddressResolver(address_objects, [])
    result = resolver.resolve({"web1"})
    desire_result = [
        AddressObjectIPNetwork(name="web1", value="192.168.1.1/32")
    ]
    assert all(obj in desire_result for obj in result)
    assert all(obj in result for obj in desire_result)


def test_resolve_address_group(objects_and_groups):
    resolver = AddressResolver(*objects_and_groups)
    result = resolver.resolve({"web-servers"})
    desire_result = [
        AddressObjectIPNetwork(name="web2", value="192.168.1.2/32"),
        AddressObjectIPNetwork(name="web1", value="192.168.1.1/32"),
    ]
    assert all(obj in desire_result for obj in result)
    assert all(obj in result for obj in desire_result)


def test_resolve_nested_address_group(objects_and_groups):
    resolver = AddressResolver(*objects_and_groups)
    result = resolver.resolve({"nested-group"})
    desire_result = [
        AddressObjectIPNetwork(
            name="web2",
            description="",
            tags=set(),
            value=IPv4Network("192.168.1.2/32"),
        ),
        AddressObjectIPNetwork(
            name="web1",
            description="",
            tags=set(),
            value=IPv4Network("192.168.1.1/32"),
        ),
        AddressObjectIPNetwork(
            name="web4_TEMP",
            description="",
            tags=set(),
            value=IPv4Network("10.10.1.10/32"),
        ),
        AddressObjectIPRange(
            name="web5",
            description="",
            tags=set(),
            value=(IPv4Address("10.10.1.10"), IPv4Address("10.10.1.15")),
        ),
    ]
    assert all(obj in desire_result for obj in result)
    assert all(obj in result for obj in desire_result)


def test_complex_hierarchy(objects_and_groups):
    resolver = AddressResolver(*objects_and_groups)
    result = resolver.resolve({"app-tier"})
    desire_result = [
        AddressObjectIPNetwork(name="web1", value="192.168.1.1/32"),
        AddressObjectIPNetwork(name="web2", value="192.168.1.2/32"),
        AddressObjectIPNetwork(name="db1", value="10.0.0.5/32"),
        AddressObjectIPNetwork(name="db2", value="10.0.0.6/32"),
        AddressObjectIPRange(name="web5", value="10.10.1.10-10.10.1.15"),
    ]
    assert all(obj in desire_result for obj in result)
    assert all(obj in result for obj in desire_result)


def test_undefined_reference(address_objects):
    resolver = AddressResolver(address_objects, [])
    with pytest.raises(ValueError) as excinfo:
        resolver.resolve({"undefined"})
    assert "Unknown address object/group: undefined" in str(excinfo.value)


def test_circular_dependency():
    groups = [
        AddressGroup(name="groupA", static={"groupB"}),
        AddressGroup(name="groupB", static={"groupA"}),
    ]
    resolver = AddressResolver([], groups)

    with pytest.raises(RecursionError) as excinfo:
        resolver.resolve({"groupA"})
    assert "maximum recursion depth" in str(excinfo.value)


def test_cache_usage(objects_and_groups):
    resolver = AddressResolver(*objects_and_groups)
    resolver.resolve({"web-servers"})
    assert "web-servers" in resolver.cache
    assert len(resolver.cache["web-servers"]) == 2


def test_empty_resolution():
    resolver = AddressResolver([], [])
    resolved = resolver.resolve(set())
    assert resolved == []


def test_duplicate_entries(address_objects):
    groups = [
        AddressGroup(name="dupes", static={"web1"}),
    ]
    resolver = AddressResolver(address_objects, groups)
    result = resolver.resolve({"dupes"})
    assert len(result) == 1
