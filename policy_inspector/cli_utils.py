import logging
from typing import Any, Callable

from click import BadParameter, argument, option
from click.types import Path as ClickPath

from policy_inspector.load import load_from_file, get_example_file_path
from policy_inspector.models import AddressGroup, AddressObject, SecurityRule


def verbose_option(**kwargs: Any) -> Callable:
    def callback(ctx, param, value) -> None:  # noqa: FBT001
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


def model_argument(model_cls, arg, **kwargs) -> Callable:
    def callback(ctx, param, value: str):
        if value.startswith("example"):
            value = get_example_file_path(model_cls, value)
        try:
            return load_from_file(model_cls, value)
        except FileNotFoundError:
            raise BadParameter(f"File {value} not found!", ctx=ctx, param=param)

    kwargs.setdefault("callback", callback)
    kwargs.setdefault("type", ClickPath(dir_okay=False))
    kwargs.setdefault("required", True)
    return argument(arg, **kwargs)


def security_rules_argument():
    return model_argument(SecurityRule, "security_rules")


def address_groups_argument():
    return model_argument(AddressGroup, "address_groups")


def address_objects_argument():
    return model_argument(AddressObject, "address_objects")
