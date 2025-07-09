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


class AppConfig(BaseModel):
    panorama: PanoramaConfig
    export: tuple[str, ...] = Field(default_factory=tuple)
    show: tuple[str, ...] = Field(tuple("text"))

    @classmethod
    def from_yaml_file(cls, file_path: str) -> "AppConfig":
        """Load configuration from a YAML file."""
        try:
            with open(file_path) as f:
                data = yaml.safe_load(f) or {}
        except FileNotFoundError as ex:
            raise FileNotFoundError(
                f"Configuration file {file_path} not found."
            ) from ex
        except yaml.YAMLError:
            raise

        return cls(**data)

    @classmethod
    def option(
        cls, config_option_name="config_file", default_config="config.yaml"
    ):
        def decorator(f):
            @click.option(
                f"--{config_option_name.replace('_', '-')}",
                type=click.Path(),
                default=default_config,
                show_default=True,
            )
            @from_pydantic(cls)
            @wraps(f)
            def wrapper(*args, **kwargs):
                config_file = kwargs.pop(config_option_name)
                model_data = kwargs.pop(cls.__name__.lower())
                try:
                    yaml_data = cls.from_yaml_file(config_file)
                except FileNotFoundError:
                    yaml_data = {}
                merged = cls(
                    **{
                        **yaml_data,
                        **model_data.model_dump(exclude_unset=True),
                    }
                )
                return f(*args, config=merged, **kwargs)

            return wrapper

        return decorator
