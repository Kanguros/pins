from typing import TYPE_CHECKING, Literal, Optional, Union

from pydantic import AliasChoices, AliasPath, BaseModel, Field
from pydantic.networks import IPv4Network
from typing_extensions import Self

from .utils import load_json

if TYPE_CHECKING:
    from pathlib import Path

AnyObj = "any"
AnyObjType = set[Literal["any"]]

AppDefault = "application-default"
AppDefaultType = set[Literal["application-default"]]

SetStr = set[str]
Action = Literal["allow", "deny", "monitor"]


def MemberAlias(attribute_name: str, raw_name: str) -> AliasChoices:  # noqa: N802
    """Helper function for ``AliasChoices`` with ``AliasPath``."""
    return AliasChoices(AliasPath(raw_name, "member"), attribute_name)


class MainModel(BaseModel):
    """Base class for all data models. Mainly for common methods."""

    @classmethod
    def load_from_json(cls, file_path: Union[str, "Path"]) -> list[Self]:
        """Loads a JSON file and create instances from each item on the list"""
        data = load_json(file_path)
        return cls.load_many(data)

    @classmethod
    def load_many(cls, data: list[dict]) -> list[Self]:
        """Create instances from each item on the list."""
        return [cls(**item) for item in data]


class SecurityRule(MainModel):
    name: str = Field(
        ...,
        validation_alias=AliasChoices("name", "@name"),
        description="Name of a rule.",
    )
    action: Action = Field(
        ..., description="Whether the traffic should be allowed or denied."
    )
    source_zones: Union[SetStr, AnyObjType] = Field(
        validation_alias=MemberAlias("source_zones", "from"),
        description="Set of source zones or 'any'",
    )
    destination_zones: Union[SetStr, AnyObjType] = Field(
        validation_alias=MemberAlias("destination_zones", "to"),
        description="Set of destination zones or 'any'",
    )

    source_addresses: Union[SetStr, AnyObjType] = Field(
        validation_alias=MemberAlias("source_addresses", "source"),
        description="Source address objects/groups or 'any'",
    )

    destination_addresses: Union[SetStr, AnyObjType] = Field(
        validation_alias=MemberAlias("destination_addresses", "destination"),
        description="Destination address objects/groups or 'any'",
    )

    applications: Union[SetStr, AnyObjType] = Field(
        validation_alias=MemberAlias("applications", "application"),
        description="Set of applications or 'any' that the rule applies to.",
    )

    services: Union[SetStr, AnyObjType, AppDefaultType] = Field(
        validation_alias=MemberAlias("services", "service"),
        description="Services (e.g., TCP/UDP ports) or 'any'/'application-default'",
    )

    category: Union[SetStr, AnyObjType] = Field(
        validation_alias=MemberAlias("category", "category"),
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


class AddressGroup(MainModel):
    name: str = Field(..., validation_alias=AliasChoices("name", "@name"))
    description: str = Field(default="")
    tag: SetStr = Field(default_factory=set)
    static: SetStr = Field(default_factory=set)


class AddressObject(MainModel):
    name: str = Field(..., validation_alias=AliasChoices("name", "@name"))
    ip_netmask: str = Field(
        ..., validation_alias=AliasChoices("ip_netmask", "ip-netmask")
    )
