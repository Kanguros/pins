import pytest

from policy_inspector.filters import (
    apply_filters,
    exclude_deny,
    exclude_disabled,
)


class MockObject:
    """Mock class to use in tests."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@pytest.mark.parametrize(
    "policies, filters, expected",
    [
        # Test case: No filters applied, return all policies
        (
            [
                MockObject(name="rule1", enabled=True, action="allow"),
                MockObject(name="rule2", enabled=False, action="deny"),
            ],
            [],
            ["rule1", "rule2"],
        ),
        # Test case: Exclude disabled rules
        (
            [
                MockObject(name="rule1", enabled=True, action="allow"),
                MockObject(name="rule2", enabled=False, action="allow"),
                MockObject(name="rule3", enabled=True, action="deny"),
            ],
            [exclude_disabled],
            ["rule1", "rule3"],
        ),
        # Test case: Exclude deny rules
        (
            [
                MockObject(name="rule1", enabled=True, action="allow"),
                MockObject(name="rule2", enabled=True, action="deny"),
                MockObject(name="rule3", enabled=False, action="allow"),
            ],
            [exclude_deny],
            ["rule1", "rule3"],
        ),
        # Test case: Exclude both disabled and deny rules
        (
            [
                MockObject(name="rule1", enabled=True, action="allow"),
                MockObject(name="rule2", enabled=False, action="deny"),
                MockObject(name="rule3", enabled=True, action="deny"),
                MockObject(name="rule4", enabled=False, action="allow"),
            ],
            [exclude_disabled, exclude_deny],
            ["rule1"],
        ),
        # Test case: No policies, expect empty result
        ([], [exclude_disabled, exclude_deny], []),
    ],
)
def test_apply_filters(policies, filters, expected):
    """Test apply_filters with different filters and policy lists."""
    filtered_policies = list(apply_filters(filters, policies))
    filtered_names = [policy.name for policy in filtered_policies]

    assert filtered_names == expected
