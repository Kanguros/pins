import logging
from typing import Optional, Literal

import requests
from requests import RequestException

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
            logger.warning(f"No SSL was provided")
            import urllib3
            urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
        self.verify_ssl = verify_ssl
        self.api_version = api_version
        self.base_url = f"https://{hostname}:{port}/restapi/{api_version}"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.token = None
        self.timeout = timeout

        self._authenticate(username, password)

    def _authenticate(self, username: str, password: str) -> None:
        """Authenticate to Panorama REST API and get token."""
        logger.info(f"↺ Authenticating to Panorama REST API at {self.hostname}")
        try:
            auth_endpoint = f"{self.base_url}/auth"
            auth_payload = {
                "username": username,
                "password": password
            }
            response = requests.post(
                auth_endpoint,
                json=auth_payload,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            if "result" in data and "key" in data["result"]:
                self.token = data["result"]["key"]
                self.headers["X-PAN-KEY"] = self.token
                logger.info("✓ Successfully authenticated to Panorama REST API")
            else:
                raise Exception("Authentication failed: No token in response")

        except RequestException as ex:
            logger.error(f"☠ Failed to connect to Panorama: {str(ex)}")
            if hasattr(ex, "response") and ex.response:
                logger.error(f"Response: {ex.response.text}")
            raise

    def _api_request(
            self,
            endpoint: str,
            method: str,
            params: Optional[dict] = None,
            data: Optional[dict] = None
    ) -> dict:
        if not self.token:
            raise Exception("Not authenticated to Panorama")
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.request(
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

        except requests.exceptions.RequestException as ex:
            logger.error(f"☠ API request failed: {str(ex)}")
            if hasattr(ex, "response") and ex.response:
                logger.error(f"☠ Response: {ex.response.text}")
            raise

    def _paginated_api_request(
            self,
            endpoint: str,
            items_key: str = "entry",
            limit: int = 500,
            offset: int = 0,
            max_items: Optional[int] = None
    ) -> list[dict]:
        """Make paginated API requests to handle large result sets.

        Args:
            endpoint: API endpoint
            items_key: Key in the response that contains the items
            limit: Items per page
            offset: Starting offset
            max_items: Maximum total items to retrieve (None for all)

        Returns:
            List of all items from paginated responses
        """
        all_items = []
        current_offset = offset
        more_pages = True

        while more_pages:
            if "?" in endpoint:
                paginated_endpoint = f"{endpoint}&limit={limit}&offset={current_offset}"
            else:
                paginated_endpoint = f"{endpoint}?limit={limit}&offset={current_offset}"

            response_data = self._api_request("GET", paginated_endpoint)

            # Extract items from response with proper path to results
            items = response_data.get("result", {}).get(items_key, [])
            # Handle case where result might be a list directly
            if isinstance(response_data.get("result", {}), list):
                items = response_data.get("result", [])

            all_items.extend(items)

            # Check if we need to get more pages based on API response
            total_count = response_data.get("result", {}).get("@total-count", 0)
            if total_count and current_offset + len(items) >= total_count:
                more_pages = False
            elif len(items) < limit:
                more_pages = False
            else:
                current_offset += limit

            # Check if we've reached the maximum requested items
            if max_items and len(all_items) >= max_items:
                all_items = all_items[:max_items]
                more_pages = False

            logger.debug(f"Retrieved {len(items)} items, total so far: {len(all_items)}")

        return all_items

    def get_address_objects(self, device_group: Optional[str] = None) -> list[AddressObject]:
        """Retrieve address objects from Panorama using REST API.

        Args:
            device_group: Name of the Device Group of shared if ``None``.

        Returns:
            List of ``AddressObject`` instances
        """
        logger.info("↺ Retrieving Address Objects from Panorama")

        if device_group:
            endpoint = f"Objects/Addresses?location=device-group&device-group={device_group}"
        else:
            endpoint = "Objects/Addresses?location=shared"

        try:
            entries = self._paginated_api_request(endpoint)
            if not entries:
                logger.info("No address objects found")
                return []
            logger.info(f"✓ Retrieved {len(entries)} address objects")
            return list(map(AddressObject.parse_json, entries))

        except Exception as e:
            logger.error(f"☠ Failed to retrieve address objects: {str(e)}")
            raise

    def get_address_groups(self, device_group: Optional[str] = None) -> list[AddressGroup]:
        """Retrieve address groups from Panorama using REST API.

        Args:
            device_group: Name of the Device Group of shared if ``None``.

        Returns:
            List of ``AddressGroup`` instances
        """
        logger.info("↺ Retrieving Address Groups from Panorama")

        if not device_group:
            endpoint = "Objects/AddressGroups?location=shared"
        else:
            endpoint = f"Objects/AddressGroups?location=device-group&device-group={device_group}"

        try:
            entries = self._paginated_api_request(endpoint)
            if not entries:
                logger.info("No address groups found")
                return []
            logger.info(f"✓ Retrieved {len(entries)} address groups")
            return list(map(AddressGroup.parse_json, entries))

        except Exception as e:
            logger.error(f"☠ Failed to retrieve Address Groups: {str(e)}")
            raise

    def get_security_rules(self,
                           device_group: Optional[str] = None,
                           rulebase: Literal["pre-rulebase", "post-rulebase"] = "post-rulebase") -> list[SecurityRule]:
        """Retrieve security rules from Panorama using REST API.

        Args:
            device_group: Name of the Device Group of shared if ``None``.
            rulebase: Type of rulebase.

        Returns:
            List of `SecurityRule` instances.
        """
        logger.info("↺ Retrieving security rules from Panorama")

        logger.info(f"↺ Retrieving security rules")
        if device_group:
            endpoint = (f"Policies/SecurityRules?location=device-group&device-group={device_group}"
                        f"&rulebase={rulebase}")
        else:
            endpoint = f"Policies/SecurityRules?location=shared&rulebase={rulebase}"

        try:
            entries = self._paginated_api_request(endpoint)
            if not entries:
                logger.info(f"No rules found in {rulebase}")
                return []
            logger.info(f"✓ Retrieved {len(entries)} security rules")
            return list(map(SecurityRule.parse_json, entries))

        except Exception as e:
            logger.error(f"☠ Failed to retrieve rules: {str(e)}")
            raise
