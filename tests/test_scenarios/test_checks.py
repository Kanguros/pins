from collections.abc import Callable

import pytest
from _pytest.mark import ParameterSet

from policy_inspector.builtin.shadowing_simple.checks import (
    check_action,
    check_application,
    check_destination_address,
    check_destination_zone,
    check_source_address,
    check_source_zone,
)
from policy_inspector.model.base import AnyObj
from policy_inspector.model.security_rule import SecurityRule

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
        "same source zones": [
            {"source_zones": {"trust"}},
            {"source_zones": {"trust"}},
            (True, "Source zones are the same"),
        ],
        "cover source zone": [
            {"source_zones": {"trust"}},
            {"source_zones": {"trust", "dmz"}},
            (False, "Source zones differ"),
        ],
        "any zones": [
            {"source_zones": {"trust"}},
            {"source_zones": {AnyObj}},
            (True, "Preceding rule source zones is 'any'"),
        ],
        "any and any": [
            {"source_zones": {AnyObj}},
            {"source_zones": {AnyObj}},
            (True, "Source zones are the same"),
        ],
        "any not covered by": [
            {"source_zones": {AnyObj}},
            {"source_zones": {"somezone", "second_zone"}},
            (False, "Source zones differ"),
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
                "Preceding rule destination zones cover rule's destination zones",
            ),
        ],
        "any destination zone": [
            {"destination_zones": {"dmz"}},
            {"destination_zones": {AnyObj}},
            (True, "Preceding rule destination zones is 'any'"),
        ],
        "any not covered by": [
            {"destination_zones": {AnyObj}},
            {"destination_zones": {"dmz"}},
            (False, "Destination zones differ"),
        ],
    },
    check_source_address: {
        "the same source addresses": [
            {"source_addresses": {"192.168.1.1"}},
            {"source_addresses": {"192.168.1.1"}},
            (True, "Source addresses are the same"),
        ],
        "cover source addresses": [
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
            {"destination_addresses": {"10.0.0.1"}},
            {"destination_addresses": {"10.0.0.1", "10.0.0.2"}},
            (
                True,
                "Preceding rule destination addresses cover rule's destination addresses",
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
            (True, "The same applications"),
        ],
        "any in preceding rule": [
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


def generate_checks_test_data() -> list[ParameterSet]:
    values = []
    for func, cases in TEST_CASES.items():
        for case_name, case_params in cases.items():
            case_id = f"{func.__name__}][{case_name}"
            values.append(pytest.param(func, *case_params, id=case_id))
    return values


CHECK_TEST_VALUES = generate_checks_test_data()


@pytest.mark.parametrize(
    "check_func,rule_params,preceding_rule_params,expected_result",
    CHECK_TEST_VALUES,
)
def test_(check_func, rule_params, preceding_rule_params, expected_result):
    rule = SecurityRule(name="rule0", **rule_params)
    preceding_rule = SecurityRule(
        name="rule_before_rule0", **preceding_rule_params
    )
    result = check_func(rule, preceding_rule)
    assert result == expected_result
