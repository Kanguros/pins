"""Test the new panorama_options decorator and updated CLI approach."""

import tempfile
from pathlib import Path

import pytest
import rich_click as click
from click.testing import CliRunner

from policy_inspector.config import (
    export_show_options,
    panorama_options,
    yaml_config_option,
)


def test_panorama_options_decorator():
    """Test that panorama_options decorator adds the correct options."""

    @panorama_options
    @click.command()
    def test_command(
        panorama_hostname: str,
        panorama_username: str,
        panorama_password: str,
        panorama_api_version: str,
        panorama_verify_ssl: bool,
    ):
        """Test command with panorama options."""
        click.echo(f"hostname={panorama_hostname}")
        click.echo(f"username={panorama_username}")
        click.echo(f"password={'***' if panorama_password else 'None'}")
        click.echo(f"api_version={panorama_api_version}")
        click.echo(f"verify_ssl={panorama_verify_ssl}")

    runner = CliRunner()

    # Test with all panorama options
    result = runner.invoke(
        test_command,
        [
            "--panorama-hostname",
            "pan.example.com",
            "--panorama-username",
            "admin",
            "--panorama-password",
            "secret",
            "--panorama-api-version",
            "v10.2",
            "--panorama-verify-ssl",
            "true",
        ],
    )
    assert result.exit_code == 0
    assert "hostname=pan.example.com" in result.output
    assert "username=admin" in result.output
    assert "password=***" in result.output
    assert "api_version=v10.2" in result.output
    assert "verify_ssl=True" in result.output


def test_panorama_options_help():
    """Test that the decorator adds help text for panorama options."""

    @panorama_options
    @click.command()
    def test_command(
        panorama_hostname: str,
        panorama_username: str,
        panorama_password: str,
        panorama_api_version: str,
        panorama_verify_ssl: bool,
    ):
        """Test command."""
        pass

    runner = CliRunner()
    result = runner.invoke(test_command, ["--help"])
    assert result.exit_code == 0
    assert "--panorama-hostname" in result.output
    assert "--panorama-username" in result.output
    assert "--panorama-password" in result.output
    assert "--panorama-api-version" in result.output
    assert "--panorama-verify-ssl" in result.output


def test_combined_decorators_with_yaml():
    """Test combining all decorators with YAML configuration."""

    @click.command()
    @yaml_config_option()
    @panorama_options
    @export_show_options
    @click.option("--threshold", type=int, default=10)
    def test_command(
        panorama_hostname: str,
        panorama_username: str,
        panorama_password: str,
        panorama_api_version: str,
        panorama_verify_ssl: bool,
        export: tuple[str, ...],
        show: tuple[str, ...],
        threshold: int,
    ):
        """Test command with all decorators."""
        click.echo(f"hostname={panorama_hostname}")
        click.echo(f"username={panorama_username}")
        click.echo(f"export={export}")
        click.echo(f"show={show}")
        click.echo(f"threshold={threshold}")

    # Create a temporary config file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write("""
threshold: 25
export:
  - json
  - csv
show:
  - table
panorama:
  hostname: config.example.com
  username: config_user
  api_version: v11.0
  verify_ssl: false
""")
        config_file = f.name

    try:
        runner = CliRunner()

        # Test with config file providing defaults
        result = runner.invoke(
            test_command,
            ["--config", config_file, "--panorama-password", "secret"],
        )
        print(f"Test output: {result.output}")
        assert result.exit_code == 0
        assert "hostname=config.example.com" in result.output
        assert "username=config_user" in result.output
        assert "export=('json', 'csv')" in result.output
        assert "show=('table',)" in result.output
        assert "threshold=25" in result.output

        # Test CLI options override config
        result = runner.invoke(
            test_command,
            [
                "--config",
                config_file,
                "--panorama-hostname",
                "override.example.com",
                "--threshold",
                "50",
                "--export",
                "xml",
            ],
        )
        assert result.exit_code == 0
        assert "hostname=override.example.com" in result.output  # CLI override
        assert "username=config_user" in result.output  # From config
        assert "export=('xml',)" in result.output  # CLI override
        assert "show=('table',)" in result.output  # From config
        assert "threshold=50" in result.output  # CLI override

    finally:
        Path(config_file).unlink()


if __name__ == "__main__":
    pytest.main([__file__])
