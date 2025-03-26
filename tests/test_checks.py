# test_check_functions.py
from typing import Callable

import pytest
from _pytest.mark import ParameterSet

from policy_inspector.models import AnyObj
from policy_inspector.scenario.shadowing import (
    check_action,
    check_application,
    check_destination_address,
    check_destination_zone,
    check_source_address,
    check_source_zone,
)


class MockSecurityRule:
    """Mock SecurityRule for testing."""

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "test_rule")
        self.action = kwargs.get("action", "allow")
        self.source_zones = set(kwargs.get("source_zones", {}))
        self.destination_zones = set(kwargs.get("destination_zones", {}))
        self.source_addresses = set(kwargs.get("source_addresses", {}))
        self.destination_addresses = set(
            kwargs.get("destination_addresses", {})
        )
        self.applications = set(kwargs.get("applications", {}))
        self.services = set(kwargs.get("services", {}))


TEST_CASES: dict[Callable, dict[str, list]] = {
    check_action: {
        "same actions": [
            {"action": "allow"},
            {"action": "allow"},
            (True, "Actions match"),
        ],
        "different actions": [
            {"action": "allow"},
            {"action": "deny"},
            (False, "Actions differ"),
        ],
    },
    check_source_zone: {
        "same zones": [
            {"source_zones": {"trust"}},
            {"source_zones": {"trust"}},
            (True, "Source zones are the same"),
        ],
        "zone subnet": [
            {"source_zones": {"trust", "dmz"}},
            {"source_zones": {"trust"}},
            (True, "Preceding rule source zones cover rule's source zones"),
        ],
        "any zones": [
            {"source_zones": {"trust"}},
            {"source_zones": {AnyObj}},
            (True, "Preceding rule source zones is 'any'"),
        ],
    },
    check_destination_zone: {
        "same destination zones": [
            {"destination_zones": {"untrust"}},
            {"destination_zones": {"untrust"}},
            (True, "Destination zones are the same"),
        ],
        "destination zone subset": [
            {"destination_zones": {"untrust"}},
            {"destination_zones": {"untrust", "dmz"}},
            (
                True,
                "Preceding rule destination zones cover rule's source zones",
            ),
        ],
        "any destination zone": [
            {"destination_zones": {"dmz"}},
            {"destination_zones": {AnyObj}},
            (True, "Preceding rule destination zones is 'any'"),
        ],
    },
    check_source_address: {
        "same source addresses": [
            {"source_addresses": {"192.168.1.1"}},
            {"source_addresses": {"192.168.1.1"}},
            (True, "Source addresses are the same"),
        ],
        "subset of source addresses": [
            {"source_addresses": {"192.168.1.1"}},
            {"source_addresses": {"192.168.1.1", "192.168.1.2"}},
            (
                True,
                "Preceding rule source addresses cover rule's source addresses",
            ),
        ],
        "any source address": [
            {"source_addresses": {"192.168.1.1"}},
            {"source_addresses": {AnyObj}},
            (True, "Preceding rule allows any source address"),
        ],
    },
    check_destination_address: {
        "same destination addresses": [
            {"destination_addresses": {"10.0.0.1"}},
            {"destination_addresses": {"10.0.0.1"}},
            (True, "Destination addresses are the same"),
        ],
        "subset of destination addresses": [
            {"destination_addresses": {"10.0.0.1", "10.0.0.2"}},
            {"destination_addresses": {"10.0.0.1"}},
            (
                True,
                "Preceding rule destination addresses cover rule's source addresses",
            ),
        ],
        "any destination address": [
            {"destination_addresses": {"10.0.0.2"}},
            {"destination_addresses": {AnyObj}},
            (True, "Preceding rule allows any destination address"),
        ],
    },
    check_application: {
        "same applications": [
            {"applications": {"app1", "app2"}},
            {"applications": {"app2", "app1"}},
            (True, "Preceding rule contains rule's applications"),
        ],
        "subset of applications covered by preceding rule": [
            {"applications": {"app2"}},
            {"applications": {AnyObj}},
            (True, "Preceding rule allows any application"),
        ],
        "applications not covered by preceding rule": [
            {"applications": ["app3"]},
            {"applications": ["app4"]},
            (False, "Rule doesn't cover"),
        ],
    },
}


def _generate_params() -> list[ParameterSet]:
    values = []
    for func, cases in TEST_CASES.items():
        for case_id, case_params in cases.items():
            values.append(
                pytest.param(
                    func, *case_params, id=f"{func.__name__}][{case_id}"
                )
            )
    return values


CHECK_TEST_VALUES = _generate_params()


@pytest.mark.parametrize(
    "check_func,rule_params,preceding_rule_params,expected_result",
    CHECK_TEST_VALUES,
)
def test_(check_func, rule_params, preceding_rule_params, expected_result):
    rule = MockSecurityRule(**rule_params)
    preceding_rule = MockSecurityRule(**preceding_rule_params)
    result = check_func(rule, preceding_rule)
    assert result == expected_result
