from ipaddress import IPv4Address, IPv4Network

import pytest

from policy_inspector.model.address_object import (
    AddressObject,
    AddressObjectFQDN,
    AddressObjectIPNetwork,
    AddressObjectIPRange,
)


@pytest.mark.parametrize(
    "input_value",
    [
        "192.168.1.0/24",
        IPv4Network("192.168.1.0/24"),
    ],
)
def test_ip_network_creation(input_value):
    obj = AddressObjectIPNetwork(
        name="test-net",
        value=input_value,
        description="Test network",
        tags={"test"},
    )
    assert isinstance(obj.value, IPv4Network)
    assert obj.value == IPv4Network("192.168.1.0/24")


@pytest.mark.parametrize(
    "input_value",
    [
        ("10.0.0.1", "10.0.0.100"),
        "10.0.0.1-10.0.0.100",
        (IPv4Address("10.0.0.1"), IPv4Address("10.0.0.100")),
    ],
)
def test_ip_range_creation(input_value):
    obj = AddressObjectIPRange(
        name="test-range",
        value=input_value,
        tags={"critical"},
    )
    assert isinstance(obj.value[0], IPv4Address)
    assert isinstance(obj.value[1], IPv4Address)
    assert obj.value == (IPv4Address("10.0.0.1"), IPv4Address("10.0.0.100"))


def test_fqdn_creation_1():
    obj = AddressObjectFQDN(
        name="test-fqdn", value="example.com", description="Test domain"
    )
    assert obj.value == "example.com"


def test_fqdn_creation_2():
    obj = AddressObjectFQDN(
        name="test-fqdn", value="example.com-da", description="Test domain"
    )
    assert obj.value == "example.com-da"


def test_invalid_ip_network():
    with pytest.raises(ValueError):
        AddressObjectIPNetwork(
            name="invalid-net", value="invalid_ip", tags={"test"}
        )


def test_invalid_ip_range_format():
    with pytest.raises(ValueError):
        AddressObjectIPRange(
            name="invalid-range",
            value="10.0.0.1-20.0.0.100.1",  # Invalid IP
            tags={"network"},
        )


def test_invalid_fqdn():
    with pytest.raises(ValueError):
        AddressObjectFQDN(
            name="invalid-fqdn",
            value="example..com",
            description="Invalid domain",
        )


class TestParsing:
    @pytest.fixture
    def json_data(self):
        return {
            "@name": "json-test",
            "description": "JSON test",
            "tag": {"member": ["json"]},
        }

    def test_parse_json_ip_netmask(self, json_data):
        json_data["ip-netmask"] = "10.0.0.0/8"
        obj = AddressObject.parse_json(json_data)
        assert isinstance(obj, AddressObjectIPNetwork)
        assert obj.value == IPv4Network("10.0.0.0/8")

    def test_parse_json_ip_range(self, json_data):
        json_data["ip-range"] = "192.168.1.1-192.168.1.254"
        obj = AddressObject.parse_json(json_data)
        assert isinstance(obj, AddressObjectIPRange)
        assert obj.value == (
            IPv4Address("192.168.1.1"),
            IPv4Address("192.168.1.254"),
        )

    def test_parse_json_fqdn(self, json_data):
        json_data["fqdn"] = "test.example.com"
        obj = AddressObject.parse_json(json_data)
        assert isinstance(obj, AddressObjectFQDN)
        assert obj.value == "test.example.com"

    def test_parse_csv_ip_network(self):
        csv_data = {
            "Name": "csv-net",
            "Type": "IP Address",
            "Address": "172.16.0.0/16",
            "Tag": "network;test",
        }
        obj = AddressObject.parse_csv(csv_data)
        assert isinstance(obj, AddressObjectIPNetwork)
        assert obj.tags == {"network", "test"}

    def test_parse_csv_invalid_type(self):
        csv_data = {"Name": "invalid", "Type": "Invalid", "Address": "dummy"}
        with pytest.raises(ValueError):
            AddressObject.parse_csv(csv_data)


def test_ip_network_with_host():
    obj = AddressObjectIPNetwork(name="host-net", value="192.168.1.1/32")
    assert obj.value == IPv4Network("192.168.1.1/32")


def test_case_insensitive_fqdn():
    obj = AddressObjectFQDN(name="mixed-case", value="Example.COM")
    assert obj.value == "example.com"


def test_missing_address_in_csv():
    csv_data = {"Name": "missing-addr", "Type": "IP Address"}
    with pytest.raises(KeyError):
        AddressObject.parse_csv(csv_data)
