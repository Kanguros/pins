from typing import ClassVar, Optional, Union

from pydantic import Field, PositiveInt

from policy_inspector.model.address_object import (
    AddressObjectFQDN,
    AddressObjectIPNetwork,
    AddressObjectIPRange,
)
from policy_inspector.model.base import (
    Action,
    AnyObjType,
    AppDefaultType,
    MainModel,
    SetStr,
)


class SecurityRule(MainModel):
    singular: ClassVar[str] = "Security Rule"
    plural: ClassVar[str] = "Security Rules"

    index: PositiveInt = Field(
        default=1, description="Policy index in a list of Policies."
    )
    name: str = Field(
        ...,
        description="Name of a rule.",
    )
    enabled: bool = Field(
        default=True,
        description="Whether the policy is enabled or disabled",
    )
    action: Action = Field(
        default="allow",
        description="Whether the traffic should be allowed or denied.",
    )
    source_zones: Union[SetStr, AnyObjType] = Field(
        default={"any"},
        description="Set of source zones or 'any'",
    )
    destination_zones: Union[SetStr, AnyObjType] = Field(
        default={"any"},
        description="Set of destination zones or 'any'",
    )

    source_addresses: Union[SetStr, AnyObjType] = Field(
        default={"any"},
        description="Source address objects/groups or 'any'",
    )

    destination_addresses: Union[SetStr, AnyObjType] = Field(
        default={"any"},
        description="Destination address objects/groups or 'any'",
    )

    applications: Union[SetStr, AnyObjType] = Field(
        default={"any"},
        description="Set of applications or 'any' that the rule applies to.",
    )

    services: Union[SetStr, AnyObjType, AppDefaultType] = Field(
        default_factory=set,
        description="Services (e.g., TCP/UDP ports) or 'any'/'application-default'",
    )

    category: Union[SetStr, AnyObjType] = Field(
        default={"any"},
        description="URL categories or 'any'",
    )

    @classmethod
    def parse_json(cls, elements: list[dict]) -> list["SecurityRule"]:
        """Map a JSON object to a SecurityRule."""
        mapping = {
            "@name": "name",
            "source": "source_addresses",
            "destination": "destination_addresses",
            "from": "source_zones",
            "to": "destination_zones",
            "application": "applications",
            "service": "services",
            "category": "category",
        }

        def extract_value(value):
            if isinstance(value, dict) and "member" in value:
                return set(value["member"])
            return value

        security_rules = []
        for index, data in enumerate(elements, start=1):
            parsed = {
                mapping.get(k, k): extract_value(v) for k, v in data.items()
            }
            parsed["index"] = index
            security_rules.append(cls(**parsed))
        return security_rules

    @classmethod
    def parse_csv(cls, elements: list[dict]) -> list["SecurityRule"]:
        """Map a CSV row to a SecurityRule."""
        mapping = {
            "Name": "name",
            "Source Address": "source_addresses",
            "Destination Address": "destination_addresses",
            "Source Zone": "source_zones",
            "Destination Zone": "destination_zones",
            "Application": "applications",
            "Service": "services",
            "Category": "category",
        }
        list_fields = {
            "source_addresses",
            "destination_addresses",
            "source_zones",
            "destination_zones",
            "applications",
            "services",
            "category",
        }

        security_rules = []
        for index, data in enumerate(elements, start=1):
            parsed_data = {"index": index}
            for key, value in data.items():
                mapped_key = mapping.get(key, key)
                key_value = value
                if mapped_key in list_fields:
                    key_value = set(value.split(";")) if value else set()
                parsed_data[mapped_key] = key_value
            security_rules.append(cls(**parsed_data))
        return security_rules


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
