import logging
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field
from pydantic.networks import IPv4Network

AnyObj = "any"
AnyObjType = set[Literal["any"]]

AppDefault = "application-default"
AppDefaultType = set[Literal["application-default"]]

SetStr = set[str]
Action = Literal["allow", "deny", "monitor"]

logger = logging.getLogger(__name__)


class MainModel(BaseModel):
    """Base class for all example models. Mainly for common methods."""


class SecurityRule(MainModel):
    name: str = Field(
        ...,
        description="Name of a rule.",
    )
    enabled: bool = Field(
        default=True,
        description="Whether the policy is enabled or disabled",
    )
    action: Action = Field(
        ...,
        description="Whether the traffic should be allowed or denied.",
    )
    source_zones: Union[SetStr, AnyObjType] = Field(
        ...,
        description="Set of source zones or 'any'",
    )
    destination_zones: Union[SetStr, AnyObjType] = Field(
        ...,
        description="Set of destination zones or 'any'",
    )

    source_addresses: Union[SetStr, AnyObjType] = Field(
        ...,
        description="Source address objects/groups or 'any'",
    )

    destination_addresses: Union[SetStr, AnyObjType] = Field(
        ...,
        description="Destination address objects/groups or 'any'",
    )

    applications: Union[SetStr, AnyObjType] = Field(
        ...,
        description="Set of applications or 'any' that the rule applies to.",
    )

    services: Union[SetStr, AnyObjType, AppDefaultType] = Field(
        ...,
        description="Services (e.g., TCP/UDP ports) or 'any'/'application-default'",
    )

    category: Union[SetStr, AnyObjType] = Field(
        ...,
        description="URL categories or 'any'",
    )

    source_addresses_ip: Optional[set[IPv4Network]] = Field(
        default=None,
        description="Resolved source addresses to a set of IP networks. ",
    )

    destination_addresses_ip: Optional[set[IPv4Network]] = Field(
        default=None,
        description="Resolved destination addresses to a set of IP networks.",
    )

    @classmethod
    def parse_json(cls, data: dict) -> "SecurityRule":
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

        parsed = {mapping.get(k, k): extract_value(v) for k, v in data.items()}
        return cls(**parsed)

    @classmethod
    def parse_csv(cls, data: dict) -> "SecurityRule":
        """Map a CSV row to a SecurityRule."""
        mapping = {
            "Source": "source_addresses",
            "Destination": "destination_addresses",
            "From": "source_zones",
            "To": "destination_zones",
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
        parsed_data = {}

        for key, value in data.items():
            mapped_key = mapping.get(key, key)
            key_value = value
            if mapped_key in list_fields:
                key_value = set(value.split(";")) if value else set()
            parsed_data[mapped_key] = key_value

        return cls(**parsed_data)


class AddressGroup(MainModel):
    name: str = Field(..., description="Name of the address group.")
    description: str = Field(default="")
    tag: set[str] = Field(default_factory=set)
    static: set[str] = Field(default_factory=set)

    @classmethod
    def parse_json(cls, data: dict) -> "AddressGroup":
        """Map a JSON object to an AddressGroup."""
        mapping = {"@name": "name", "ip-address": "ip_address"}
        list_fields = ("tag", "static")

        parsed = {}
        for key, value in data.items():
            mapped_key = mapping.get(key, key)
            key_value = value
            if mapped_key in list_fields:
                key_value = set(value) if value else set()
            parsed[mapped_key] = key_value
        return cls(**parsed)


class AddressObject(MainModel):
    name: str = Field(..., description="Name of the address object.")
    ip_netmask: str = Field(
        ...,
        description="IP address and netmask of the address object.",
    )

    @classmethod
    def parse_json(cls, data: dict) -> "AddressObject":
        """Map a JSON object to an AddressObject."""
        mapping = {"@name": "name", "ip-netmask": "ip_netmask"}
        parsed = {mapping.get(k, k): v for k, v in data.items()}
        return cls(**parsed)
