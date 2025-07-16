"""
Displayer classes for handling different terminal output formats.

This module provides a base Displayer class and built-in display methods
for common formats like JSON, table, and text output.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class Displayer(ABC):
    """Base class for displaying scenario data in various terminal formats."""

    method_prefix: str = "display_"

    def display(self, data: Any, formats: list[str]) -> None:
        """
        Display data in multiple formats to the terminal.

        Args:
            data: The data to display
            formats: List of display format names
        """
        for display_format in formats:
            try:
                display_method = getattr(
                    self, f"{self.method_prefix}{display_format}", None
                )
                if display_method:
                    display_method(data)
                else:
                    # Fallback to JSON if method doesn't exist
                    logger.warning(
                        f"Display method for '{display_format}' not found, falling back to JSON"
                    )
                    self.display_json(data)

            except Exception as e:
                logger.error(f"Failed to display {display_format}: {e}")
                # Try JSON fallback
                try:
                    self.display_json(data)
                except Exception as fallback_error:
                    logger.error(f"Even JSON fallback failed: {fallback_error}")
                    print(f"Error displaying data: {str(data)}")

    def display_json(self, data: Any) -> None:
        """
        Display data as formatted JSON.

        Args:
            data: Data to display
        """
        # Convert data to JSON-serializable format
        if hasattr(data, "dict"):
            # Pydantic model
            json_data = data.dict()
        elif hasattr(data, "__dict__"):
            # Regular object with attributes
            json_data = self._serialize_object(data)
        else:
            json_data = data

        json_str = json.dumps(
            json_data, indent=2, default=str, ensure_ascii=False
        )
        print(json_str)

    def display_text(self, data: Any) -> None:
        """
        Display data as plain text.

        Args:
            data: Data to display
        """
        if isinstance(data, str):
            print(data)
        elif isinstance(data, list | tuple):
            for item in data:
                print(f"• {item}")
        elif isinstance(data, dict):
            for key, value in data.items():
                print(f"{key}: {value}")
        else:
            print(str(data))

    def display_raw(self, data: Any) -> None:
        """
        Display data in raw format.

        Args:
            data: Data to display
        """
        print(data)

    def _serialize_object(self, obj: Any) -> dict[str, Any]:
        """
        Serialize an object to a dictionary for JSON display.

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
        Get list of available display formats for this displayer.

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
        formats.extend(["json", "text", "raw"])
        return sorted(set(formats))


class DefaultDisplayer(Displayer):
    """Default displayer with common formats."""

    def get_available_formats(self) -> list[str]:
        """Get available display formats."""
        return ["json", "text", "raw"]

    def display_table(self, data: Any) -> None:
        """
        Display data in table format using rich if available.

        Args:
            data: Data to display
        """
        try:
            from rich.console import Console
            from rich.table import Table

            console = Console()

            if isinstance(data, list) and data:
                # Create table from list of objects/dicts
                table = Table(show_header=True, header_style="bold magenta")

                if isinstance(data[0], dict):
                    # List of dictionaries
                    headers = list(data[0].keys())
                    for header in headers:
                        table.add_column(header)

                    for item in data:
                        row = [str(item.get(header, "")) for header in headers]
                        table.add_row(*row)

                elif hasattr(data[0], "__dict__"):
                    # List of objects
                    headers = list(vars(data[0]).keys())
                    headers = [h for h in headers if not h.startswith("_")]

                    for header in headers:
                        table.add_column(header)

                    for item in data:
                        row = [
                            str(getattr(item, header, "")) for header in headers
                        ]
                        table.add_row(*row)

                else:
                    # List of simple values
                    table.add_column("Value")
                    for item in data:
                        table.add_row(str(item))

                console.print(table)

            elif isinstance(data, dict):
                # Single dictionary
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Key")
                table.add_column("Value")

                for key, value in data.items():
                    table.add_row(str(key), str(value))

                console.print(table)

            else:
                # Fallback to text display
                self.display_text(data)

        except ImportError:
            logger.warning(
                "Rich library not available, falling back to text display"
            )
            self.display_text(data)


class RichDisplayer(DefaultDisplayer):
    """Enhanced displayer with rich formatting support."""

    def get_available_formats(self) -> list[str]:
        """Get available display formats including rich formats."""
        base_formats = super().get_available_formats()
        rich_formats = ["table", "rich"]
        return sorted(set(base_formats + rich_formats))

    def display_rich(self, data: Any) -> None:
        """
        Display data with rich formatting.

        Args:
            data: Data to display
        """
        try:
            from rich.console import Console
            from rich.pretty import pprint

            console = Console()
            console.print("[bold]Data:[/bold]")
            pprint(data)

        except ImportError:
            logger.warning(
                "Rich library not available, falling back to JSON display"
            )
            self.display_json(data)
