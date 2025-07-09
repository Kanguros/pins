"""Mock Panorama connector for examples and testing."""

import logging
from pathlib import Path
from typing import Literal, Optional

from policy_inspector.model.address_group import AddressGroup
from policy_inspector.model.address_object import AddressObject
from policy_inspector.model.security_rule import SecurityRule
from policy_inspector.utils import load_json

logger = logging.getLogger(__name__)


class MockPanoramaConnector:
    """Mock Panorama connector that reads data from JSON files.

    This connector is used for examples and testing where real Panorama
    connectivity is not available.

    Args:
        data_dir: Directory containing JSON data files
        device_group: Device group name for the mock data
    """

    def __init__(
        self,
        data_dir: Path,
        device_group: str = "mock",
        **kwargs,  # Accept any additional args for compatibility
    ):
        self.data_dir = Path(data_dir)
        self.device_group = device_group
        logger.info(
            f"✓ Mock Panorama connector initialized with data from {data_dir}"
        )

    def get_address_objects(
        self, device_group: Optional[str] = None
    ) -> list[AddressObject]:
        """Retrieve address objects from JSON file.

        Args:
            device_group: Ignored in mock implementation.

        Returns:
            List of ``AddressObject`` instances.
        """
        logger.info("↺ Loading Address Objects from JSON file")
        file_path = self.data_dir / "address_objects.json"

        if not file_path.exists():
            logger.warning(f"Address objects file not found: {file_path}")
            return []

        entries = load_json(file_path)
        if not entries:
            logger.warning("No Address Objects found in file")
            return []

        logger.info(f"✓ Loaded {len(entries)} Address Objects")
        return AddressObject.parse_json(entries)

    def get_address_groups(
        self, device_group: Optional[str] = None
    ) -> list[AddressGroup]:
        """Retrieve address groups from JSON file.

        Args:
            device_group: Ignored in mock implementation.

        Returns:
            List of ``AddressGroup`` instances
        """
        logger.info("↺ Loading Address Groups from JSON file")
        file_path = self.data_dir / "address_groups.json"

        if not file_path.exists():
            logger.warning(f"Address groups file not found: {file_path}")
            return []

        entries = load_json(file_path)
        if not entries:
            logger.warning("No Address Groups found in file")
            return []

        logger.info(f"✓ Loaded {len(entries)} Address Groups")
        return AddressGroup.parse_json(entries)

    def get_security_rules(
        self,
        device_group: Optional[str] = None,
        rulebase: Literal["pre", "post"] = "post",
    ) -> list[SecurityRule]:
        """Retrieve security rules from JSON file.

        Args:
            device_group: Ignored in mock implementation.
            rulebase: Ignored in mock implementation.

        Returns:
            List of ``SecurityRule`` instances.
        """
        logger.info("↺ Loading Security Rules from JSON file")
        file_path = self.data_dir / "policies.json"

        if not file_path.exists():
            logger.warning(f"Security rules file not found: {file_path}")
            return []

        entries = load_json(file_path)
        if not entries:
            logger.warning("No Security Rules found in file")
            return []

        logger.info(f"✓ Loaded {len(entries)} Security Rules")
        return SecurityRule.parse_json(entries)

    def get_device_groups(self) -> list[str]:
        """Return mock device groups.

        Returns:
            List containing the configured device group name.
        """
        return [self.device_group]
