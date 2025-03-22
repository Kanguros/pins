from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from policy_inspector.models import SecurityRule

FilterFunction = Callable[["SecurityRule"], bool]


def apply_filters(
    filters: Iterable[FilterFunction], policies: Iterable["SecurityRule"]
) -> Iterator["SecurityRule"]:
    """Apply a set of filter functions to security policies.

    Args:
        filters: An iterable of filter functions that take a `SecurityRule` object
            and return a boolean indicating whether the rule should be included.
        policies: An iterable of `SecurityRule` objects to be filtered.

    Returns:
        An iterator over `SecurityRule` objects that pass all filter conditions.

    Example:
        filters = [exclude_disabled, exclude_deny]
        filtered_policies = apply_filters(filters, policies)
        for policy in filtered_policies:
            print(policy)
    """
    return filter(
        lambda p: all(filter_func(p) for filter_func in filters), policies
    )


def exclude_disabled(policy: "SecurityRule") -> bool:
    """Exclude security rules that are disabled."""
    return True if policy.enabled else False


def exclude_deny(policy: "SecurityRule") -> bool:
    """Exclude security rules with a 'deny' action."""
    return policy.action != "deny"
