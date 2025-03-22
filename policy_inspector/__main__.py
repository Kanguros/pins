import logging

import rich_click as click
from rich.logging import RichHandler

from policy_inspector.param import (
    address_groups_argument,
    address_objects_argument,
    security_rules_argument,
    verbose_option,
)
from policy_inspector.scenario.complex_shadowing import ComplexShadowing
from policy_inspector.scenario.shadowing import ShadowingScenario

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
    """Policy Inspector"""


@main.group(no_args_is_help=True)
@verbose_option()
def run():
    """Execute one of the predefined scenarios."""


@run.command("shadowing", no_args_is_help=True)
@verbose_option()
@security_rules_argument()
def run_shadowing(security_rules):
    scenario = ShadowingScenario(security_rules)
    output = scenario.execute()
    scenario.analyze(output)


@run.command("complex_shadowing", no_args_is_help=True)
@verbose_option()
@security_rules_argument()
@address_groups_argument()
@address_objects_argument()
def run_complex_shadowing(security_rules, address_groups, address_objects):
    scenario = ComplexShadowing(security_rules, address_groups, address_objects)
    output = scenario.execute()
    scenario.analyze(output)


if __name__ == "__main__":
    main()
