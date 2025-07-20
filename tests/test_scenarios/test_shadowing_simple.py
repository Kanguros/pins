import pytest

from policy_inspector.builtin.shadowing_simple.scenario import Shadowing
from policy_inspector.model.security_rule import SecurityRule


@pytest.fixture
def base_rules():
    """Basic rule set with 3 rules where rule3 is shadowed by rule1"""
    return [
        SecurityRule(
            name="rule1",
            action="allow",
            source_zones={"zoneA"},
            destination_zones={"zoneB"},
            source_addresses={"any"},
            destination_addresses={"any"},
            applications={"web"},
            services={"http"},
        ),
        SecurityRule(
            name="rule2",
            action="deny",  # Different action prevents shadowing
            source_zones={"zoneA"},
            destination_zones={"zoneB"},
            source_addresses={"any"},
            destination_addresses={"any"},
            applications={"web"},
            services={"http"},
        ),
        SecurityRule(  # Should be shadowed by rule1
            name="rule3",
            action="allow",
            source_zones={"zoneA"},
            destination_zones={"zoneB"},
            source_addresses={"any"},
            destination_addresses={"any"},
            applications={"web"},
            services={"http"},
        ),
    ]


@pytest.fixture
def empty_rules():
    """Empty rule list"""
    return []


@pytest.fixture
def different_rules():
    return [
        SecurityRule(
            name="ruleA",
            action="allow",
            source_zones={"zoneX"},
            destination_zones={"zoneY"},
            source_addresses={"192.168.1.1"},
            destination_addresses={"10.2.111.2"},
            applications={"ssh"},
        ),
        SecurityRule(
            name="ruleB",
            action="deny",
            source_zones={"zoneZ"},
            destination_zones={"zoneQ"},
            source_addresses={"10.0.0.1"},
            destination_addresses={"10.2.2.2"},
            applications={"http"},
        ),
    ]


@pytest.fixture
def identical_rules():
    return [
        SecurityRule(
            name=f"rule{i}",
            action="allow",
            source_zones={"zoneA"},
            destination_zones={"zoneB"},
            source_addresses={"any"},
            destination_addresses={"any"},
            applications={"web"},
            services={"http"},
        )
        for i in range(3)
    ]


def test_empty_rules(empty_rules):
    # Provide required device_groups argument (empty list for test)
    from policy_inspector.panorama import PanoramaConnector

    panorama = PanoramaConnector(
        hostname="dummy", username="dummy", password="dummy", verify_ssl=False
    )
    scenario = Shadowing(panorama=panorama, device_groups=[])
    results = scenario.execute()
    assert results == {}


def test_single_rule(base_rules):
    from policy_inspector.panorama import PanoramaConnector

    panorama = PanoramaConnector(
        hostname="dummy", username="dummy", password="dummy", verify_ssl=False
    )
    scenario = Shadowing(panorama=panorama, device_groups=["dg1"])
    # Patch _load_security_rules_per_dg to return our test rule
    scenario._load_security_rules_per_dg = lambda: {"dg1": [base_rules[0]]}
    scenario.security_rules_by_dg = {"dg1": [base_rules[0]]}
    scenario.rules_by_name_by_dg = {"dg1": {base_rules[0].name: base_rules[0]}}
    results = scenario.execute()
    assert len(results["dg1"]) == 1
    assert results["rule1"] == {}


@pytest.mark.parametrize(
    "rule_index,expected_preceding",
    [
        (0, 0),  # First rule has no preceding
        (1, 1),  # Second rule checks 1 preceding
        (2, 2),  # Third rule checks 2 preceding
    ],
)
def test_rule_preceding_counts(base_rules, rule_index, expected_preceding):
    from policy_inspector.panorama import PanoramaConnector

    panorama = PanoramaConnector(
        hostname="dummy", username="dummy", password="dummy", verify_ssl=False
    )
    scenario = Shadowing(panorama=panorama, device_groups=["dg1"])
    scenario._load_security_rules_per_dg = lambda: {"dg1": base_rules}
    scenario.security_rules_by_dg = {"dg1": base_rules}
    scenario.rules_by_name_by_dg = {
        "dg1": {rule.name: rule for rule in base_rules}
    }
    results = scenario.execute()
    rule_name = base_rules[rule_index].name
    assert len(results["dg1"][rule_name]) == expected_preceding


def test_identical_rules(identical_rules):
    from policy_inspector.panorama import PanoramaConnector

    panorama = PanoramaConnector(
        hostname="dummy", username="dummy", password="dummy", verify_ssl=False
    )
    scenario = Shadowing(panorama=panorama, device_groups=["dg1"])
    scenario._load_security_rules_per_dg = lambda: {"dg1": identical_rules}
    scenario.security_rules_by_dg = {"dg1": identical_rules}
    scenario.rules_by_name_by_dg = {
        "dg1": {rule.name: rule for rule in identical_rules}
    }
    results = scenario.execute()
    for i, rule_result in enumerate(results["dg1"].values()):
        assert i == len(rule_result)
