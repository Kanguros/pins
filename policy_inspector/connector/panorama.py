import logging
from typing import Literal, Optional

import urllib3
from requests import RequestException, Session

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
            logger.warning("No SSL was provided")
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
        logger.info("↺ Authenticating to Panorama")
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
            logger.info("✓ Successfully authenticated to Panorama")

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

    def _paginated_api_request(
        self,
        endpoint: str,
        items_key: str = "entry",
        limit: int = 500,
        offset: int = 0,
        max_items: Optional[int] = None,
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
                paginated_endpoint = (
                    f"{endpoint}&limit={limit}&offset={current_offset}"
                )
            else:
                paginated_endpoint = (
                    f"{endpoint}?limit={limit}&offset={current_offset}"
                )

            response_data = self._api_request(paginated_endpoint, "GET")
            items = response_data.get("result", {}).get(items_key, [])
            if isinstance(response_data.get("result", {}), list):
                items = response_data.get("result", [])

            all_items.extend(items)

            total_count = int(
                response_data.get("result", {}).get("@total-count", 0)
            )
            if total_count and current_offset + len(items) >= total_count:
                more_pages = False
            elif len(items) < limit:
                more_pages = False
            else:
                current_offset += limit

            if max_items and len(all_items) >= max_items:
                all_items = all_items[:max_items]
                more_pages = False

            logger.debug(
                f"Retrieved {len(items)} items, total so far: {len(all_items)}"
            )

        return all_items

    def get_address_objects(
        self, device_group: Optional[str] = None
    ) -> list[dict]:
        """Retrieve address objects from Panorama using REST API.

        Args:
            device_group: Name of the Device Group or shared if ``None``.

        Returns:
            List of Address Objects as dict.
        """
        logger.info("↺ Retrieving Address Objects")
        if device_group:
            endpoint = f"Objects/Addresses?location=device-group&device-group={device_group}"
        else:
            endpoint = "Objects/Addresses?location=shared"

        entries = self._paginated_api_request(endpoint)
        if not entries:
            logger.warning("No Address Objects found")
            return []
        logger.info(f"✓ Retrieved {len(entries)} Address Objects")
        return entries

    def get_address_groups(
        self, device_group: Optional[str] = None
    ) -> list[dict]:
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

        entries = self._paginated_api_request(endpoint)
        if not entries:
            logger.warning("No Address Groups found")
            return []
        logger.info(f"✓ Retrieved {len(entries)} Address Groups")
        return entries

    def get_security_rules(
        self,
        device_group: Optional[str] = None,
        rulebase: Literal["pre", "post"] = "post",
    ) -> list[dict]:
        """Retrieve security rules from Panorama using REST API.

        Args:
            device_group: Name of the Device Group of shared if ``None``.
            rulebase: Type of rulebase.

        Returns:
            List of `SecurityRule` instances.
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

        entries = self._paginated_api_request(endpoint)
        if not entries:
            logger.warning("No Security Rules found")
            return []
        logger.info(f"✓ Retrieved {len(entries)} Security Rules")
        return entries
