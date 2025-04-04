import csv
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar, Union

if TYPE_CHECKING:
    from policy_inspector.models import MainModel

logger = logging.getLogger(__name__)

ModelClass = TypeVar("ModelClass", bound="MainModel")
"""Type variable for model classes derived from MainModel."""


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


class Loader:
    _loaders = {"json": load_json, "csv": load_csv}
    """Mapping of file extensions to example loading functions."""
    parser_suffix: str = "parse_"

    @classmethod
    def load_model(
        cls, model_cls: type[ModelClass], file_path: Path
    ) -> list[ModelClass]:
        """Load given file and create instances of the specified model class.

        Args:
            model_cls: The model class to instantiate for each example entry.
            file_path: The path to the JSON or CSV file containing the example.

        Returns:
            A list of instances of the specified model class.
        """
        ext = file_path.suffix.lower().lstrip(".")

        if ext not in cls._loaders:
            raise ValueError(f"Unsupported file type: {ext}")

        loader = cls._loaders[ext]
        raw_items = loader(file_path)

        parser_name = f"{cls.parser_suffix}{ext}"
        parser_method = getattr(model_cls, parser_name, None)
        if parser_method is None:
            raise ValueError(f"{model_cls.__name__} lacks {parser_name} method")

        return [parser_method(item) for item in raw_items]
