import logging
from typing import Literal, Optional

import urllib3
from requests import RequestException, Session

from policy_inspector.model.address_group import AddressGroup
from policy_inspector.model.address_object import AddressObject
from policy_inspector.model.security_rule import SecurityRule

logger = logging.getLogger(__name__)


class PanoramaConnector:
    """Connect to Panorama and retrieve objects using REST API.

    Args:
        hostname: Panorama hostname or IP address
        username: API username
        password: API password
        port: API port (default: 443)
        verify_ssl: Whether to verify SSL certificates
        api_version: REST API version (default: v1)
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        port: int = 443,
        verify_ssl: bool = False,
        api_version: str = "v1",
        timeout: int = 60,
    ):
        self.hostname = hostname
        self.port = port
        if not verify_ssl:
            logger.debug("! No SSL was provided")
            urllib3.disable_warnings(
                category=urllib3.exceptions.InsecureRequestWarning
            )
        self.verify_ssl = verify_ssl
        self.api_version = api_version
        self.base_url = f"https://{hostname}:{port}/restapi/{api_version}"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.token = None
        self.timeout = timeout
        self.session = Session()

        self._authenticate(username, password)

    def _authenticate(self, username: str, password: str) -> None:
        """Authenticate to Panorama REST API and get token."""
        try:
            response = self.session.post(
                f"https://{self.hostname}:{self.port}/api/?type=keygen",
                data={"user": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.text
            token = data.split("<key>")[1].split("</key>")[0]
            self.token = token
            self.headers["X-PAN-KEY"] = token

        except RequestException as ex:
            error_msg = f"Failed to connect to Panorama. \n{str(ex)}"
            if hasattr(ex, "response") and ex.response:
                error_msg = f"{error_msg}\n{ex.response.text}"
            raise ValueError(error_msg) from ex

    def _api_request(
        self,
        endpoint: str,
        method: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> dict:
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.request(
                method,
                url,
                headers=self.headers,
                params=params,
                verify=self.verify_ssl,
                timeout=self.timeout,
                json=data,
            )
            response.raise_for_status()
            return response.json()

        except RequestException as ex:
            error_msg = f"Panorama API request failed \n{str(ex)}"
            if hasattr(ex, "response") and ex.response:
                error_msg = f"{error_msg}\n{ex.response.text}"
            raise ValueError(error_msg) from ex

    def _get_api_request(
        self,
        endpoint: str,
        items_key: str = "entry",
    ) -> list[dict]:
        response_data = self._api_request(endpoint, "GET")
        return response_data.get("result", {}).get(items_key, [])

    def get_address_objects(
        self, device_group: Optional[str] = None
    ) -> list[AddressObject]:
        """Retrieve address objects from Panorama using REST API.

        Args:
            device_group: Name of the Device Group or shared if ``None``.

        Returns:
            List of ``AddressObject`` instances.
        """
        logger.info("↺ Retrieving Address Objects")
        if device_group:
            endpoint = f"Objects/Addresses?location=device-group&device-group={device_group}"
        else:
            endpoint = "Objects/Addresses?location=shared"

        entries = self._get_api_request(endpoint)
        if not entries:
            logger.warning("No Address Objects found")
            return []
        logger.info(f"✓ Retrieved {len(entries)} Address Objects")
        return AddressObject.parse_json(entries)

    def get_address_groups(
        self, device_group: Optional[str] = None
    ) -> list[AddressGroup]:
        """Retrieve address groups from Panorama using REST API.

        Args:
            device_group: Name of the Device Group of shared if ``None``.

        Returns:
            List of ``AddressGroup`` instances
        """
        logger.info("↺ Retrieving Address Groups")
        if device_group:
            endpoint = f"Objects/AddressGroups?location=device-group&device-group={device_group}"
        else:
            endpoint = "Objects/AddressGroups?location=shared"

        entries = self._get_api_request(endpoint)
        if not entries:
            logger.warning("No Address Groups found")
            return []
        logger.info(f"✓ Retrieved {len(entries)} Address Groups")
        return AddressGroup.parse_json(entries)

    def get_security_rules(
        self,
        device_group: Optional[str] = None,
        rulebase: Literal["pre", "post"] = "post",
    ) -> list[SecurityRule]:
        """Retrieve security rules from Panorama using REST API.

        Args:
            device_group: Name of the Device Group of shared if ``None``.
            rulebase: Type of rulebase.

        Returns:
            List of ``SecurityRule`` instances.
        """
        if rulebase == "pre":
            resource = "Policies/SecurityPreRules"
        else:
            resource = "Policies/SecurityPostRules"
        logger.info("↺ Retrieving Security Rules")
        if device_group:
            endpoint = (
                f"{resource}?location=device-group&device-group={device_group}"
                f"&rulebase={rulebase}"
            )
        else:
            endpoint = f"{resource}?location=shared&rulebase={rulebase}"

        entries = self._get_api_request(endpoint)
        if not entries:
            logger.warning("No Security Rules found")
            return []
        logger.info(f"✓ Retrieved {len(entries)} Security Rules")
        return SecurityRule.parse_json(entries)

    def get_device_groups(self) -> list[str]:
        """Retrieve device groups from Panorama using REST API.

        Returns:
            List of device group names.
        """
        # TODO: Implement device groups retrieval
        pass
