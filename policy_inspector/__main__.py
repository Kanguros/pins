import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from policy_inspector.load import load_from_file
from policy_inspector.scenario.complex_shadowing import ComplexShadowing
from policy_inspector.scenario.shadowing import ShadowingScenario

if int(os.environ.get("DISABLE_RICH_CLICK", 0)):
    import click
else:
    import rich_click as click

from click.types import Path as ClickPath
from rich.logging import RichHandler

from policy_inspector.models import AddressGroup, AddressObject, SecurityRule
from policy_inspector.utils import verbose_option

if TYPE_CHECKING:
    pass

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
            omit_repeated_times=False,
        )
    ],
)

logger = logging.getLogger(__name__)


@click.group(no_args_is_help=True, add_help_option=True)
@verbose_option()
def main():
    """Rules Check"""


@main.group(no_args_is_help=True)
@verbose_option()
def run():
    """Execute one of the predefined scenarios."""


@run.command("shadowing")
@verbose_option()
@click.option(
    "--security-rules",
    "-sr",
    "security_rules_file",
    type=ClickPath(exists=True, dir_okay=False, path_type=Path),
    help="Path to file with Security Rules.",
)
def run_shadowing(security_rules_file):
    security_rules = load_from_file(SecurityRule, security_rules_file)
    scenario = ShadowingScenario(security_rules)
    output = scenario.execute()
    scenario.analyze(output)


@run.command("complex_shadowing")
@verbose_option()
@click.option(
    "--security-rules",
    "-sr",
    "security_rules_file",
    type=ClickPath(exists=True, dir_okay=False, path_type=Path),
    help="Path to JSON file with Security Rules",
)
@click.option(
    "--address-groups",
    "-ag",
    "address_groups_file",
    type=ClickPath(exists=True, dir_okay=False, path_type=Path),
    help="Path to JSON file with Address Groups",
)
@click.option(
    "--address-objects",
    "-ao",
    "address_objects_file",
    type=ClickPath(exists=True, dir_okay=False, path_type=Path),
    help="Path to JSON file with Address Objects",
)
def run_complex_shadowing(
    security_rules_file, address_objects_file, address_groups_file
):
    security_rules = load_from_file(SecurityRule, security_rules_file)
    address_groups = load_from_file(AddressGroup, address_groups_file)
    address_objects = load_from_file(AddressObject, address_objects_file)
    scenario = ComplexShadowing(security_rules, address_groups, address_objects)
    output = scenario.execute()
    scenario.analyze(output)


if __name__ == "__main__":
    main()
