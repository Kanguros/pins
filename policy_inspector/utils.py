# ruff: noqa: RET503
import logging
from gettext import ngettext
from pathlib import Path
from typing import Any, Callable, Optional

from click import Context, Parameter, option
from click.types import Choice as clickChoice
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

    def callback(ctx, param, value) -> None:
        if not value:
            return
        count = len(value)
        if count > 0:
            logger.setLevel(logging.DEBUG)
            for handler in logger.handlers:
                handler.setLevel(logging.DEBUG)
        if count > 1:
            handler: RichHandler = logger.handlers[0]
            handler.enable_link_path = True
            handler._log_render.show_path = True
            handler._log_render.show_time = True
            handler._log_render.show_level = True

    kwargs = {
        "is_flag": True,
        "multiple": True,
        "callback": callback,
        "expose_value": False,
        "is_eager": True,
        "help": "Set log messages to DEBUG",
    }
    return option("-v", "--verbose", **kwargs)


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
    rich_handler = RichHandler(
        level=level,
        rich_tracebacks=True,
        # tracebacks_suppress=[click],
        show_path=False,
        show_time=False,
        show_level=False,
        omit_repeated_times=False,
    )
    formatter = logging.Formatter(log_format, date_format, "%")
    rich_handler.setFormatter(formatter)
    logger.handlers = [rich_handler]


class Choice(clickChoice):
    def __init__(self, choices: list[Example]) -> None:
        choices = [e.name for e in choices]
        super().__init__(choices, False)  # noqa: FBT003

    def convert(
        self, value: Any, param: Optional["Parameter"], ctx: Optional["Context"]
    ) -> Any:
        normed_value = value
        normed_choices = {choice: choice for choice in self.choices}

        if ctx is not None and ctx.token_normalize_func is not None:
            normed_value = ctx.token_normalize_func(value)
            normed_choices = {
                ctx.token_normalize_func(normed_choice): original
                for normed_choice, original in normed_choices.items()
            }

        if not self.case_sensitive:
            normed_value = normed_value.casefold()
            normed_choices = {
                normed_choice.casefold(): original
                for normed_choice, original in normed_choices.items()
            }

        if normed_value in normed_choices:
            return normed_choices[normed_value]

        matching_choices = list(
            filter(lambda c: c.startswith(normed_value), normed_choices)
        )

        if matching_choices:
            self.fail(
                f"{normed_value!r} too many matches: {', '.join(matching_choices)}.",
                param,
                ctx,
            )

        choices_str = ", ".join(map(repr, self.choices))
        self.fail(
            ngettext(
                "{value!r} is not {choice}.",
                "{value!r} is not one of {choices}.",
                len(self.choices),
            ).format(value=value, choice=choices_str, choices=choices_str),
            param,
            ctx,
        )
