import logging

from policy_inspector.cli.loader import ScenarioLoader
from policy_inspector.cli.options import config_option, verbose_option

try:
    import rich_click as click

    clickGroup = click.RichGroup
except ImportError:
    import click

    clickGroup = click.Group

logger = logging.getLogger(__name__)



class VerboseGroup(clickGroup):
    """Click Group that automatically adds verbose option to all commands."""

    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        
        self.params.append(verbose_option())
        self.params.append(config_option())

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
