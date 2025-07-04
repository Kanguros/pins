from functools import wraps
from typing import Union

import rich_click as click
import yaml
from pydanclick import from_pydantic
from pydantic import BaseModel, Field, SecretStr


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
    export: tuple[str, ...] = Field(default_factory=tuple)
    show: tuple[str, ...] = Field(tuple("text"))

def yaml_pydantic(model_class, config_option_name='config_file', default_config='config.yaml'):
    def decorator(f):
        @click.option(f'--{config_option_name.replace("_", "-")}', type=click.Path(), default=default_config, show_default=True)
        @from_pydantic(model_class)
        @wraps(f)
        def wrapper(*args, **kwargs):
            config_file = kwargs.pop(config_option_name)
            model_data = kwargs.pop(model_class.__name__.lower())
            try:
                with open(config_file) as f_yaml:
                    yaml_data = yaml.safe_load(f_yaml) or {}
            except FileNotFoundError:
                yaml_data = {}
            # Merge: CLI > YAML
            merged = {**yaml_data, **model_data.model_dump(exclude_unset=True)}
            merged_model = model_class(**merged)
            return f(*args, config=merged_model, **kwargs)
        return wrapper
    return decorator