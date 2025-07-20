"""
Dynamic scenario loader for discovering and loading scenario modules.

This module provides functionality to dynamically discover scenario modules
from various directories and load them for CLI integration.
"""

import importlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING
from click import Command


logger = logging.getLogger(__name__)


def get_builtin_commands_dir() -> list[Path]:
    """Get the directory containing built-in scenario commands."""
    root_path = Path(__file__).parent.parent / "builtin"
    return [p for p in root_path.iterdir() if p.is_dir() and not p.name.startswith("_")]


class ScenarioLoader:
    """Loads scenario modules dynamically from configured directories."""

    def __init__(
        self,
        custom_paths: list[str] | None = None,
        builtin_commands: str = "policy_inspector.builtin",
        command_module: str = "cmd",
    ):
        """
        Initialize the scenario loader.

        Args:
            custom_paths: List of import paths
            builtin_commands: Import path for built-in commands
            command_module: The name of a module with command definitions
        """
        self.custom_paths = custom_paths or []
        self.command_module = command_module
        self.builtin_commands = builtin_commands

        self._loaded_scenarios: dict[str, "Command"] = {}  # noqa: UP037

    def load_commands(self) -> dict[str, "Command"]:
        """
        Discover all available scenario classes.

        Returns:
            Dictionary mapping scenario names to scenario classes

        Raises:
            RuntimeError: If any error occurs during command loading.
        """
        if self._loaded_scenarios:
            logger.debug("Using cached scenarios.")
            return self._loaded_scenarios

        commands = {}
        commands.update(self._load_builtin_scenarios())
        for custom_path in self.custom_paths:
            commands.update(self._load_scenarios_from_directory(custom_path))
        self._loaded_scenarios = commands
        return commands

    def _load_builtin_scenarios(self) -> dict[str, "Command"]:
        """
        Load built-in scenario commands.

        Returns:
            Dictionary mapping scenario names to click commands
        """
        scenarios = {}

        builtin_commands_path = get_builtin_commands_dir()
        for folder in builtin_commands_path:
            logger.info(f"Found scenario directory: {folder.name}")
            module_path = (
                f"{self.builtin_commands}.{folder.name}.{self.command_module}"
            )
            command = self._load_command(module_path, folder.name)
            if command:
                scenarios[folder.name] = command

        return scenarios

    def _load_scenarios_from_directory(
        self, directory: str
    ) -> dict[str, "Command"]:
        """
        Load scenario commands from a specific directory or import path.

        Args:
            directory: Path to the directory or import path

        Returns:
            Dictionary mapping scenario names to click commands

        Raises:
            FileNotFoundError: If the directory does not exist.
            RuntimeError: If any error occurs during command loading.
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
            module_path = f"{directory}.{folder.name}.{self.command_module}"
            scenario_command = self._load_command(module_path, folder.name)
            if scenario_command:
                scenarios[folder.name] = scenario_command
        return scenarios

    def _load_command(self, module_path: str, command_name: str) -> "Command":
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
                logger.warning(
                    f"Command '{command_name}' not found in module '{module_path}'"
                )
                return None
            if not callable(command_func):
                logger.warning(
                    f"'{command_name}' in module '{module_path}' is not callable"
                )
                return None
            if not isinstance(command_func, Command):
                logger.warning(
                    f"'{command_name}' in module '{module_path}' is not a Click command"
                )
                return None
            logger.debug(f"Loaded command {command_name} from {module_path}")
            return command_func
        except ImportError as e:
            logger.error(f"Failed to import module '{module_path}': {e}")
            raise ImportError(f"Error importing module '{module_path}': {e}")
        except Exception as e:
            logger.error(
                f"Unexpected error while loading command '{command_name}' from module '{module_path}': {e}"
            )
            raise RuntimeError(
                f"Error loading command '{command_name}' from module '{module_path}': {e}"
            )

    def get_available_scenario_names(self) -> list[str]:
        """
        Get list of available scenario names.

        Returns:
            List of scenario names
        """
        if not self._loaded_scenarios:
            self.load_commands()

        return list(self._loaded_scenarios.keys())
