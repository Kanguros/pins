from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError
from yaml.parser import ParserError

from policy_inspector.config import Config


def test_minimal_valid_config(tmp_path):
    yaml_content = """
panorama:
    hostname: 5.6.7.8
    username: NameForPan
    password: "Sdds@342_12!"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content.strip())

    cfg = Config.from_yaml_file(config_file)
    assert cfg.panorama.hostname == "5.6.7.8"


def test_default_values(tmp_path):
    yaml_content = """
panorama:
    hostname: 5.6.7.8
    username: NameForPan
    password: "pass"
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)

    cfg = Config.from_yaml_file(config_file)
    assert cfg.panorama.api_version == "v11.1"
    assert cfg.panorama.verify_ssl is False


@pytest.mark.parametrize(
    "yaml_content, expected_error",
    [
        (
            "",
            "panorama\n  Field required",
        ),
        (
            """
panorama:
    hostname: 123
    username: test
    password: test
""",
            "hostname\n  Input should be a valid string",
        ),
    ],
)
def test_invalid_configs(tmp_path, yaml_content, expected_error):
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text(yaml_content)

    with pytest.raises(ValidationError) as excinfo:
        Config.from_yaml_file(config_file)
    assert expected_error in str(excinfo.value)


def test_ssl_cert_path(tmp_path):
    yaml_content = """
    panorama:
      hostname: 5.6.7.8
      username: user
      password: "pass"
      verify_ssl: /path/to/cert
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)

    cfg = Config.from_yaml_file(config_file)
    assert cfg.panorama.verify_ssl == "/path/to/cert"


def test_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        Config.from_yaml_file(Path("nonexistent_file.yaml"))


def test_invalid_yaml_syntax(tmp_path):
    config_file = tmp_path / "bad.yaml"
    config_file.write_text("panorama: [invalid: yaml")

    with pytest.raises(ParserError) as excinfo:
        Config.from_yaml_file(config_file)
    assert "while parsing a flow sequence" in str(excinfo.value)


def test_password_obfuscation(tmp_path):
    yaml_content = """
    panorama:
      hostname: host
      username: user
      password: "secret!"
    """
    config_file = tmp_path / "secret.yaml"
    config_file.write_text(yaml_content)

    cfg = Config.from_yaml_file(config_file)
    assert isinstance(cfg.panorama.password, SecretStr)
    assert "secret!" not in repr(cfg)
    assert "********" in repr(cfg.panorama.password)
