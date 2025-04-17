import csv
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional, TypeVar

if TYPE_CHECKING:
    from policy_inspector.model.base import MainModel

logger = logging.getLogger(__name__)

ModelClass = TypeVar("ModelClass", bound="MainModel")
"""Type variable for model classes derived from MainModel."""

LoaderFunc = Callable[[Path], list[dict]]
ParserFunc = Callable[[dict], ModelClass]


def load_json(
    file_path: Path,
    encoding: str = "utf-8",
) -> list[dict]:
    """Loads JSON file from given file_path and return it's content."""
    return json.loads(file_path.read_text(encoding=encoding))


def load_csv(
    file_path: Path,
    encoding: str = "utf-8",
) -> list[dict]:
    """Loads CSV file from given file_path and return it's content."""
    # csv.field_size_limit(sys.maxsize)
    return list(
        csv.DictReader(file_path.open(encoding=encoding), dialect="excel")
    )


loaders: dict[str, LoaderFunc] = {"json": load_json, "csv": load_csv}
"""Mapping of file extensions to example loading functions."""

parser_suffix: str = "parse_"


def load_model(
    model_cls: type[ModelClass],
    file_path: Path,
    loader_func: Optional[LoaderFunc] = None,
    parser_func: Optional[ParserFunc] = None,
) -> list[ModelClass]:
    """Load given file and create instances of the specified model class.

    Args:
        model_cls: The model class to instantiate for each example entry.
        file_path: The path to the JSON or CSV file containing the example.
        loader_func: Optional function to load ``file_path`` file.
        parser_func: Optional function to parse items from file to ``model_cls``.

    Returns:
        A list of instances of the specified model class.
    """
    ext = file_path.suffix.lower().lstrip(".")

    if not loader_func:
        if ext not in loaders:
            raise ValueError(f"Unsupported file type: {ext}")
        loader_func = loaders[ext]

    items = loader_func(file_path)

    if not parser_func:
        parser_name = f"{parser_suffix}{ext}"
        parser_func = getattr(model_cls, parser_name, None)
        if parser_func is None:
            raise ValueError(f"{model_cls.__name__} lacks {parser_name} method")

    instances = []
    for item in items:
        instances.append(parser_func(item))
    return instances


def save_json(items: list, filename: str) -> None:
    """Save list of objects to a JSON file."""
    if not items:
        logger.warning(f"No items to save to '{filename}'")
        return
    try:
        with open(filename, "w") as f:
            json.dump(items, f, indent=2)
        logger.info(f"✓ Saved {len(items)} items to '{filename}'")
    except Exception as ex:
        logger.error(f"☠ Failed to save to {filename}: {str(ex)}")
        raise
