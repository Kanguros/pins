import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING

from policy_inspector.model.address_object import (
    AddressObject,
    AddressObjectIPNetwork,
    AddressObjectIPRange,
)

if TYPE_CHECKING:
    from policy_inspector.model.address_group import AddressGroup

logger = logging.getLogger(__name__)


class Resolver:
    """Process Address Groups into their Address Objects or IP Network object.

    It expands Address Groups (AG) recursively.

    Args:
        address_objects: A list of ``AddressObject``.
        address_groups: A list of ``AddressGroup``.
    """

    def __init__(
        self,
        address_objects: list["AddressObject"],
        address_groups: list["AddressGroup"],
    ):
        self.address_objects: dict[str, AddressObject] = {
            ao.name: ao for ao in address_objects
        }
        self.address_groups: dict[str, set[str]] = {
            ag.name: ag.static for ag in address_groups
        }
        self.cache: dict[str, list[AddressObject]] = {}
        self._resolution_stack: set[str] = set()

    def resolve(self, names: Iterable[str]) -> list["AddressObject"]:
        """Resolve given names.

        Args:
            names: Names of ``Address Groups`` or ``Address Objects``
        """
        result = []
        for name in names:
            result.extend(self._resolve_name(name))
        return result

    def _resolve_name(self, name: str) -> list["AddressObject"]:
        """Resolve single ``name``"""
        if name == "any":
            return []

        if name in self.cache:
            return self.cache[name]

        # Check for circular dependency
        if name in self._resolution_stack:
            raise ValueError(
                f"Circular dependency detected: {name} is already being resolved"
            )

        self._resolution_stack.add(name)
        try:
            try:
                logger.debug(f"Resolving Address Group by name: {name}")
                resolved = []
                for member in self.address_groups[name]:
                    resolved.extend(self._resolve_name(member))
                self.cache[name] = resolved
                return resolved
            except KeyError:
                pass

            try:
                logger.debug(f"Resolving Address Object by name: {name}")
                resolved = [self.address_objects[name]]
                self.cache[name] = resolved
                return resolved
            except KeyError:
                pass

            try:
                logger.debug(
                    f"Creating {AddressObjectIPNetwork} from value: {name}"
                )
                resolved = [AddressObjectIPNetwork(name=name, value=name)]
                self.cache[name] = resolved
                return resolved
            except ValueError:
                pass

            try:
                logger.debug(
                    f"Creating {AddressObjectIPRange} from value: {name}"
                )
                resolved = [AddressObjectIPRange(name=name, value=name)]
                self.cache[name] = resolved
                return resolved
            except ValueError as ex:
                raise ValueError(
                    f"Unknown address object/group: {name}"
                ) from ex
        finally:
            self._resolution_stack.discard(name)
