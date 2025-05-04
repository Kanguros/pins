from pathlib import Path
from typing import Union

from pydantic import BaseModel, Field, SecretStr
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


ScenarioName = str
"""Name of the Scenario"""


class RunConfig(BaseModel):
    panorama: PanoramaConfig
    device_groups: list[str] = Field(..., min_length=1)
    scenarios: list[ScenarioName] = Field(..., min_length=1)
    continue_on_error: bool = True

    @classmethod
    def from_yaml_file(cls, file_path: Path) -> "RunConfig":
        data = safe_load(file_path.read_text())
        return cls(**data)
