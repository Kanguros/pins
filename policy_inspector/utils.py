import json
import logging
from pathlib import Path
from typing import Any, Optional

import rich_click as click
from click.types import Choice as clickChoice
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, ConfigDict
from rich.logging import RichHandler


def load_json(file_path: Path) -> Any:
    """
    Load JSON data from a file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data
    """
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def load_jinja_template(template_dir: Path, template_name: str):
    """
    Load a Jinja2 template from the current directory.
    """
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["enumerate"] = enumerate
    env.globals["getattr"] = getattr
    return env.get_template(template_name)


def config_logger(
    logger_name: str = "policy_inspector",
    default_level: str = "INFO",
    log_format: str = "%(message)s",
    date_format: str = "[%X]",
) -> None:
    """
    Configure ``logger`` with ``RichHandler``

    Args:
        logger: Instance of a ``logging.Logger``
        level: Default level of a ``logger``.
        log_format: Logs format.
        date_format: Date format in logs.
    """
    rich_handler = RichHandler(
        rich_tracebacks=True,
        show_path=False,
        show_time=False,
        show_level=False,
        omit_repeated_times=False,
    )
    rich_handler.enable_link_path = True
    formatter = logging.Formatter(log_format, date_format, "%")
    rich_handler.setFormatter(formatter)

    main_logger = logging.getLogger(logger_name)
    main_logger.handlers = [rich_handler]
    main_logger.setLevel(logging.INFO)


class Example(BaseModel):
    """Represents an example that can be run."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    scenario: type | None  # Allow None for dynamic loading
    data_dir: str
    device_group: str
    show: tuple[str, ...] = ("text",)
    export: tuple[str, ...] = ()
    args: dict[str, Any] = {}

    def get_data_dir(self) -> Path:
        """Get the absolute path to the data directory."""
        # Get the directory where cli.py is located (policy_inspector package)
        cli_dir = Path(__file__).parent
        # Construct the path to the example data directory
        return cli_dir / "example" / self.data_dir


class ExampleChoice(clickChoice):
    def __init__(self, examples: list[Example]) -> None:
        self.examples = {example.name: example for example in examples}
        super().__init__(list(self.examples.keys()), False)  # noqa: FBT003

    def convert(
        self,
        value: Any,
        param: Optional["click.Parameter"],
        ctx: Optional["click.Context"],
    ) -> Any:
        normed_value = value
        normed_choices = self.examples

        if ctx is not None and ctx.token_normalize_func is not None:
            normed_value = ctx.token_normalize_func(value)
            normed_choices = {
                ctx.token_normalize_func(normed_choice): original
                for normed_choice, original in normed_choices.items()
            }

        normed_value = normed_value.casefold()
        normed_choices = {
            normed_choice.casefold(): original
            for normed_choice, original in normed_choices.items()
        }

        try:
            return normed_choices[normed_value]
        except KeyError:
            matching_choices = list(
                filter(lambda c: c.startswith(normed_value), normed_choices)
            )

        if len(matching_choices) == 1:
            return matching_choices[0]

        if not matching_choices:
            choices_str = ", ".join(map(repr, self.choices))
            message = f"{value!r} is not one of {choices_str}."
        else:
            choices_str = ", ".join(map(repr, matching_choices))
            message = f"{value!r} too many matches: {choices_str}."
        raise click.UsageError(message=message, ctx=ctx)


def get_example_file_path(name: str) -> Path:
    """Get the path to an example file."""
    return Path(__file__).parent / "example" / name
