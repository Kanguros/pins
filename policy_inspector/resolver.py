import logging
from ipaddress import IPv4Network
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from policy_inspector.models import AddressGroup, AddressObject

logger = logging.getLogger(__name__)


class AddressResolver:
    """Process type of class to resolve Address Groups and Address Objects into their actual IP addresses.

    It expands Address Groups (AG) recursively and converts Address Objects (AO) into IP networks.

    Args:
        address_objects: A list of ``AddressObject``.
        address_groups: A list of ``AddressGroup``.
    """

    def __init__(
        self,
        address_objects: list["AddressObject"],
        address_groups: list["AddressGroup"],
    ):
        self.address_objects: dict[str, str] = {
            ao.name: ao.ip_netmask for ao in address_objects
        }
        self.address_groups: dict[str, set[str]] = {
            ag.name: ag.static for ag in address_groups
        }
        self.cache: dict[str, set[IPv4Network]] = {}

    def resolve(self, names: set[str]) -> set[IPv4Network]:
        """Resolve given names of ``Address Groups`` or ``Address Objects`` to actual IP address.

        Args:
            names: Names of ``Address Groups`` or ``Address Objects``

        Returns:
            Set of ``IPv4Network`` of all ``names``.

        """
        result = set()
        for name in names:
            result.update(self._resolve_name(name))
        return result

    def _resolve_name(self, name: str) -> set[IPv4Network]:
        """Resolve single ``name``"""
        if name in self.cache:
            return self.cache[name]

        if name in self.address_groups:
            logger.debug(f"Resolving group: {name}")
            resolved = set()
            for member in self.address_groups[name]:
                resolved.update(self._resolve_name(member))
            self.cache[name] = resolved
            return resolved

        if name in self.address_objects:
            logger.debug(f"Resolving object: {name}")
            try:
                network = IPv4Network(self.address_objects[name], strict=False)
                result = {network}
                self.cache[name] = result
                return result
            except ValueError as e:
                raise ValueError(f"Invalid IP network for {name}: {e}") from e

        raise ValueError(f"Unknown address object/group: {name}")
