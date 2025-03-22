import csv
import json
from pathlib import Path
from typing import Any, Union


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
