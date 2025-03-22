import logging
from typing import Any, Callable

from click import option, argument, BadParameter
from click.types import Path as ClickPath

from policy_inspector.load import load_from_file, load_example


def verbose_option(**kwargs: Any) -> Callable:
    def callback(ctx, param, value: bool) -> None:  # noqa: FBT001
        if not value:
            return
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    kwargs.setdefault("is_flag", True)
    kwargs.setdefault("callback", callback)
    kwargs.setdefault("expose_value", False)
    kwargs.setdefault("is_eager", True)
    kwargs.setdefault("help", "Set log messages to DEBUG")
    return option("-v", "--verbose", **kwargs)


def model_argument(model_cls, name, **kwargs) -> Callable:
    def callback(ctx, param, value: str):

        if value.startswith("example"):
            try:
                return load_example(model_cls, value)
            except FileNotFoundError:
                raise BadParameter(f"Example '{value}' for {model_cls.__name__} not found!", ctx=ctx, param=param)
        try:
            return load_from_file(model_cls, value)
        except FileNotFoundError:
            raise BadParameter(f"File {value} not found!", ctx=ctx, param=param)

    kwargs.setdefault("callback", callback)
    kwargs.setdefault("type", ClickPath(dir_okay=False))
    kwargs.setdefault("required", True)
    return argument(name, **kwargs)
