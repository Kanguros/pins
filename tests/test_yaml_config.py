"""Test the new YAML configuration approach."""

import tempfile
from pathlib import Path

import pytest
import rich_click as click
from click.testing import CliRunner

from policy_inspector.config import (
    config_option,
    export_options,
    show_options,
)


def test_yaml_config_option_basic():
    """Test basic YAML configuration loading."""

    @config_option(default="test_config.yaml")
    @export_options
    @show_options
    @click.command()
    def test_command(export: tuple[str, ...], show: tuple[str, ...]):
        """Test command."""
        click.echo(f"export={export}")
        click.echo(f"show={show}")

    # Create a temporary config file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write("""
export:
  - json
  - csv
show:
  - table
  - rich
""")
        config_file = f.name

    try:
        runner = CliRunner()

        # Test with config file
        result = runner.invoke(test_command, ["--config", config_file])
        assert result.exit_code == 0
        assert "export=('json', 'csv')" in result.output
        assert "show=('table', 'rich')" in result.output

        # Test that CLI options override config file
        result = runner.invoke(
            test_command,
            ["--config", config_file, "--export", "xml", "--show", "text"],
        )
        assert result.exit_code == 0
        assert "export=('xml',)" in result.output
        assert "show=('text',)" in result.output

    finally:
        Path(config_file).unlink()


def test_yaml_config_option_missing_file():
    """Test behavior when config file doesn't exist."""

    @config_option(default="nonexistent.yaml")
    @export_options
    @show_options
    @click.command()
    def test_command(export: tuple[str, ...], show: tuple[str, ...]):
        """Test command."""
        click.echo(f"export={export}")
        click.echo(f"show={show}")

    runner = CliRunner()

    # Should work fine with missing config file
    result = runner.invoke(test_command, [])
    assert result.exit_code == 0
    assert "export=()" in result.output
    assert "show=()" in result.output


def test_yaml_config_option_invalid_yaml():
    """Test behavior with invalid YAML."""

    @config_option(default="test_config.yaml")
    @export_options
    @show_options
    @click.command()
    def test_command(export: tuple[str, ...], show: tuple[str, ...]):
        """Test command."""
        click.echo(f"export={export}")
        click.echo(f"show={show}")

    # Create a temporary config file with invalid YAML
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write("""
export: [
  - json
  - csv
  invalid: yaml: here
""")
        config_file = f.name

    try:
        runner = CliRunner()

        # Should fail with invalid YAML
        result = runner.invoke(test_command, ["--config", config_file])
        assert result.exit_code == 2
        assert "Invalid YAML in config file" in result.output

    finally:
        Path(config_file).unlink()


def test_comprehensive_config_option():
    """Test the comprehensive config option decorator."""

    @config_option()
    @export_options
    @show_options
    @click.option("--name", default="test")
    @click.command()
    def test_command(name: str, export: tuple[str, ...], show: tuple[str, ...]):
        """Test command."""
        click.echo(f"name={name}")
        click.echo(f"export={export}")
        click.echo(f"show={show}")

    # Create a temporary config file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write("""
name: from_config
export:
  - json
show:
  - table
""")
        config_file = f.name

    try:
        runner = CliRunner()

        # Test with config file providing defaults
        result = runner.invoke(test_command, ["--config", config_file])
        assert result.exit_code == 0
        assert "name=from_config" in result.output
        assert "export=('json',)" in result.output
        assert "show=('table',)" in result.output

        # Test CLI options override config
        result = runner.invoke(
            test_command,
            ["--config", config_file, "--name", "from_cli", "--export", "csv"],
        )
        assert result.exit_code == 0
        assert "name=from_cli" in result.output
        assert "export=('csv',)" in result.output
        assert "show=('table',)" in result.output  # Still from config

    finally:
        Path(config_file).unlink()


if __name__ == "__main__":
    pytest.main([__file__])
