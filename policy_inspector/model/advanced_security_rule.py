from typing import Optional, Union

from pydantic import Field

from policy_inspector.model.address_object import (
    AddressObjectFQDN,
    AddressObjectIPNetwork,
    AddressObjectIPRange,
)
from policy_inspector.model.security_rule import SecurityRule

AddressObjectTypes = Union[
    AddressObjectIPNetwork, AddressObjectIPRange, AddressObjectFQDN
]


class AdvancedSecurityRule(SecurityRule):
    resolved_source_addresses: Optional[list[AddressObjectTypes]] = Field(
        default=None,
        description="Resolved source addresses to a list of specific Address Objects",
    )

    resolved_destination_addresses: Optional[list[AddressObjectTypes]] = Field(
        default=None,
        description="Resolved destination to a list of specific Address Objects",
    )

    @classmethod
    def from_security_rule(
        cls, rule: SecurityRule, **kwargs
    ) -> "AdvancedSecurityRule":
        """Convert a base ``SecurityRule`` to an ``AdvancedSecurityRule``.

        Args:
            rule: ``SecurityRule`` instance to convert

        Returns:
            New ``AdvancedSecurityRule`` instance with same field values
        """
        data = rule.model_dump(
            exclude_none=True,
        )
        return cls(**data, **kwargs)
