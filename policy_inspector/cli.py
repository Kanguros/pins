import logging
from pathlib import Path

import rich_click as click
from click import Path as ClickPath
from rich.logging import RichHandler

from policy_inspector.loader import load_from_file
from policy_inspector.models import (
    AddressGroup,
    AddressObject,
    SecurityRule,
)
from policy_inspector.scenario import Scenario
from policy_inspector.scenario.complex_shadowing import ShadowingByValue
from policy_inspector.scenario.shadowing import Shadowing
from policy_inspector.utils import Example, verbose_option

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
@click.argument(
    "security_rules_path",
    required=True,
    type=ClickPath(dir_okay=False, path_type=Path),
)
def run_shadowing(security_rules_path: Path) -> None:
    security_rules = load_from_file(SecurityRule, security_rules_path)
    scenario = Shadowing(security_rules)
    output = scenario.execute()
    scenario.analyze(output)


@main_run.command("complex_shadowing", no_args_is_help=True)
@verbose_option()
@click.argument(
    "security_rules_path",
    required=True,
    type=ClickPath(dir_okay=False, path_type=Path),
)
@click.argument(
    "address_groups_path",
    required=True,
    type=ClickPath(dir_okay=False, path_type=Path),
)
@click.argument(
    "address_objects_path",
    required=True,
    type=ClickPath(dir_okay=False, path_type=Path),
)
def run_complex_shadowing(
    security_rules_path: Path,
    address_groups_path: Path,
    address_objects_path: Path,
) -> None:
    security_rules = load_from_file(SecurityRule, security_rules_path)
    address_groups = load_from_file(AddressGroup, address_groups_path)
    address_objects = load_from_file(AddressObject, address_objects_path)
    scenario = ShadowingByValue(security_rules, address_groups, address_objects)
    output = scenario.execute()
    scenario.analyze(output)


examples = [
    Example(
        name="shadowing_by_name",
        args=[Path("1/securityrule.json")],
        cmd=run_shadowing,
    ),
    Example(
        name="shadowing_by_value",
        args=[
            Path("1/securityrule.json"),
            Path("1/addressgroup.json"),
            Path("1/addressobject.json"),
        ],
        cmd=run_complex_shadowing,
    ),
]

examples_by_name = {e.name: e for e in examples}

examples_dir: Path = Path(__file__).parent / "example"


@main_run.command("example", no_args_is_help=True)
@verbose_option()
@click.argument(
    "name",
    metavar="EXAMPLE_NAME",
    type=click.Choice(list(examples_by_name.keys())),
)
@click.pass_context
def run_example(ctx, name: str) -> None:
    """Run one of the examples."""
    example = examples_by_name[name]
    args = [examples_dir / arg for arg in example.args]
    ctx.invoke(example.cmd.callback, *args)


if __name__ == "__main__":
    main()
