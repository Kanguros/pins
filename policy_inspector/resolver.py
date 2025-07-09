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


class CircularDependencyError(ValueError):
    """Raised when a circular dependency is detected in address groups."""
    pass


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

    def resolve(self, names: Iterable[str]) -> list["AddressObject"]:
        """Resolve given names.

        Args:
            names: Names of ``Address Groups`` or ``Address Objects``
        """
        result = []
        for name in names:
            result.extend(self._resolve_name(name, set()))
        return result

    def _resolve_name(self, name: str, path: set[str]) -> list["AddressObject"]:
        """Resolve single ``name``"""
        if name == "any":
            return []

        # Check for circular dependency
        if name in path:
            raise CircularDependencyError(
                f"Circular dependency detected in address group resolution: {' -> '.join(path)} -> {name}"
            )

        if name in self.cache:
            return self.cache[name]

        try:
            logger.debug(f"Resolving Address Group by name: {name}")
            resolved = []
            # Add current name to path before recursing
            new_path = path | {name}
            for member in self.address_groups[name]:
                resolved.extend(self._resolve_name(member, new_path))
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
            logger.debug(f"Creating {AddressObjectIPRange} from value: {name}")
            resolved = [AddressObjectIPRange(name=name, value=name)]
            self.cache[name] = resolved
            return resolved
        except ValueError as ex:
            raise ValueError(f"Unknown address object/group: {name}") from ex
