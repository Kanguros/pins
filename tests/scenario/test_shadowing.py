import pytest

from policy_inspector.model.security_rule import SecurityRule
from policy_inspector.scenario.shadowing import Shadowing


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
    scenario = Shadowing(empty_rules)
    results = scenario.execute()
    assert results == {}


def test_single_rule(base_rules):
    scenario = Shadowing([base_rules[0]])
    results = scenario.execute()
    assert len(results) == 1
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
    scenario = Shadowing(base_rules)
    results = scenario.execute()
    rule_name = base_rules[rule_index].name
    assert len(results[rule_name]) == expected_preceding


def test_identical_rules(identical_rules):
    scenario = Shadowing(identical_rules)
    results = scenario.execute()
    for i, rule_result in enumerate(results.values()):
        assert i == len(rule_result)
