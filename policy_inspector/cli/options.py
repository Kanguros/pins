import logging

import rich_click as click

logger = logging.getLogger(__name__)





def panorama_options(f):
    """
    Decorator that adds panorama connection click options to a command.

    These options are for connecting to Panorama:
    - panorama_hostname: str - Panorama hostname/IP
    - panorama_username: str - Username for authentication
    - panorama_password: str - Password for authentication (hidden input)
    - panorama_api_version: str - PAN-OS API version (default: v11.1)
    - panorama_verify_ssl: bool - Whether to verify SSL certificates (default: False)

    Args:
        f: The function to decorate

    Returns:
        The decorated function with panorama options added
    """
    options = [
        click.option(
            "--panorama-verify-ssl",
            type=bool,
            default=False,
            help="Verify SSL certificates",
        ),
        click.option(
            "--panorama-api-version", default="v11.1", help="PAN-OS API version"
        ),
        click.option(
            "--panorama-password", help="Panorama password", hide_input=True
        ),
        click.option("--panorama-username", help="Panorama username"),
        click.option("--panorama-hostname", help="Panorama hostname"),
    ]
    for option in reversed(options):
        f = option(f)

    logger.debug("Panorama options applied: %s", options)
    return f
