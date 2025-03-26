import logging
from typing import Callable

from click import option
from pydantic import BaseModel
from rich.logging import RichHandler


# It's just make use of pydantic because it's available ;)
class Example(BaseModel):
    name: str
    args: list
    cmd: Callable


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
