"""
Unified Scenario base class with integrated exporter and displayer support.

This module provides the unified Scenario class that uses composition with
Exporter and Displayer classes for better separation of concerns.
"""

import logging
from typing import TYPE_CHECKING, Any, TypeVar

from policy_inspector.displayer import DefaultDisplayer, Displayer
from policy_inspector.exporter import DefaultExporter, Exporter

if TYPE_CHECKING:
    import rich_click as click

    from policy_inspector.panorama import PanoramaConnector

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

    _scenarios: dict[str, type["Scenario"]] = {}

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

    def __init_subclass__(cls, **kwargs) -> None:
        """Registers subclasses automatically in the `_scenarios` dict for backwards compatibility."""
        super().__init_subclass__(**kwargs)
        cls._scenarios[str(cls)] = cls

    def __str__(self):
        return self.name or self.__class__.__name__

    @classmethod
    def get_scenario_name(cls) -> str:
        """
        Get the scenario name for CLI registration.

        Returns:
            Snake_case name derived from class name
        """
        if cls.name:
            return cls.name.lower().replace(" ", "_").replace("-", "_")

        # Convert CamelCase to snake_case
        name = cls.__name__
        if name.endswith("Scenario"):
            name = name[:-8]  # Remove 'Scenario' suffix

        # Convert CamelCase to snake_case
        import re

        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    @classmethod
    def get_cli_options(cls) -> list["click.Option"]:
        """
        Get CLI options specific to this scenario.

        Override this method in subclasses to define scenario-specific CLI options.

        Returns:
            List of Click option decorators
        """
        return []

    def get_available_export_formats(self) -> list[str]:
        """
        Get available export formats for this scenario.

        Returns:
            List of available export format names
        """
        return self.exporter.get_available_formats()

    def get_available_display_formats(self) -> list[str]:
        """
        Get available display formats for this scenario.

        Returns:
            List of available display format names
        """
        return self.displayer.get_available_formats()

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

    def get_data_for_export(self) -> Any:
        """
        Get data ready for export.

        Override this method to customize what data gets exported.
        By default, returns the analysis results.

        Returns:
            Data to be exported
        """
        return self._analysis if self._analysis is not None else self._results

    def get_data_for_display(self) -> Any:
        """
        Get data ready for display.

        Override this method to customize what data gets displayed.
        By default, returns the analysis results.

        Returns:
            Data to be displayed
        """
        return self._analysis if self._analysis is not None else self._results

    def show(self, formats: list[str] | tuple[str, ...]) -> None:
        """
        Display scenario results in the given formats.

        Args:
            formats: List of display format names
        """
        if not formats:
            return

        data = self.get_data_for_display()
        if data is None:
            logger.warning(
                "No data available for display. Run execute_and_analyze() first."
            )
            return

        logger.info(f"Displaying results in formats: {', '.join(formats)}")
        self.displayer.display(data, list(formats))

    def export(
        self,
        formats: list[str] | tuple[str, ...],
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

        data = self.get_data_for_export()
        if data is None:
            logger.warning(
                "No data available for export. Run execute_and_analyze() first."
            )
            return {}

        # Use provided output_dir or create new exporter if needed
        exporter = self.exporter
        if output_dir and output_dir != str(self.exporter.output_dir):
            exporter = self.exporter_class(output_dir=output_dir)

        filename_base = f"{self.get_scenario_name()}_results"
        logger.info(f"Exporting results in formats: {', '.join(formats)}")

        return exporter.export(data, list(formats), filename_base)

    def get_help_text(self) -> str:
        """
        Get help text for this scenario.

        Returns:
            Help text describing the scenario
        """
        return self.__doc__ or f"Analysis scenario: {self}"

    def get_description(self) -> str:
        """
        Get a brief description of this scenario.

        Returns:
            Brief description
        """
        if self.__doc__:
            # Return first line of docstring
            return self.__doc__.strip().split("\n")[0]
        return f"Analysis scenario: {self}"
