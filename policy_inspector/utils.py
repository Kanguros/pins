# ruff: noqa: RET503
import logging
from pathlib import Path
from typing import Any, Callable, Optional

import rich_click as click
from click.types import Choice as clickChoice
from click.types import Path as ClickPath
from pydantic import BaseModel
from rich.logging import RichHandler

EXAMPLES_DIR = Path(__file__).parent / "example"


def get_example_file_path(file_path: Path) -> Path:
    return EXAMPLES_DIR / file_path


# It's just make use of pydantic because it's available ;)
class Example(BaseModel):
    name: str
    args: list
    cmd: Callable

    def model_post_init(self, data):
        self.args = [get_example_file_path(arg) for arg in self.args]


def verbose_option(logger) -> Callable:
    """Wrapper around Click ``option``. Sets logger and its handlers to the ``DEBUG`` level."""

    def callback(ctx: click.Context, param, value) -> None:
        if not value:
            return
        package_logger = logging.getLogger("policy_inspector")
        count = len(value)
        if count > 0:
            logger.setLevel(logging.DEBUG)
        if count > 1:
            package_logger.setLevel(logging.INFO)
        if count > 2:
            package_logger.setLevel(logging.DEBUG)
        if count > 3:
            handler: RichHandler = logger.handlers[0]
            handler._log_render.show_path = True
            handler._log_render.show_time = True
            handler._log_render.show_level = True

    kwargs = {
        "is_flag": True,
        "multiple": True,
        "callback": callback,
        "expose_value": False,
        "is_eager": True,
        "help": "More verbose and detailed output with each `-v` up to `-vvvv`",
    }
    return click.option("-v", "--verbose", **kwargs)


def exclude_check_option(arg_name: str = "exclude_checks") -> Callable:
    return click.option(
        "-ec",
        "--exclude-check",
        arg_name,
        multiple=True,
        type=click.STRING,
        nargs=1,
        help="Exclude 'check' from Scenario if it contains provided keyword",
    )


def config_logger(
    logger: logging.Logger,
    level: str = "INFO",
    log_format: str = "%(message)s",
    date_format: str = "[%X]",
) -> None:
    """
    Configure ``logger`` with ``RichHandler``

    Args:
        logger: Instance of a ``logging.Logger``
    """
    logger.setLevel(level)
    package_logger = logging.getLogger("policy_inspector")
    package_logger.setLevel(logging.WARNING)
    package_logger.propagate = True
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
    logger.handlers = [rich_handler]


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
