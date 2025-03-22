import csv
import json
import logging
from pathlib import Path
from typing import Any, Callable, Union

from click import option


def load_json(
    file_path: Union[str, Path], encoding: str = "utf-8"
) -> Union[list[dict], Any]:
    """Loads JSON file from given file_path and return it's content."""
    with open(file_path, encoding=encoding) as file:
        return json.loads(file.read())


def load_csv(
    file_path: Union[str, Path], encoding: str = "utf-8"
) -> Union[list[dict], Any]:
    """Loads CSV file from given file_path and return it's content."""
    with open(file_path, encoding=encoding) as file:
        reader = csv.DictReader(file)
        return list(reader)


def verbose_option(**kwargs: Any) -> Callable:
    def callback(ctx, param, value: bool) -> None:  # noqa: FBT001
        if not value:
            return
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    kwargs.setdefault("is_flag", True)
    kwargs.setdefault("callback", callback)
    kwargs.setdefault("expose_value", False)
    kwargs.setdefault("is_eager", True)
    kwargs.setdefault("help", "Set log messages to DEBUG")
    return option("-v", "--verbose", **kwargs)
