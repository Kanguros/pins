import logging
from typing import Callable

from pathlib import Path

from click import BadParameter, argument, option
from click.types import Path as ClickPath

from policy_inspector.loader import get_example_file_path, load_from_file
from policy_inspector.models import AddressGroup, AddressObject, SecurityRule


def verbose_option() -> Callable:
    """Wrapper around Click ``option``. Sets logger and its handlers to the ``DEBUG`` level."""

    def callback(ctx, param, value) -> None:
        if not value:
            return
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    kwargs = {
        "is_flag": True,
        "callback": callback,
        "expose_value": False,
        "is_eager": True,
        "help": "Set log messages to DEBUG",
    }
    return option("-v", "--verbose", **kwargs)


def model_argument(model_cls, arg, **kwargs) -> Callable:
    """Wrapper around Click ``argument`` that loads a model instances from a file.

    This argument allows specifying a file path to load data into a model instance.
    If the value starts with 'example', it attempts to load from example files.

    Args:
        model_cls: The model class to instantiate.
        arg: The name of the argument.
        **kwargs: Additional keyword arguments passed to Click's argument decorator.

    Raises:
        BadParameter: If the specified file is not found.

    Example:
        @click.command()
        @model_argument(MyModel, 'model_file')
        def cli(model_file):
            process(model_file)

    """

    def callback(ctx, param, value: str):
        if value.startswith("example"):
            value = get_example_file_path(model_cls, value)
        else:
            value = Path(value)
        try:
            return load_from_file(model_cls, value)
        except FileNotFoundError:
            raise BadParameter(
                f"File '{value}' not found!",
                ctx=ctx,
                param=param,
            ) from None

    kwargs = {
        "type": ClickPath(dir_okay=False),
        "callback": callback,
        "required": True,
    }
    return argument(arg, **kwargs)


def security_rules_argument():
    """Click ``Argument`` for loading ``SecurityRule`` instances from a file.

    Notes:
        Passes ``security_rules`` argument to decorated function.

    Example:
        @click.command()
        @security_rules_argument()
        def cli(security_rules):
            process(security_rules)

    """
    return model_argument(SecurityRule, "security_rules")


def address_groups_argument():
    """Click ``Argument`` for loading ``AddressGroup`` instances from a file.

    Notes:
        Passes ``address_groups`` argument to decorated function.

    Example:
        @click.command()
        @security_rules_argument()
        def cli(security_rules):
            process(security_rules)

    """
    return model_argument(AddressGroup, "address_groups")


def address_objects_argument():
    """Click ``Argument`` for loading ``AddressObject`` instances from a file.

    Notes:
        Passes ``address_objects`` argument to decorated function.

    Example:
        @click.command()
        @security_rules_argument()
        def cli(security_rules):
            process(security_rules)

    """
    return model_argument(AddressObject, "address_objects")
