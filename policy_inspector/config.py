import logging

import rich_click as click
import yaml

logger = logging.getLogger(__name__)


def configure_from_yaml(ctx, param, filename):
    """
    Callback for --config option that reads YAML configuration file
    and sets ctx.default_map for Click to use as parameter defaults.

    Args:
        ctx: Click context
        param: The parameter object (not used)
        filename: Path to the YAML configuration file
    """
    if filename is None:
        return

    try:
        with open(filename) as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        # If config file doesn't exist, just continue with no defaults
        return
    except yaml.YAMLError as e:
        raise click.BadParameter(f"Invalid YAML in config file: {e}") from e

    ctx.default_map = {}

    for key, value in data.items():
        if key == "panorama" and isinstance(value, dict):
            for pano_key, pano_value in value.items():
                ctx.default_map[f"panorama_{pano_key}"] = pano_value
        elif isinstance(value, dict):
            ctx.default_map[key] = value
        else:
            if isinstance(value, list):
                value = tuple(value)
            ctx.default_map[key] = value

    logger.debug("Default map set from YAML: %s", ctx.default_map)
    logger.debug("Final ctx.default_map: %s", ctx.default_map)
    print("ctx.default_map:", ctx.default_map)


def config_option(
    config_file_name: str = "--config", default: str = "config.yaml"
):
    """
    Decorator that adds a --config option to read defaults from a YAML file.

    This uses Click's ctx.default_map mechanism to set parameter defaults
    from the configuration file. The configuration file is processed eagerly
    before other options.

    Args:
        config_file_name: The option name (default: "--config")
        default: Default config file name
        help_text: Help text for the option

    Returns:
    """

    def decorator(f):
        return click.option(
            config_file_name,
            type=click.Path(dir_okay=False),
            default=default,
            callback=configure_from_yaml,
            is_eager=True,
            expose_value=False,
            help="Read configuration from YAML file",
            show_default=True,
        )(f)

    return decorator


def show_options(f):
    """Decorator that adds --show click options to a command."""
    options = [
        click.option(
            "-s",
            "--show",
            multiple=True,
            help="Output format (can be specified multiple times)",
        )
    ]
    for option in reversed(options):
        f = option(f)
    return f


def export_options(f):
    """Decorator that adds --export and --export-dir options to a command."""
    options = [
        click.option(
            "-ed",
            "--export-dir",
            default=".",
            type=click.Path(file_okay=False, dir_okay=True),
            show_default=True,
            help="Directory to save exported files (default: current directory)",
        ),
        click.option(
            "-e",
            "--export",
            multiple=True,
            help="Export format (can be specified multiple times)",
        ),
    ]
    for option in reversed(options):
        f = option(f)
    return f


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
