import json
import logging
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.logging import RichHandler


def load_json(file_path: Path) -> Any:
    """
    Load JSON data from a file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data
    """
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def load_jinja_template(template_dir: Path, template_name: str):
    """
    Load a Jinja2 template from the current directory.
    """
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["enumerate"] = enumerate
    env.globals["getattr"] = getattr
    return env.get_template(template_name)


def config_logger(
    logger_name: str = "policy_inspector",
    default_level: str = "INFO",
    log_format: str = "%(message)s",
    date_format: str = "[%X]",
) -> None:
    """
    Configure ``logger`` with ``RichHandler``

    Args:
        logger: Instance of a ``logging.Logger``
        level: Default level of a ``logger``.
        log_format: Logs format.
        date_format: Date format in logs.
    """
    rich_handler = RichHandler(
        rich_tracebacks=True,
        show_path=False,
        show_time=False,
        show_level=False,
        omit_repeated_times=False,
    )
    rich_handler.enable_link_path = True
    formatter = logging.Formatter(log_format, date_format, "%")
    rich_handler.setFormatter(formatter)

    main_logger = logging.getLogger(logger_name)
    main_logger.handlers = [rich_handler]
    main_logger.setLevel(logging.INFO)
