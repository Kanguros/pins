"""
Dynamic scenario loader for discovering and loading scenario modules.

This module provides functionality to dynamically discover scenario modules
from various directories and load them for CLI integration.
"""

import importlib
import logging
import pkgutil
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ScenarioLoader:
    """Loads scenario modules dynamically from configured directories."""

    def __init__(self, scenario_directories: list[str] | None = None):
        """
        Initialize the scenario loader.

        Args:
            scenario_directories: List of directory paths to search for scenarios
        """
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

    def _load_builtin_scenarios(self) -> dict[str, type]:
        """
        Load scenarios from the built-in scenarios module.

        Returns:
            Dictionary mapping scenario names to scenario classes
        """
        scenarios = {}

        try:
            # Test if scenarios package is available
            import importlib.util

            if importlib.util.find_spec("policy_inspector.scenarios"):
                # Import to trigger registration
                import policy_inspector.scenarios  # noqa: F401

            # Load scenarios through dynamic discovery
            try:
                scenarios.update(self._load_scenarios_dynamic())
                logger.info(f"Loaded {len(scenarios)} scenarios")
            except Exception as e:
                logger.debug(f"Error loading scenarios: {e}")

        except ImportError as e:
            logger.debug(f"Error importing scenarios package: {e}")

        return scenarios

    def _load_scenarios_from_directory(self, directory: str) -> dict[str, type]:
        """
        Load scenarios from a specific directory.

        Args:
            directory: Path to directory containing scenario modules

        Returns:
            Dictionary mapping scenario names to scenario classes
        """
        scenarios = {}
        dir_path = Path(directory)

        if not dir_path.exists():
            logger.debug(f"Scenario directory does not exist: {directory}")
            return scenarios

        logger.debug(f"Loading scenarios from directory: {directory}")

        try:
            # Add directory to Python path temporarily
            import sys

            if str(dir_path.absolute()) not in sys.path:
                sys.path.insert(0, str(dir_path.absolute()))

            # Discover and import Python modules in the directory
            for module_info in pkgutil.iter_modules([str(dir_path)]):
                try:
                    module = importlib.import_module(module_info.name)
                    scenarios.update(
                        self._extract_scenarios_from_module(module)
                    )
                except Exception as e:
                    logger.debug(
                        f"Error loading module {module_info.name}: {e}"
                    )

        except Exception as e:
            logger.debug(f"Error loading scenarios from {directory}: {e}")

        return scenarios

    def _extract_scenarios_from_module(self, module) -> dict[str, type]:
        """
        Extract scenario classes from a module.

        Args:
            module: The imported module to inspect

        Returns:
            Dictionary mapping scenario names to scenario classes
        """
        scenarios = {}

        try:
            from policy_inspector.scenario import Scenario

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, Scenario)
                    and attr is not Scenario
                ):
                    scenario_name = attr.get_scenario_name()
                    scenarios[scenario_name] = attr
                    logger.debug(f"Found scenario: {scenario_name}")

        except ImportError:
            logger.debug("Scenario base class not available")
        except Exception as e:
            logger.debug(f"Error extracting scenarios from module: {e}")

        return scenarios

    def get_scenario_class(self, scenario_name: str) -> type | None:
        """
        Get a scenario class by name.

        Args:
            scenario_name: Name of the scenario

        Returns:
            Scenario class or None if not found
        """
        if not self._loaded_scenarios:
            self.discover_scenarios()

        return self._loaded_scenarios.get(scenario_name)

    def get_available_scenario_names(self) -> list[str]:
        """
        Get list of available scenario names.

        Returns:
            List of scenario names
        """
        if not self._loaded_scenarios:
            self.discover_scenarios()

        return list(self._loaded_scenarios.keys())

    def _get_scenario_name_from_class(self, cls: type) -> str:
        """
        Get scenario name from class.

        Args:
            cls: Scenario class

        Returns:
            Scenario name
        """
        if hasattr(cls, "get_scenario_name"):
            return cls.get_scenario_name()

        # Fallback to class name conversion
        name = cls.__name__
        if name.endswith("Scenario"):
            name = name[:-8]  # Remove 'Scenario' suffix

        # Convert CamelCase to snake_case
        import re

        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    def get_scenario_info(self, scenario_name: str) -> dict[str, Any] | None:
        """
        Get information about a specific scenario.

        Args:
            scenario_name: Name of the scenario

        Returns:
            Dictionary with scenario information or None if not found
        """
        scenario_cls = self.get_scenario_class(scenario_name)
        if not scenario_cls:
            return None

        info = {
            "name": scenario_name,
            "class_name": scenario_cls.__name__,
            "module": scenario_cls.__module__,
            "description": self._get_scenario_description(scenario_cls),
            "help_text": self._get_scenario_help(scenario_cls),
        }

        # Add available formats if possible
        try:
            info["export_formats"] = scenario_cls.exporter_class.get_available_formats()
            info["display_formats"] = scenario_cls.displayer_class.get_available_formats()
        except Exception as e:
            logger.debug(f"Could not get format info for {scenario_name}: {e}")

        return info

    def _get_scenario_description(self, cls: type) -> str:
        """Get scenario description from class."""
        # Try class method first
        if hasattr(cls, "get_description") and callable(cls.get_description):
            try:
                # Try calling as class method first
                return cls.get_description()
            except TypeError:
                # If it fails, it's probably an instance method
                pass

        # Fall back to docstring
        if cls.__doc__:
            return cls.__doc__.strip().split("\n")[0]

        return f"Analysis scenario: {cls.__name__}"

    def _get_scenario_help(self, cls: type) -> str:
        """Get scenario help text from class."""
        # Try class method first
        if hasattr(cls, "get_help_text") and callable(cls.get_help_text):
            try:
                # Try calling as class method first
                return cls.get_help_text()
            except TypeError:
                # If it fails, it's probably an instance method
                pass

        return cls.__doc__ or f"Analysis scenario: {cls.__name__}"

    def _load_scenarios_dynamic(self) -> dict[str, type]:
        """
        Dynamically load scenarios through module discovery.

        Returns:
            Dictionary mapping scenario names to scenario classes
        """
        scenarios = {}

        # Import the scenario base class
        try:
            from policy_inspector.scenario import Scenario
        except ImportError:
            logger.debug("Scenario class not available")
            return scenarios

        # Discover scenario modules in built-in scenarios directory
        import importlib.util
        import os

        # Get the scenarios directory
        scenarios_dir = os.path.join(os.path.dirname(__file__), "scenarios")

        if os.path.exists(scenarios_dir):
            for root, _dirs, files in os.walk(scenarios_dir):
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        file_path = os.path.join(root, file)
                        module_name = f"policy_inspector.scenarios.{os.path.relpath(file_path, scenarios_dir).replace(os.sep, '.')[:-3]}"

                        try:
                            spec = importlib.util.spec_from_file_location(
                                module_name, file_path
                            )
                            if spec and spec.loader:
                                module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module)

                                # Find all Scenario subclasses in the module
                                for attr_name in dir(module):
                                    attr = getattr(module, attr_name)
                                    if (
                                        isinstance(attr, type)
                                        and issubclass(attr, Scenario)
                                        and attr is not Scenario
                                    ):
                                        scenario_name = attr.get_scenario_name()
                                        scenarios[scenario_name] = attr
                                        logger.debug(
                                            f"Discovered scenario: {scenario_name}"
                                        )

                        except Exception as e:
                            logger.debug(
                                f"Error loading module {module_name}: {e}"
                            )

        return scenarios
