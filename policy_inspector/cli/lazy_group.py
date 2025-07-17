"""
Dynamic CLI command handler for scenarios.

This module provides the ScenarioCLI class that implements Click's MultiCommand
interface to dynamically create CLI commands for discovered scenarios.
"""

import logging
from typing import Any

import rich_click as click

from policy_inspector.cli.base_group import VerboseGroup
from policy_inspector.cli.loader import ScenarioLoader

logger = logging.getLogger(__name__)


class ScenarioCLI(VerboseGroup):
    """Dynamic CLI handler that creates commands for discovered scenarios."""

    def __init__(self, scenario_directories: list[str] | None = None, **kwargs):
        """
        Initialize the ScenarioCLI.

        Args:
            scenario_directories: List of directories to search for scenarios
            **kwargs: Additional arguments for Click MultiCommand
        """
        super().__init__(**kwargs)
        self.loader = ScenarioLoader(scenario_directories)
        self._scenarios_cache: dict[str, type] | None = None

    def _get_scenarios(self) -> dict[str, type]:
        """
        Get all available scenarios, caching the result.

        Returns:
            Dictionary mapping scenario names to scenario classes
        """
        if self._scenarios_cache is None:
            logger.debug("Discovering scenarios...")
            self._scenarios_cache = self.loader.discover_scenarios()
            logger.debug(f"Discovered scenarios: {self._scenarios_cache}")
        return self._scenarios_cache

    def list_commands(self, ctx: click.Context) -> list[str]:
        """
        List all available scenario commands.

        Args:
            ctx: Click context

        Returns:
            List of scenario command names
        """
        try:
            scenarios = self._get_scenarios()
            return sorted(scenarios.keys())
        except Exception as e:
            logger.error(f"Failed to list scenarios: {e}")
            return []

    def get_command(
        self, ctx: click.Context, name: str
    ) -> click.Command | None:
        """
        Dynamically create a CLI command for the specified scenario.

        Args:
            ctx: Click context
            name: Scenario command name

        Returns:
            Click command or None if scenario not found
        """
        try:
            scenarios = self._get_scenarios()
            scenario_cls = scenarios.get(name)

            if not scenario_cls:
                return None

            return self._create_scenario_command(scenario_cls, name)

        except Exception as e:
            logger.error(f"Failed to create command for scenario '{name}': {e}")
            return None

    def _create_scenario_command(
        self, scenario_cls: type, scenario_name: str
    ) -> click.Command:
        """
        Create a Click command for a scenario class.

        Args:
            scenario_cls: The scenario class
            scenario_name: The scenario command name

        Returns:
            Click command
        """
        # Get scenario information
        scenario_info = self.loader.get_scenario_info(scenario_name)
        help_text = (
            scenario_info["help_text"]
            if scenario_info
            else f"Run {scenario_name} analysis"
        )
        description = (
            scenario_info["description"] if scenario_info else help_text
        )

        # Create the command function
        @click.command(name=scenario_name, help=help_text)
        @click.pass_context
        def scenario_command(ctx: click.Context, **kwargs):
            """Dynamic scenario command."""
            self._execute_scenario(ctx, scenario_cls, **kwargs)

        # Add common options
        scenario_command = self._add_common_options(
            scenario_command, scenario_info
        )

        # Add scenario-specific options
        scenario_command = self._add_scenario_options(
            scenario_command, scenario_cls
        )

        # Update command help
        scenario_command.short_help = description
        scenario_command.help = help_text

        return scenario_command

    def _add_common_options(
        self, command: click.Command, scenario_info: dict[str, Any] | None
    ) -> click.Command:
        """
        Add common options that all scenarios support.

        Args:
            command: Click command to modify
            scenario_info: Scenario information dictionary

        Returns:
            Modified command
        """
        # Export formats
        export_formats = (
            scenario_info.get("export_formats", ["json", "yaml", "csv"])
            if scenario_info
            else ["json", "yaml", "csv"]
        )
        command = click.option(
            "--export",
            multiple=True,
            type=click.Choice(export_formats),
            help="Export formats (can be specified multiple times)",
        )(command)

        # Display formats
        display_formats = (
            scenario_info.get("display_formats", [])
            if scenario_info
            else []
        )
        command = click.option(
            "-d","--display",
            multiple=True,
            type=click.Choice(display_formats),
            default=["text"],
            help="Display formats (can be specified multiple times)",
        )(command)

        # Export directory
        return click.option(
            "--export-dir", default=".", help="Directory to save exported files"
        )(command)

    def _add_scenario_options(
        self, command: click.Command, scenario_cls: type
    ) -> click.Command:
        """
        Add scenario-specific options if the scenario defines them.

        Args:
            command: Click command to modify
            scenario_cls: Scenario class

        Returns:
            Modified command
        """
        if hasattr(scenario_cls, "get_cli_options"):
            try:
                cli_options = scenario_cls.get_cli_options()
                for option in reversed(
                    cli_options
                ):  # Apply in reverse order for correct stacking
                    command = option(command)
            except Exception as e:
                logger.warning(
                    f"Failed to add CLI options for {scenario_cls.__name__}: {e}"
                )

        return command

    def _execute_scenario(
        self, ctx: click.Context, scenario_cls: type, **kwargs
    ):
        """
        Execute a scenario with the provided options.

        Args:
            ctx: Click context
            scenario_cls: Scenario class to execute
            **kwargs: Command line options
        """
        try:
            # Extract common options
            export_formats = kwargs.pop("export", ())
            show_formats = kwargs.pop("show", ())
            export_dir = kwargs.pop("export_dir", ".")

            # Create panorama connector from context parameters
            panorama = self._create_panorama_connector(ctx)
            if not panorama:
                click.echo(
                    "Error: Failed to create Panorama connector.", err=True
                )
                return

            # Create and execute scenario
            scenario = scenario_cls(
                panorama=panorama, export_dir=export_dir, **kwargs
            )

            click.echo(f"Executing scenario: {scenario}")

            # Execute and analyze
            scenario.execute_and_analyze()

            # Display results
            if show_formats:
                scenario.show(show_formats)

            # Export results
            if export_formats:
                exported_files = scenario.export(export_formats, export_dir)
                for format_name, file_path in exported_files.items():
                    click.echo(f"Exported {format_name.upper()}: {file_path}")

            click.echo("Scenario execution completed successfully!")

        except Exception as e:
            logger.error(f"Scenario execution failed: {e}")
            click.echo(f"Error: {e}", err=True)

    def _create_panorama_connector(self, ctx: click.Context):
        """
        Create a panorama connector from context parameters.

        Args:
            ctx: Click context containing connection parameters

        Returns:
            Panorama connector instance or None if creation fails
        """
        if not ctx.obj:
            logger.error("No context object available")
            return None

        try:
            from policy_inspector.panorama import PanoramaConnector

            return PanoramaConnector(
                hostname=ctx.obj["panorama_hostname"],
                username=ctx.obj["panorama_username"],
                password=ctx.obj["panorama_password"],
                api_version=ctx.obj.get("panorama_api_version", "v11.1"),
                verify_ssl=ctx.obj.get("panorama_verify_ssl", False),
            )
        except KeyError as e:
            logger.error(f"Missing required connection parameter: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create Panorama connector: {e}")
            return None


def create_panorama_options() -> list[click.Option]:
    """
    Create common Panorama connection options.

    Returns:
        List of Click options for Panorama connection
    """
    return [
        click.option(
            "--panorama-hostname",
            required=True,
            help="Panorama hostname or IP address",
        ),
        click.option(
            "--panorama-username", required=True, help="Panorama username"
        ),
        click.option(
            "--panorama-password",
            required=True,
            hide_input=True,
            prompt=True,
            help="Panorama password",
        ),
        click.option(
            "--panorama-api-version",
            default="v11.1",
            help="Panorama API version",
        ),
        click.option(
            "--panorama-verify-ssl",
            is_flag=True,
            default=False,
            help="Verify SSL certificates",
        ),
    ]


def add_panorama_options(command: click.Command) -> click.Command:
    """
    Add Panorama connection options to a command.

    Args:
        command: Click command to modify

    Returns:
        Modified command with Panorama options
    """
    for option in reversed(create_panorama_options()):
        command = option(command)
    return command
