import logging
from ipaddress import IPv4Network
from typing import Union

from pins.models import (
    AddressGroup,
    AddressObject,
    AnyObj,
    SecurityRule,
)

logger = logging.getLogger(__name__)


class AddressLookup:
    """Process type of class to resolve Address Groups and Address Objects into their actual IP addresses.

    It expands Address Groups (AG) recursively and converts Address Objects (AO) into IP networks.

    Args:
        address_objects: A list of AddressObject.
        address_groups: A list of AddressGroup.

    """

    def __init__(
        self,
        address_objects: list[AddressObject],
        address_groups: list[AddressGroup],
    ):
        self.address_objects = {
            ao.name: ao.ip_netmask for ao in address_objects
        }
        self.address_groups = {ag.name: set(ag.static) for ag in address_groups}
        self.cache: dict[Union[str, tuple[str]], set[IPv4Network]] = {}

    def resolve(self, names: set[str]) -> set[IPv4Network]:
        """Resolve given names of ``Address Groups`` or ``Address Objects``  into actual IP address.

        Args:
            names: Names of ``Address Groups`` or ``Address Objects``

        Returns:
            Unique ``IPv4Network``.

        """
        resolved = set()
        stack = list(names)
        visited = set()

        while stack:
            current = stack.pop()
            logger.debug(f"Resolving name={current} to IP address")

            if current in visited:
                continue
            visited.add(current)

            if current in self.cache:
                resolved.update(self.cache[current])
                continue

            if current in self.address_groups:
                stack.extend(self.address_groups[current])
                continue

            if current in self.address_objects:
                current = self.address_objects[current]

            try:
                ip_network = IPv4Network(current, strict=False)
                resolved.add(ip_network)
                self.cache[current] = set(ip_network)
            except ValueError as ex:
                raise ValueError(
                    f"Unknown address object or group: {current}",
                ) from ex

        self.cache[tuple(names)] = resolved
        return resolved


def resolve_rules_addresses(
    rules: list[SecurityRule],
    address_objects: list[AddressObject],
    address_groups: list[AddressGroup],
) -> list[SecurityRule]:
    """Resolve Security Rules source_addresses and destination_addresses values
    of Address Objects and Address Groups to an actual IP addresses.
    """
    resolver = AddressLookup(address_objects, address_groups)
    errors = []
    attr_pairs = (
        ("source_addresses", "source_addresses_ip"),
        ("destination_addresses", "destination_addresses_ip"),
    )
    for rule in rules:
        for origin_attr, desire_attr in attr_pairs:
            current_value = getattr(rule, origin_attr)
            if not current_value or AnyObj in current_value:
                continue
            try:
                resolved_value = resolver.resolve(current_value)
                if resolved_value:
                    setattr(rule, desire_attr, resolved_value)
            except ValueError as ex:
                logger.debug(ex)
                errors.append(f"rule={rule.name} {origin_attr}={current_value}")

    if errors:
        raise ValueError(
            f"Failed to resolve rules addresses: {' | '.join(errors)}",
        )
    return rules
