import logging

import rich_click as click
import yaml

logger = logging.getLogger(__name__)





def show_options(f):
    """Decorator that adds --show click options to a command."""
    options = [
        click.option(
            "-d",
            "--display",
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





def get_scenario_directories_from_config(
    config_file: str = "config.yaml",
) -> list[str]:
    """
    Get scenario directories from configuration file.

    Args:
        config_file: Path to the configuration file

    Returns:
        List of scenario directory paths
    """
    try:
        with open(config_file) as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.debug(
            f"Config file '{config_file}' not found, using default scenario directories"
        )
        return []
    except yaml.YAMLError as e:
        logger.warning(f"Invalid YAML in config file: {e}")
        return []

    scenarios = data.get("scenarios", [])
    if isinstance(scenarios, list):
        return [str(path) for path in scenarios]
    if isinstance(scenarios, str):
        return [scenarios]

    logger.warning(
        f"Invalid scenarios configuration: expected list or string, got {type(scenarios)}"
    )
    return []
