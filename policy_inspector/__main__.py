import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import rich

if int(os.environ.get("DISABLE_RICH_CLICK", 0)):
    import click
else:
    import rich_click as click

from click import ClickException
from click.types import Path as ClickPath
from rich.logging import RichHandler

from policy_inspector.check import COMPLEX_CHECKS, SIMPLE_CHECKS, run_checks_on_rules
from policy_inspector.evaluate import analyze_checks_results
from policy_inspector.models import AddressGroup, AddressObject, SecurityRule
from policy_inspector.resolve import resolve_rules_addresses
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


@main.command("run")
@click.argument("checks_list", default="simple", nargs=1)
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
    type=ClickPath(exists=False, dir_okay=False, path_type=Path),
    help="Path to JSON file with Address Groups",
)
@click.option(
    "--address-objects",
    "-ao",
    "address_objects_file",
    type=ClickPath(exists=False, dir_okay=False, path_type=Path),
    help="Path to JSON file with Address Objects",
)
def main_run(
        checks_list, security_rules_file, address_objects_file, address_groups_file
):
    """
    Execute
    """
    checks = SIMPLE_CHECKS
    if not security_rules_file:
        raise ClickException("No path was provided for --security-rules/-sr")

    security_rules = SecurityRule.load_from_json(security_rules_file)
    if checks_list == "complex":
        if not address_groups_file or not address_objects_file:
            logger.error(
                "Cannot run complex checks without Address Groups and Address Objects files."
            )
        else:
            address_objects = AddressObject.load_from_json(address_objects_file)
            address_groups = AddressGroup.load_from_json(address_groups_file)

            security_rules = resolve_rules_addresses(
                security_rules, address_objects, address_groups
            )
            checks = COMPLEX_CHECKS

    logger.info("Starting shadowed Rules detection")
    logger.info(f"Number of Rules to check: {len(security_rules)}")
    logger.info(f"Number of Checks: {len(checks)}")
    for check in checks:
        logger.debug(f"- {check.__name__}")
    logger.info("Finished shadowed Rules detection. Analyzing results")

    results = run_checks_on_rules(security_rules, checks)
    analyze_checks_results(results)

    rich.print(results)


@main.command("run-example")
@verbose_option()
def main_run_example():
    logger.info("Running an example")

    from policy_inspector.tests.conftest import (
        get_example_address_groups_path,
        get_example_address_objects_path,
        get_example_security_rules_path,
    )

    security_rules = SecurityRule.load_from_json(
        get_example_security_rules_path()
    )
    address_objects = AddressObject.load_from_json(
        get_example_address_objects_path()
    )
    address_groups = AddressGroup.load_from_json(
        get_example_address_groups_path()
    )

    security_rules = resolve_rules_addresses(
        security_rules, address_objects, address_groups
    )

    logger.info("Starting shadowed Rules detection")
    logger.info(f"Number of Rules to check: {len(security_rules)}")
    logger.info(f"Number of Checks: {len(SIMPLE_CHECKS)}")
    for check in SIMPLE_CHECKS:
        logger.debug(f"- {check.__name__}")
    logger.info("Finished shadowed Rules detection. Analyzing results")

    results = run_checks_on_rules(security_rules, SIMPLE_CHECKS)
    analyze_checks_results(results)

    rich.print(results)


if __name__ == "__main__":
    main()
