import logging
import re
from ipaddress import IPv4Address, IPv4Network
from typing import ClassVar

from pydantic import Field, field_validator

from policy_inspector.model.base import MainModel

logger = logging.getLogger(__name__)


class AddressObject(MainModel):
    singular: ClassVar[str] = "Address Object"
    plural: ClassVar[str] = "Address Objects"

    name: str = Field(..., description="Name of the address object.")
    description: str = Field(default="", description="Object description")
    tags: set[str] = Field(default_factory=set, description="Tags")

    def is_covered_by(self, other: type["AddressObject"]) -> bool:
        raise NotImplementedError("To be implement in child class")

    @classmethod
    def parse_json(cls, data: dict) -> "AddressObject":
        """Parse JSON data from PAN-OS API response"""
        type_map = {
            "ip-netmask": AddressObjectIPNetwork,
            "ip-range": AddressObjectIPRange,
            "fqdn": AddressObjectFQDN,
        }
        key_name = next(k for k in type_map if k in data)
        subclass = type_map[key_name]

        return subclass(
            name=data.get("@name"),
            value=data[key_name],
            description=data.get("description", ""),
            tags=data.get("tag", set()),
        )

    @classmethod
    def parse_csv(cls, data: dict) -> "AddressObject":
        """Parse CSV row from spreadsheet import"""
        type_map = {
            "IP Address": AddressObjectIPNetwork,
            "IP Range": AddressObjectIPRange,
            "FQDN": AddressObjectFQDN,
        }
        addr_type = data.get("Type", "")
        try:
            subclass = type_map[addr_type]
        except KeyError as ex:
            raise ValueError(f"Unknown 'Type'='{addr_type}'") from ex

        tags = data.get("Tag", "")
        tags = tags.split(";") if tags else set()
        return subclass(
            name=data["Name"],
            value=data["Address"],
            description=data.get("Description", ""),
            tags=tags,
        )


class AddressObjectIPNetwork(AddressObject):
    value: IPv4Network = Field(..., description="Address IP subnet value")

    @field_validator("value", mode="before")
    @classmethod
    def convert(cls, v) -> IPv4Network:
        try:
            return IPv4Network(v, strict=False)
        except ValueError as ex:
            raise ValueError(f"value '{v}' is not a valid IPv4 network") from ex

    def is_covered_by(self, other: type["AddressObject"]) -> bool:
        if isinstance(other, AddressObjectIPNetwork):
            return self.value.subnet_of(other.value)
        if isinstance(other, AddressObjectIPRange):
            return (
                self.value.network_address >= other.value[0]
                and self.value.broadcast_address <= other.value[1]
            )
        return False


class AddressObjectIPRange(AddressObject):
    value: tuple[IPv4Address, IPv4Address] = Field(
        ..., description="Address IP range value"
    )

    @field_validator("value", mode="before")
    @classmethod
    def convert(cls, v) -> tuple[IPv4Address, IPv4Address]:
        if isinstance(v, str):
            parts = tuple(v.split("-"))
            return tuple(map(IPv4Address, parts))
        if isinstance(v, (tuple, list)):
            return tuple(map(IPv4Address, v))
        return v

    @field_validator("value", mode="after")
    @classmethod
    def check(cls, v):
        print(v)
        if v[0] > v[1]:
            raise ValueError("last IP address must be greater than first")
        return v

    def is_covered_by(self, other: type["AddressObject"]) -> bool:
        if isinstance(other, AddressObjectIPNetwork):
            network_start = other.value.network_address
            network_end = other.value.broadcast_address
            return (
                self.value[0] >= network_start and self.value[1] <= network_end
            )
        if isinstance(other, AddressObjectIPRange):
            return (
                self.value[0] >= other.value[0]
                and self.value[1] <= other.value[1]
            )
        return False


class AddressObjectFQDN(AddressObject):
    value: str = Field(..., description="Address FQDN value")

    @field_validator("value", mode="before")
    @classmethod
    def validate(cls, v: str) -> str:
        v = v.lower()
        fqdn_regex = r"^([a-z0-9-]{1,63}\.)+[a-z]{2,63}$"
        if not re.match(fqdn_regex, v):
            raise ValueError(
                f"Invalid FQDN={v}. Not matches regex: {fqdn_regex}"
            )
        return v

    def is_covered_by(self, other: type["AddressObject"]) -> bool:
        if isinstance(other, AddressObjectFQDN):
            return self.value.lower() == other.value.lower()
        return False
