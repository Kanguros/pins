"""
Exporter classes for handling different output formats.

This module provides a base Exporter class and built-in export methods
for common formats like JSON, YAML, and CSV.
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class Exporter(ABC):
    """Base class for exporting scenario data to various formats."""

    method_prefix: str = "export_"

    def __init__(self, output_dir: str | Path = "."):
        """
        Initialize the exporter.

        Args:
            output_dir: Directory where exported files will be saved
        """
        self.output_dir = Path(output_dir)
        self.exporters = self._build_exporters_map()

    def _build_exporters_map(self) -> dict[str, Any]:
        """
        Build a map of available export methods.

        Returns:
            Dictionary mapping format names to export methods
        """
        exporters = {}
        for attr_name in dir(self):
            if attr_name.startswith(self.method_prefix) and callable(
                getattr(self, attr_name)
            ):
                format_name = attr_name[len(self.method_prefix) :]
                exporters[format_name] = getattr(self, attr_name)
        return exporters

    def export(
        self, data: Any, formats: list[str], filename_base: str = "export"
    ) -> dict[str, str]:
        """
        Export data to multiple formats.

        Args:
            data: The data to export
            formats: List of export format names
            filename_base: Base filename for exported files

        Returns:
            Dictionary mapping format names to output file paths
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        for export_format in formats:
            try:
                export_method = self.exporters.get(export_format)
                if export_method:
                    output_path = export_method(data, filename_base)
                    results[export_format] = output_path
                    logger.info(
                        f"✓ Exported {export_format.upper()} to: {output_path}"
                    )
                else:
                    # Fallback to JSON if method doesn't exist
                    logger.warning(
                        f"Export method for '{export_format}' not found, falling back to JSON"
                    )
                    output_path = self.export_json(
                        data, f"{filename_base}_{export_format}_fallback"
                    )
                    results[export_format] = output_path

            except Exception as e:
                logger.error(f"Failed to export {export_format}: {e}")
                # Try JSON fallback
                try:
                    output_path = self.export_json(
                        data, f"{filename_base}_{export_format}_error"
                    )
                    results[export_format] = output_path
                    logger.info(
                        f"✓ Exported fallback JSON for {export_format} to: {output_path}"
                    )
                except Exception as fallback_error:
                    logger.error(f"Even JSON fallback failed: {fallback_error}")

        return results

    def save(self, content: str, filename: str) -> str:
        """
        Save content to a file.

        Args:
            content: Content to save
            filename: Filename to save to

        Returns:
            Full path to the saved file
        """
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return str(output_path)

    def export_json(self, data: Any, filename_base: str = "export") -> str:
        """
        Export data as JSON format.

        Args:
            data: Data to export
            filename_base: Base filename

        Returns:
            Path to the exported file
        """
        filename = f"{filename_base}.json"

        # Convert data to JSON-serializable format
        if hasattr(data, "dict"):
            # Pydantic model
            json_data = data.dict()
        elif hasattr(data, "__dict__"):
            # Regular object with attributes
            json_data = self._serialize_object(data)
        else:
            json_data = data

        content = json.dumps(
            json_data, indent=2, default=str, ensure_ascii=False
        )
        return self.save(content, filename)

    def export_yaml(self, data: Any, filename_base: str = "export") -> str:
        """
        Export data as YAML format.

        Args:
            data: Data to export
            filename_base: Base filename

        Returns:
            Path to the exported file
        """
        filename = f"{filename_base}.yaml"

        # Convert data to YAML-serializable format
        if hasattr(data, "dict"):
            yaml_data = data.dict()
        elif hasattr(data, "__dict__"):
            yaml_data = self._serialize_object(data)
        else:
            yaml_data = data

        content = yaml.dump(
            yaml_data, default_flow_style=False, allow_unicode=True
        )
        return self.save(content, filename)

    def export_csv(self, data: Any, filename_base: str = "export") -> str:
        """
        Export data as CSV format.

        Args:
            data: Data to export
            filename_base: Base filename

        Returns:
            Path to the exported file
        """
        import csv
        import io

        filename = f"{filename_base}.csv"

        # Handle different data types
        if isinstance(data, list) and data:
            # List of dictionaries or objects
            output = io.StringIO()

            if isinstance(data[0], dict):
                fieldnames = data[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            elif hasattr(data[0], "__dict__"):
                # List of objects
                first_obj = data[0]
                fieldnames = list(vars(first_obj).keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                for obj in data:
                    writer.writerow(vars(obj))
            else:
                # List of simple values
                writer = csv.writer(output)
                for item in data:
                    writer.writerow([item])

            content = output.getvalue()

        elif isinstance(data, dict):
            # Convert dict to CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Key", "Value"])
            for key, value in data.items():
                writer.writerow([key, str(value)])
            content = output.getvalue()

        else:
            # Fallback: convert to string and save as single-column CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Data"])
            writer.writerow([str(data)])
            content = output.getvalue()

        return self.save(content, filename)

    def _serialize_object(self, obj: Any) -> dict[str, Any]:
        """
        Serialize an object to a dictionary for JSON/YAML export.

        Args:
            obj: Object to serialize

        Returns:
            Dictionary representation of the object
        """
        if hasattr(obj, "__dict__"):
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith("_"):  # Skip private attributes
                    if hasattr(value, "__dict__"):
                        result[key] = self._serialize_object(value)
                    elif isinstance(value, list | tuple):
                        result[key] = [
                            self._serialize_object(item)
                            if hasattr(item, "__dict__")
                            else item
                            for item in value
                        ]
                    elif isinstance(value, dict):
                        result[key] = {
                            k: self._serialize_object(v)
                            if hasattr(v, "__dict__")
                            else v
                            for k, v in value.items()
                        }
                    else:
                        result[key] = value
            return result
        return str(obj)

    @abstractmethod
    def get_available_formats(self) -> list[str]:
        """
        Get list of available export formats for this exporter.

        Returns:
            List of format names
        """
        formats = []
        for attr_name in dir(self):
            if attr_name.startswith(self.method_prefix) and callable(
                getattr(self, attr_name)
            ):
                format_name = attr_name[len(self.method_prefix) :]
                if (
                    format_name != "json"
                ):  # Don't include base methods unless overridden
                    formats.append(format_name)

        # Always include built-in formats
        formats.extend(["json", "yaml", "csv"])
        return sorted(set(formats))


class DefaultExporter(Exporter):
    """Default exporter with common formats."""

    def get_available_formats(self) -> list[str]:
        """Get available export formats."""
        return ["json", "yaml", "csv"]
