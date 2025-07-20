from ipaddress import IPv4Network

import pytest

from policy_inspector.builtin.shadowing.scenario import AdvancedShadowing
from policy_inspector.model.address_object import (
    AddressObjectFQDN,
    AddressObjectIPNetwork,
)
from policy_inspector.model.security_rule import SecurityRule


@pytest.fixture
def base_rules():
    """Basic rule set with shadowing relationships after resolution"""
    return [
        SecurityRule(  # Broad rule that should shadow others
            name="rule1",
            source_addresses={"wide-net"},
            destination_addresses={"any"},
            action="allow",
        ),
        SecurityRule(  # Narrower rule that should be shadowed
            name="rule2",
            source_addresses={"narrow-net"},
            destination_addresses={"any"},
            action="allow",
        ),
        SecurityRule(  # Same as rule2 but different action
            name="rule3",
            source_addresses={"narrow-net"},
            destination_addresses={"any"},
            action="deny",
        ),
    ]


@pytest.fixture
def address_objects():
    return [
        AddressObjectIPNetwork(
            name="wide-net", value=IPv4Network("10.0.0.0/8")
        ),
        AddressObjectIPNetwork(
            name="narrow-net", value=IPv4Network("10.1.0.0/16")
        ),
        AddressObjectFQDN(name="web-fqdn", value="example.com"),
    ]


@pytest.fixture
def fqdn_rules():
    return [
        SecurityRule(
            name="fqdn-rule1",
            destination_addresses={"web-fqdn"},
            source_addresses={"any"},
        ),
        SecurityRule(
            name="fqdn-rule2",
            destination_addresses={"web-fqdn"},
            source_addresses={"wide-net"},
        ),
    ]


@pytest.fixture
def mixed_rules(address_objects):
    return [
        SecurityRule(
            name="mixed1",
            source_addresses={"wide-net", "web-fqdn"},
            destination_addresses={"narrow-net"},
        ),
        SecurityRule(
            name="mixed2",
            source_addresses={"narrow-net"},
            destination_addresses={"web-fqdn", "wide-net"},
        ),
    ]


def test_empty_rules(address_objects):
    """Test scenario with empty rule list"""
    scenario = AdvancedShadowing(
        panorama=None,
        device_groups=["test"],
        security_rules_by_dg={"test": []},
        address_objects_by_dg={"test": address_objects},
        address_groups_by_dg={"test": []},
    )
    results = scenario.execute()
    assert results == {"test": {}}


def test_single_rule(address_objects):
    """Test scenario with single rule"""
    rule = SecurityRule(name="single", source_addresses={"wide-net"})
    scenario = AdvancedShadowing(
        panorama=None,
        device_groups=["test"],
        security_rules_by_dg={"test": [rule]},
        address_objects_by_dg={"test": address_objects},
        address_groups_by_dg={"test": []},
    )
    results = scenario.execute()
    assert len(results["test"]) == 1
    assert results["test"]["single"] == {}


@pytest.mark.parametrize(
    "rule_index,expected_preceding",
    [
        (0, 0),  # First rule has no preceding
        (1, 1),  # Second rule checks 1 preceding
        (2, 2),  # Third rule checks 2 preceding
    ],
)
def test_rule_preceding_counts(
    base_rules, address_objects, rule_index, expected_preceding
):
    """Verify correct number of preceding rules checked for each position"""
    scenario = AdvancedShadowing(
        panorama=None,
        device_groups=["test"],
        security_rules_by_dg={"test": base_rules},
        address_objects_by_dg={"test": address_objects},
        address_groups_by_dg={"test": []},
    )
    results = scenario.execute()
    rule_name = base_rules[rule_index].name
    assert len(results["test"][rule_name]) == expected_preceding


def test_shadowing_relationships(base_rules, address_objects):
    scenario = AdvancedShadowing(
        panorama=None,
        device_groups=["test"],
        security_rules_by_dg={"test": base_rules},
        address_objects_by_dg={"test": address_objects},
        address_groups_by_dg={"test": []},
    )
    results = scenario.execute()
    # assert "rule1" in results["rule2"]
    assert (
        results["test"]["rule2"]["rule1"]["check_source_addresses_by_ip"][0]
        is True
    )
    assert (
        results["test"]["rule3"]["rule1"]["check_source_addresses_by_ip"][0]
        is True
    )


def test_fqdn_rule_handling(fqdn_rules, address_objects):
    scenario = AdvancedShadowing(
        panorama=None,
        device_groups=["test"],
        security_rules_by_dg={"test": fqdn_rules},
        address_objects_by_dg={"test": address_objects},
        address_groups_by_dg={"test": []},
    )
    results = scenario.execute()
    assert len(results["test"]["fqdn-rule1"]) == 0
    assert "fqdn-rule1" in results["test"]["fqdn-rule2"]


def test_mixed_address_types(mixed_rules, address_objects):
    """Test rules with combined IP and FQDN addresses"""
    scenario = AdvancedShadowing(
        panorama=None,
        device_groups=["test"],
        security_rules_by_dg={"test": mixed_rules},
        address_objects_by_dg={"test": address_objects},
        address_groups_by_dg={"test": []},
    )
    results = scenario.execute()
    assert len(results["test"]["mixed1"]) == 0
    assert len(results["test"]["mixed2"]) == 1


def test_identical_rules(address_objects):
    """Test multiple identical rules after resolution"""
    rules = [
        SecurityRule(
            name=f"rule{i}",
            source_addresses={"wide-net"},
            destination_addresses={"narrow-net"},
        )
        for i in range(3)
    ]

    scenario = AdvancedShadowing(
        panorama=None,
        device_groups=["test"],
        security_rules_by_dg={"test": rules},
        address_objects_by_dg={"test": address_objects},
        address_groups_by_dg={"test": []},
    )
    results = scenario.execute()

    # Each subsequent rule should check all preceding rules
    for i, rule_name in enumerate(["rule0", "rule1", "rule2"]):
        assert len(results["test"][rule_name]) == i
