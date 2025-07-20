"""
Unified Scenario base class with integrated exporter and displayer support.

This module provides the unified Scenario class that uses composition with
Exporter and Displayer classes for better separation of concerns.
"""

import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, TypeVar

from policy_inspector.output.displayer import DefaultDisplayer, Displayer
from policy_inspector.output.exporter import DefaultExporter, Exporter
from policy_inspector.panorama import PanoramaConnector

if TYPE_CHECKING:
    import rich_click as click


logger = logging.getLogger(__name__)

ScenarioResults = TypeVar("ScenarioResults")
AnalysisResult = TypeVar("AnalysisResult")


class Scenario:
    """
    Unified base class for defining security scenarios and checks with integrated export/display support.

    Attributes:
        name: Scenario display name.
        panorama: PanoramaConnector instance for data retrieval.
        exporter: Exporter instance for handling exports.
        displayer: Displayer instance for handling display.
        _scenarios: A dict of all registered subclasses of Scenario (for backwards compatibility).
    """

    name: str | None = None
    exporter_class: type[Exporter] = DefaultExporter
    displayer_class: type[Displayer] = DefaultDisplayer
    panorama_class: type[PanoramaConnector] = PanoramaConnector

    def __init__(self, panorama: "PanoramaConnector", **kwargs) -> None:
        """
        Initialize a Scenario instance.

        Args:
            panorama: PanoramaConnector instance for data retrieval.
            **kwargs: Additional keyword arguments for subclass customization.
        """
        self.panorama = panorama

        # Initialize exporter and displayer
        export_dir = kwargs.pop("export_dir", ".")
        self.exporter = self.exporter_class(output_dir=export_dir)
        self.displayer = self.displayer_class()

        # Set remaining kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Storage for execution results
        self._results: ScenarioResults | None = None
        self._analysis: AnalysisResult | None = None

    def __str__(self):
        return self.name or self.__class__.__name__

    def execute(self) -> ScenarioResults:
        """
        Execute the scenario logic.

        Warnings:
            This method must be implemented by subclasses.

        Returns:
            The results of executing.
        """
        raise NotImplementedError("Subclasses must implement execute() method")

    def analyze(self, results: ScenarioResults) -> AnalysisResult:
        """
        Analyze the results obtained from executing a scenario.

        Warnings:
            This method must be implemented by subclasses.

        Args:
            results: The results to analyze.

        Returns:
            The analysis outcome.
        """
        raise NotImplementedError("Subclasses must implement analyze() method")

    def execute_and_analyze(self) -> AnalysisResult:
        """Execute the scenario and analyze the results."""
        logger.info(f"Executing scenario: {self}")
        self._results = self.execute()

        logger.info(f"Analyzing results for scenario: {self}")
        self._analysis = self.analyze(self._results)

        return self._analysis

    def show(self, formats: Iterable[str]) -> None:
        """
        Display scenario results in the given formats.

        Args:
            formats: List of display format names
        """
        if not formats:
            return

        logger.info(f"Displaying results in formats: {', '.join(formats)}")
        self.displayer.display(self, formats)

    def export(
        self,
        formats: Iterable[str],
        output_dir: str | None = None,
    ) -> dict[str, str]:
        """
        Export scenario results in the given formats.

        Args:
            formats: List of export format names
            output_dir: Directory to save exports (overrides instance setting)

        Returns:
            Dictionary mapping format names to output file paths
        """
        if not formats:
            return {}

        exporter = self.exporter_class(output_dir=output_dir)

        filename_base = f"{self.get_scenario_name()}_results"
        logger.info(f"Exporting results in formats: {', '.join(formats)}")

        return exporter.export(self, formats, filename_base)


TPanorama = TypeVar("TPanorama", bound="PanoramaConnector")


def initialize_panorama(panorama_cls: type[TPanorama], **kwargs) -> TPanorama:
    """
    Create a panorama connector from context parameters.

    Args:
        ctx: Click context containing connection parameters

    Returns:
        Panorama connector instance or None if creation fails
    """
    try:
        return panorama_cls(
            hostname=kwargs["panorama_hostname"],
            username=kwargs["panorama_username"],
            password=kwargs["panorama_password"],
            api_version=kwargs.get("panorama_api_version"),
            verify_ssl=kwargs.get("panorama_verify_ssl"),
        )
    except KeyError as e:
        logger.error(f"Missing required connection parameter: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to create Panorama connector: {e}")
        return None


def run_scenario(scenario_cls: type, **kwargs):
    """
    Execute a scenario with the provided options.

    Args:
        ctx: Click context
        scenario_cls: Scenario class to execute
        **kwargs: Command line options
    """
    try:
        export_formats = kwargs.pop("export", ())
        show_formats = kwargs.pop("show", ())
        export_dir = kwargs.pop("export_dir", ".")

        panorama = initialize_panorama(scenario_cls.panorama_class, **kwargs)
        if not panorama:
            click.echo("Error: Failed to create Panorama connector.", err=True)
            return

        scenario = scenario_cls(
            panorama=panorama, export_dir=export_dir, **kwargs
        )

        click.echo(f"Executing scenario: {scenario}")
        scenario.execute_and_analyze()
        scenario.show(show_formats)
        scenario.export(export_formats, export_dir)
        click.echo("Scenario execution completed successfully!")

    except Exception as e:
        logger.error(f"Scenario execution failed: {e}")
        click.echo(f"Error: {e}", err=True)


def get_exporter_displayer_formats(
    scenario: Scenario,
) -> tuple[type[Exporter], type[Displayer]]:
    """
    Helper function to retrieve exporter and displayer formats for a given scenario.

    Args:
        scenario: The Scenario instance.

    Returns:
        A tuple containing the exporter and displayer classes.
    """
    return scenario.exporter_class, scenario.displayer_class
