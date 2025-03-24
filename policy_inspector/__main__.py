import logging
from pathlib import Path
from typing import TYPE_CHECKING

import rich_click as click
from rich.logging import RichHandler

from policy_inspector.param import (
    address_groups_argument,
    address_objects_argument,
    security_rules_argument,
    verbose_option,
)
from policy_inspector.scenario.base import Scenario
from policy_inspector.scenario.complex_shadowing import ShadowingByValue
from policy_inspector.scenario.shadowing import Shadowing

if TYPE_CHECKING:
    from policy_inspector.models import (
        AddressGroup,
        AddressObject,
        SecurityRule,
    )

LOG_FORMAT = "%(message)s"
LOG_DEFAULT_LEVEL = "INFO"
logging.basicConfig(
    level=LOG_DEFAULT_LEVEL,
    format=LOG_FORMAT,
    datefmt="[%X]",
    handlers=[
        RichHandler(
            level=LOG_DEFAULT_LEVEL,
            rich_tracebacks=True,
            tracebacks_suppress=[click],
            show_path=False,
            show_time=False,
            show_level=False,
            omit_repeated_times=False,
        ),
    ],
)

logger = logging.getLogger(__name__)


@click.group(no_args_is_help=True, add_help_option=True)
@verbose_option()
def main():
    """Policy Inspector"""


@main.command("list")
@verbose_option()
def main_list() -> None:
    """List available Scenarios."""
    logger.info("Available Scenarios:")
    scenarios = Scenario.list()
    for scenario in scenarios:
        logger.info(f"- {scenario.__name__}")


@main.group("run", no_args_is_help=True)
@verbose_option()
def main_run():
    """Execute Scenario."""


@main_run.command("shadowing", no_args_is_help=True)
@verbose_option()
@security_rules_argument()
def run_shadowing(security_rules: list["SecurityRule"]) -> None:
    scenario = Shadowing(security_rules)
    output = scenario.execute()
    scenario.analyze(output)


@main_run.command("complex_shadowing", no_args_is_help=True)
@verbose_option()
@security_rules_argument()
@address_groups_argument()
@address_objects_argument()
def run_complex_shadowing(
    security_rules: list["SecurityRule"],
    address_groups: list["AddressGroup"],
    address_objects: list["AddressObject"],
) -> None:
    scenario = ShadowingByValue(security_rules, address_groups, address_objects)
    output = scenario.execute()
    scenario.analyze(output)


examples = {
    "shadowing_by_name": {
        "kwargs": {"security_rules": Path("1/securityrule.json")},
        "cmd": run_shadowing,
    },
    "shadowing_by_value": {
        "kwargs": {
            "security_rules": Path("1/securityrule.json"),
            "address_groups": Path("1/addressgroup.json"),
            "address_objects": Path("1/addressobject.json"),
        },
        "cmd": run_complex_shadowing,
    },
}

examples_dir: Path = Path(__file__).parent / "example"


@main_run.command("example", no_args_is_help=True)
@verbose_option()
@click.argument(
    "name", metavar="EXAMPLE_NAME", type=click.Choice(list(examples.keys()))
)
@click.pass_context
def run_example(ctx, name: str) -> None:
    """Run one of the examples."""
    example_params = examples[name]

    kwargs = example_params["kwargs"]
    for arg, value in kwargs.items():
        example_params[arg] = examples_dir / value
    command = example_params["cmd"]
    ctx.invoke(command, **kwargs)


if __name__ == "__main__":
    main()
