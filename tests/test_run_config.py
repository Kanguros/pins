from pathlib import Path

import pytest
import yaml
from pydantic import SecretStr, ValidationError

from policy_inspector.run_config import RunConfig


def test_minimal_valid_config(tmp_path):
    yaml_content = """
panorama:
    hostname: 5.6.7.8
    username: NameForPan
    password: "Sdds@342_12!"
device_groups: ["DeviceGroup_1"]
scenarios: [ "Shadowing" ]
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content.strip())

    cfg = RunConfig.from_yaml_file(config_file)
    assert cfg.panorama.hostname == "5.6.7.8"
    assert cfg.device_groups == ["DeviceGroup_1"]
    assert cfg.scenarios == ["Shadowing"]


def test_default_values(tmp_path):
    yaml_content = """
panorama:
    hostname: 5.6.7.8
    username: NameForPan
    password: "pass"
device_groups: [dg]
scenarios: [scen]
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)

    cfg = RunConfig.from_yaml_file(config_file)
    assert cfg.panorama.api_version == "v11.1"
    assert cfg.panorama.verify_ssl is False
    assert cfg.continue_on_error is True


def test_optional_continue_on_error(tmp_path):
    yaml_content = """
panorama:
    hostname: 5.6.7.8
    username: user
    password: "pass"
device_groups: [dg]
scenarios: [scen]
continue_on_error: false
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)

    cfg = RunConfig.from_yaml_file(config_file)
    assert cfg.continue_on_error is False


@pytest.mark.parametrize(
    "yaml_content, expected_error",
    [
        (
            "device_groups: [ 'dg' ]\nscenarios: [ 'scen' ]",
            "panorama\n  Field required",
        ),
        (
            """
panorama:
    hostname: 123
    username: test
    password: test
device_groups: ['dg']
scenarios: ['scen']
""",
            "hostname\n  Input should be a valid string",
        ),
        (
            """
panorama:
    hostname: valid
    username: test
    password: test
device_groups: []
scenarios: [scen]
        """,
            "device_groups\n  List should have at least 1 item",
        ),
    ],
)
def test_invalid_configs(tmp_path, yaml_content, expected_error):
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text(yaml_content)

    with pytest.raises(ValidationError) as excinfo:
        RunConfig.from_yaml_file(config_file)
    assert expected_error in str(excinfo.value)


def test_ssl_cert_path(tmp_path):
    yaml_content = """
    panorama:
      hostname: 5.6.7.8
      username: user
      password: "pass"
      verify_ssl: /path/to/cert
    device_groups: [dg]
    scenarios: [scen]
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)

    cfg = RunConfig.from_yaml_file(config_file)
    assert cfg.panorama.verify_ssl == "/path/to/cert"


def test_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        RunConfig.from_yaml_file(Path("nonexistent.yaml"))


def test_invalid_yaml_syntax(tmp_path):
    config_file = tmp_path / "bad.yaml"
    config_file.write_text("panorama: [invalid: yaml")

    with pytest.raises(yaml.parser.ParserError) as excinfo:
        RunConfig.from_yaml_file(config_file)
    assert "while parsing a flow sequence" in str(excinfo.value)


def test_password_obfuscation(tmp_path):
    yaml_content = """
    panorama:
      hostname: host
      username: user
      password: "secret!"
    device_groups: [dg]
    scenarios: [scen]
    """
    config_file = tmp_path / "secret.yaml"
    config_file.write_text(yaml_content)

    cfg = RunConfig.from_yaml_file(config_file)
    assert isinstance(cfg.panorama.password, SecretStr)
    assert "secret!" not in repr(cfg)
    assert "********" in repr(cfg.panorama.password)
