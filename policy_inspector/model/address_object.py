import re
from enum import Enum
from ipaddress import IPv4Network, IPv4Address
from typing import ClassVar, Union

from pydantic import Field

from policy_inspector.model.base import MainModel


class AddressType(str, Enum):
    IP_NETMASK = "ip-netmask"
    IP_RANGE = "ip-range"
    FQDN = "fqdn"


class AddressObject(MainModel):
    singular: ClassVar[str] = "Address Object"
    plural: ClassVar[str] = "Address Objects"

    name: str = Field(..., description="Name of the address object.")
    type: AddressType = Field(..., description="Type of address object.")
    value: Union[IPv4Network, tuple[IPv4Address, IPv4Address], str] = Field(...,
                                                                            description="Address value based on type")
    description: str = Field("", description="Object description")
    tags: set[str] = Field(default_factory=set, description="Tags")

    @staticmethod
    def convert_value(addr_type: AddressType, value: str) -> Union[IPv4Network, tuple[IPv4Address, IPv4Address], str]:

        if addr_type == AddressType.IP_NETMASK:
            try:
                return IPv4Network(value, strict=False)
            except ValueError:
                raise ValueError(f"Invalid IPv4 network format: {value}")

        if addr_type == AddressType.IP_RANGE:
            try:
                start_addr, end_addr = value.split("-")
                return (IPv4Address(start_addr), IPv4Address(end_addr))
            except Exception as ex:
                raise ValueError(f"Invalid IP range format '{value}'. ie:  10.0.0.1-10.0.0.100)")

        if addr_type == AddressType.FQDN:
            fqdn_regex = r'^([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$'
            if not re.match(fqdn_regex, value):
                raise ValueError(f"Invalid FQDN format: {value}")
            return value

        raise ValueError(f"Unknown AddressType: {addr_type}")

    @classmethod
    def parse_json(cls, data: dict) -> "AddressObject":
        """Parse JSON data from PAN-OS API response"""
        type_map = {
            'ip-netmask': (AddressType.IP_NETMASK, 'ip-netmask'),
            'ip-range': (AddressType.IP_RANGE, 'ip-range'),
            'fqdn': (AddressType.FQDN, 'fqdn')
        }

        addr_type_key = next((k for k in type_map if k in data), 'ip-netmask')
        addr_type, field_name = type_map[addr_type_key]
        value = cls.convert_value(addr_type, data.get(field_name, ''))

        return cls(
            name=data.get("@name"),
            type=addr_type,
            value=value,
            description=data.get("description", ""),
            tags=data.get("tag", set()),
        )

    @classmethod
    def parse_csv(cls, data: dict) -> "AddressObject":
        """Parse CSV row from spreadsheet import"""
        type_map = {
            "IP Address": AddressType.IP_NETMASK,
            "IP Range": AddressType.IP_RANGE,
            "FQDN": AddressType.FQDN,
        }
        addr_type = type_map.get(data.get("Type"))
        value = cls.convert_value(addr_type, data["Address"])
        tags = data.get("Tag", "")
        tags = tags.split(";") if tags else set()
        return cls(
            name=data["Name"],
            type=addr_type,
            value=value,
            description=data.get("Description"),
            tags=tags,
        )
