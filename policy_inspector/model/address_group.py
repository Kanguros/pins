from typing import ClassVar

from pydantic import Field

from policy_inspector.model.base import MainModel, SetStr


class AddressGroup(MainModel):
    singular: ClassVar[str] = "Address Group"
    plural: ClassVar[str] = "Address Groups"

    name: str = Field(..., description="Name of the address group.")
    description: str = Field(default="")
    tag: SetStr = Field(default_factory=set)
    static: SetStr = Field(default_factory=set)

    @classmethod
    def parse_json(cls, data: dict) -> "AddressGroup":
        """Map a JSON object to an AddressGroup."""
        mapping = {"@name": "name"}
        list_fields = ("tag", "static")

        parsed = {}
        for key, value in data.items():
            mapped_key = mapping.get(key, key)
            key_value = value
            if mapped_key in list_fields:
                members = key_value.get("member", [])
                key_value = set(members) if members else set()
            parsed[mapped_key] = key_value
        return cls(**parsed)

    @classmethod
    def parse_csv(cls, data: dict) -> "AddressGroup":
        """Map a JSON object to an AddressObject."""
        mapping = {"Name": "name", "Addresses": "static", "Tags": "tag"}
        list_fields = ("tag", "static")
        parsed = {}
        for key, value in data.items():
            mapped_key = mapping.get(key, key)
            if not mapped_key:
                continue
            key_value = value
            if mapped_key in list_fields:
                key_value = set(value.split(";")) if value else set()
            parsed[mapped_key] = key_value
        return cls(**parsed)
