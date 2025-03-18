import json
from pathlib import Path
from typing import Any, Union


def load_json(
    file_path: Union[str, Path], encoding: str = "utf-8"
) -> Union[list[dict], Any]:
    """Loads JSON file from given file_path and return it."""
    with open(file_path, encoding=encoding) as f:
        return json.loads(f.read())
