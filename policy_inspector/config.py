import logging

import yaml

logger = logging.getLogger(__name__)


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
