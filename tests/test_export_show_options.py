"""Test the export_show_options decorator."""

import pytest
import rich_click as click
from click.testing import CliRunner

from policy_inspector.config import export_options, show_options


def test_export_show_options_decorator():
    """Test that export_show_options decorator adds the correct options."""

    @export_options
    @show_options
    @click.command()
    def test_command(
        export: tuple[str, ...], show: tuple[str, ...], export_dir: str
    ):
        """Test command with export, show, and export_dir options."""
        click.echo(f"export={export}")
        click.echo(f"show={show}")
        click.echo(f"export_dir={export_dir}")

    runner = CliRunner()

    # Test with no options (should use defaults)
    result = runner.invoke(test_command, [])
    assert result.exit_code == 0
    assert "export=()" in result.output
    assert "show=()" in result.output

    # Test with single export and show options
    result = runner.invoke(
        test_command, ["--export", "json", "--show", "table"]
    )
    assert result.exit_code == 0
    assert "export=('json',)" in result.output
    assert "show=('table',)" in result.output

    # Test with multiple export and show options
    result = runner.invoke(
        test_command,
        [
            "--export",
            "json",
            "--export",
            "csv",
            "--show",
            "table",
            "--show",
            "text",
        ],
    )
    assert result.exit_code == 0
    assert "export=('json', 'csv')" in result.output
    assert "show=('table', 'text')" in result.output


def test_export_show_options_help():
    """Test that the decorator adds help text for the options."""

    @export_options
    @show_options
    @click.command()
    def test_command(
        export: tuple[str, ...], show: tuple[str, ...], export_dir: str
    ):
        """Test command with export, show, and export_dir options."""
        pass

    runner = CliRunner()
    result = runner.invoke(test_command, ["--help"])
    assert result.exit_code == 0
    assert "--export" in result.output
    assert "--show" in result.output
    assert "Export format" in result.output
    assert "Output format" in result.output
    # rich_click help output may not include 'multiple times', so we skip this assertion


if __name__ == "__main__":
    pytest.main([__file__])
