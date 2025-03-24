import csv
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar, Union

if TYPE_CHECKING:
    from policy_inspector.models import MainModel

logger = logging.getLogger(__name__)


def load_json(
    file_path: Path,
    encoding: str = "utf-8",
) -> Union[list[dict], Any]:
    """Loads JSON file from given file_path and return it's content."""
    return json.loads(file_path.read_text(encoding=encoding))


def load_csv(
    file_path: Path,
    encoding: str = "utf-8",
) -> Union[list[dict], Any]:
    """Loads CSV file from given file_path and return it's content."""
    return list(csv.DictReader(file_path.open(encoding=encoding)))


ModelClass = TypeVar("ModelClass", bound="MainModel")
"""Type variable for model classes derived from MainModel."""


class FileHandler:
    _loaders = {"json": load_json, "csv": load_csv}
    """Mapping of file extensions to example loading functions."""

    @classmethod
    def add_loader(cls, extension: str, loader: callable):
        cls._loaders[extension] = loader

    @classmethod
    def load_for_model(
        cls, model_cls: type[ModelClass], file_path: Path
    ) -> list[ModelClass]:
        """Main entry point for loading model data from files"""
        ext = file_path.suffix.lower().lstrip(".")

        if ext not in cls._loaders:
            raise ValueError(f"Unsupported file type: {ext}")

        loader = cls._loaders[ext]
        raw_items = loader(file_path)

        parser_name = f"parse_{ext}"
        parser_method = getattr(model_cls, parser_name, None)
        if parser_method is None:
            raise ValueError(f"{model_cls.__name__} lacks {parser_name} method")

        return [parser_method(item) for item in raw_items]


def load_from_file(
    model_cls: type[ModelClass], file_path: Path
) -> list[ModelClass]:
    """Load example from a given file and create instances of the specified model class.

    Args:
        model_cls: The model class to instantiate for each example entry.
        file_path: The path to the JSON or CSV file containing the example.

    Returns:
        A list of instances of the specified model class, each initialized
        with example from the file.

    Example:
        example = load_from_file(MyModel, 'example.json')
        for item in example:
            print(item)

    """
    return FileHandler.load_for_model(model_cls, file_path)


def get_example_file_path(
    model_cls: type[ModelClass],
    dir_name: str,
    suffix: str = "json",
) -> Path:
    dir_name = str(dir_name).replace("example", "").strip()
    examples_dir = Path(__file__).parent / "example" / dir_name
    return examples_dir / f"{model_cls.__name__.lower()}.{suffix}"
