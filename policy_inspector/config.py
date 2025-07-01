from pathlib import Path
from typing import Union

from pydantic import BaseModel, SecretStr
from yaml import safe_load


class PanoramaConfig(BaseModel):
    hostname: str
    """Panorama address"""
    username: str
    """Privileged used to access Panorama"""
    password: SecretStr
    """Password for a ``username``"""
    api_version: str = "v11.1"
    """PAN-OS version"""
    verify_ssl: Union[bool, str] = False
    """Default SSL verification setting"""


class Config(BaseModel):
    panorama: PanoramaConfig

    @classmethod
    def from_yaml_file(cls, file_path: Path) -> "Config":
        data = safe_load(file_path.read_text())
        if data is None:
            data = {}
        return cls(**data)
