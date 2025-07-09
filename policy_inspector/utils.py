import json
import logging
from pathlib import Path
from typing import Any, Callable, Optional

import rich_click as click
from click.types import Choice as clickChoice
from click.types import Path as ClickPath
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, ConfigDict
from rich.logging import RichHandler


def load_json(path: Path) -> list[dict[str, Any]]:
    """Load and parse a JSON file, returning its contents as a list of dictionaries."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


_EXPORT_REGISTRY: dict[tuple[type, str], Callable] = {}
_SHOW_REGISTRY: dict[tuple[type, str], Callable] = {}


def register_export(scenario_cls: type, fmt: str):
    """Decorator to register an export function for a scenario and format."""

    def decorator(func: Callable):
        _EXPORT_REGISTRY[(scenario_cls, fmt)] = func
        return func

    return decorator


def get_export_func(scenario, fmt: str):
    """Get export function for scenario instance and format."""
    return _EXPORT_REGISTRY.get((type(scenario), fmt))


def register_show(scenario_cls: type, fmt: str):
    """Decorator to register a show function for a scenario and format."""

    def decorator(func: Callable):
        _SHOW_REGISTRY[(scenario_cls, fmt)] = func
        return func

    return decorator


def get_show_func(scenario, fmt: str):
    """Get show function for scenario instance and format."""
    return _SHOW_REGISTRY.get((type(scenario), fmt))


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
    return env.get_template(template_name)


def _verbose_callback(ctx: click.Context, param, value) -> None:
    """Callback function for verbose option."""
    if not value:
        return
    _logger = logging.getLogger(__name__).parent
    count = len(value)
    if count > 0:
        _logger.setLevel(logging.DEBUG)
    if count > 1:
        handler = _logger.handlers[0]
        handler._log_render.show_level = True
    if count > 2:
        handler = _logger.handlers[0]
        handler._log_render.show_path = True
        handler._log_render.show_time = True


class VerboseGroup(click.RichGroup):
    """Click Group that automatically adds verbose option to all commands."""

    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        self.params.append(self._verbose_option())

    def add_command(self, cmd, name=None):
        """Override to add verbose option to all commands."""
        cmd.params.append(self._verbose_option())
        super().add_command(cmd, name)

    @staticmethod
    def _verbose_option() -> click.Option:
        return click.Option(
            ["-v", "--verbose"],
            is_flag=True,
            multiple=True,
            callback=_verbose_callback,
            expose_value=False,
            is_eager=True,
            help="More verbose and detailed output with each `-v` up to `-vvvv`",
        )


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
    cmd: Callable
    args: dict[str, Any]


class FilePath(ClickPath):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, exists=True, dir_okay=False, path_type=Path, **kwargs
        )


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
