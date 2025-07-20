import logging

from policy_inspector.cli.loader import ScenarioLoader
from policy_inspector.cli.options import verbose_option

try:
    import rich_click as click

    click_group = click.RichGroup
except ImportError:
    import click

    click_group = click.Group

from click import Command

logger = logging.getLogger(__name__)


class VerboseGroup(click_group):
    """Click Group that automatically adds verbose option to all commands."""

    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        self.help_option_names = ["-h", "--help"]
        self.params.append(verbose_option())

    def add_command(self, cmd, name=None):
        """Override to add verbose option to all commands."""
        cmd.params.append(verbose_option())
        super().add_command(cmd, name)


class LazyGroup(VerboseGroup):
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
        self._commands_cache: dict[str, Command] | None = None

    def _load_commands(self) -> dict[str, "Command"]:
        """
        Get all available scenarios, caching the result.

        Returns:
            Dictionary mapping scenario names to scenario classes
        """
        if self._commands_cache is None:
            logger.debug("Discovering scenarios...")
            self._commands_cache = self.loader.load_commands()
            logger.debug(f"Discovered scenarios: {self._commands_cache}")
        return self._commands_cache

    def list_commands(self, ctx: click.Context) -> list[str]:
        """
        List all available scenario commands.

        Args:
            ctx: Click context

        Returns:
            List of scenario command names
        """
        commands = super().list_commands(ctx)
        try:
            scenarios = self._load_commands()
            return commands + sorted(scenarios.keys())
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
            commands_map = self._load_commands()
            command = commands_map.get(name)
            if command:
                return command

        except Exception as e:
            logger.error(f"Failed to create command for scenario '{name}': {e}")
            return None
