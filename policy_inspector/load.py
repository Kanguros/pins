import logging
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar, Union

from policy_inspector.utils import load_csv, load_json

if TYPE_CHECKING:
    from policy_inspector.models import MainModel

logger = logging.getLogger(__name__)

parsers = {
    ".csv": "parse_csv",
    ".json": "parse_json",
}
"""Mapping of file extensions to parser method names."""

loaders = {".json": load_json, ".csv": load_csv}
"""Mapping of file extensions to example loading functions."""

ModelClass = TypeVar("ModelClass", bound="MainModel")
"""Type variable for model classes derived from MainModel."""


def load_from_file(
    model_cls: type[ModelClass], file_path: Union[str, Path]
) -> list[ModelClass]:
    """Load example from a given file and create instances of the specified model class.

    Args:
        model_cls: The model class to instantiate for each example entry.
        file_path: The path to the JSON or CSV file containing the example.

    Returns:
        A list of instances of the specified model class, each initialized
        with example from the file.

    Raises:
        ValueError: If the file extension is unsupported or no parser method
        is found in the model class for the file type.

    Example:
        example = load_from_file(MyModel, 'example.json')
        for item in example:
            print(item)
    """
    file_path = Path(file_path)
    logger.debug(f"Loading {model_cls} from {file_path}")
    suffix = str(file_path.suffix.lower())

    loader = loaders.get(suffix)
    if loader is None:
        raise ValueError(f"Unsupported file type: {suffix}")

    parser_name = parsers.get(suffix)
    if parser_name is None:
        raise ValueError(f"No parser for: {suffix}")
    parser = getattr(model_cls, parser_name, model_cls.model_validate)
    if parser is None:
        logger.debug(f"No parsed found in {model_cls} for {suffix}")

    data = loader(file_path)
    return [parser(item) for item in data]


def load_example(model_cls: type[ModelClass], name: str, suffix: str = ".json") -> list[ModelClass]:
    examples_dir = Path(__file__).parent / "example"
    model_name = model_cls.__name__.lower()
    file_path = examples_dir / f"{model_name}.{name}{suffix}"
    return load_from_file(model_cls, file_path)
