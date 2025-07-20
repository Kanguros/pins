"""
Dynamic scenario loader for discovering and loading scenario modules.

This module provides functionality to dynamically discover scenario modules
from various directories and load them for CLI integration.
"""

import importlib
import logging
from pathlib import Path

from click import Command

logger = logging.getLogger(__name__)


class ScenarioLoader:
    """Loads scenario modules dynamically from configured directories."""

    def __init__(self, scenario_directories: list[str] | None = None):
        """
        Initialize the scenario loader.

        Args:
            scenario_directories: List of directory paths to search for scenarios
        """
        self.builtin_commands = Path(__file__).parent.parent / "builtin"
        self.scenario_directories = scenario_directories or []
        self._loaded_scenarios: dict[str, type] = {}

    def discover_scenarios(self) -> dict[str, type]:
        """
        Discover all available scenario classes.

        Returns:
            Dictionary mapping scenario names to scenario classes
        """
        scenarios = {}

        # Load built-in scenarios first
        scenarios.update(self._load_builtin_scenarios())

        # Load scenarios from configured directories
        for directory in self.scenario_directories:
            scenarios.update(self._load_scenarios_from_directory(directory))

        # Cache the results
        self._loaded_scenarios = scenarios
        return scenarios

    def _load_builtin_scenarios(self) -> dict[str, "Command"]:
        """
        Load built-in scenario commands.

        Returns:
            Dictionary mapping scenario names to click commands
        """
        scenarios = {}

        if not self.builtin_commands.exists():
            logger.debug(f"Built-in scenarios directory does not exist: {self.builtin_commands}")
            return scenarios

        for folder in self.builtin_commands.iterdir():
            if not folder.is_dir():
                continue
            module_path = f"policy_inspector.builtin.{folder.name}.cmd"
            scenario_command = self._load_command(module_path, folder.name)
            if scenario_command:
                scenarios[folder.name] = scenario_command
                logger.debug(f"Loaded command from {module_path}")

        return scenarios

    def _load_scenarios_from_directory(self, directory: str) -> dict[str, "Command"]:
        """
        Load scenario commands from a specific directory.

        Args:
            directory: Path to the directory

        Returns:
            Dictionary mapping scenario names to click commands
        """
        scenarios = {}
        dir_path = Path(directory)

        if not dir_path.exists():
            logger.debug(f"Scenario directory does not exist: {directory}")
            return scenarios

        for folder in dir_path.iterdir():
            if not folder.is_dir():
                continue
            logger.debug(f"Loading scenario from folder: {folder.name}")
            module_path = f"{folder.name}.cmd"
            scenario_command = self._load_command(module_path, folder.name)
            if scenario_command:
                scenarios[folder.name] = scenario_command
                logger.debug(f"Loaded command from {module_path}")
        return scenarios

    def _load_command(self, module_path, command_name: str) -> "Command":
        """
        Load a specific command from a module.

        Args:
            module_path: Path to the module
            command_name: Name of the command to load

        Returns:
            Click command instance
        """
        try:
            module = importlib.import_module(module_path)
            command_func = getattr(module, command_name, None)
            if command_func is None:
                logger.warning(f"Command '{command_name}' not found in module '{module_path}'")
                return None
            if not callable(command_func):
                logger.warning(f"'{command_name}' in module '{module_path}' is not callable")
                return None
            if not isinstance(command_func, Command):
                logger.warning(f"'{command_name}' in module '{module_path}' is not a Click command")
                return None
            return command_func
        except ImportError as e:
            logger.error(f"Failed to import module '{module_path}': {e}")
            return None

    def get_available_scenario_names(self) -> list[str]:
        """
        Get list of available scenario names.

        Returns:
            List of scenario names
        """
        if not self._loaded_scenarios:
            self.discover_scenarios()

        return list(self._loaded_scenarios.keys())
