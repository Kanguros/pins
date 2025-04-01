import logging
from pathlib import Path

import rich_click as click
from click import Path as ClickPath

from pins.loader import FileHandler, ModelClass
from pins.models import (
    AddressGroup,
    AddressObject,
    SecurityRule,
)
from pins.scenario import Scenario
from pins.scenario.complex_shadowing import ShadowingByValue
from pins.scenario.shadowing import Shadowing
from pins.utils import (
    Example,
    ExampleChoice,
    config_logger,
    verbose_option,
)

logger = logging.getLogger()
config_logger(logger)
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.TEXT_MARKUP = "markdown"
# click.rich_click.APPEND_METAVARS_HELP = True
click.rich_click.SHOW_METAVARS_COLUMN = False


@click.group(no_args_is_help=True, add_help_option=True)
@verbose_option(logger)
def main():
    """*PINS*
    as Policy Inspector
    """


@main.command("list")
@verbose_option(logger)
def main_list() -> None:
    """List available Scenarios."""
    logger.info("Available Scenarios:")
    scenarios = Scenario.get_available()
    for name, scenario in scenarios.items():
        logger.info(f"- {name}")
        logger.debug(f"  {scenario.__doc__}")
        for check in scenario.checks:
            logger.debug(f"  - {check.__name__}")


@main.group("run", no_args_is_help=True)
@verbose_option(logger)
def main_run():
    """Execute Scenario."""


@main_run.command("shadowing", no_args_is_help=True)
@verbose_option(logger)
@click.argument(
    "security_rules_path",
    required=True,
    type=ClickPath(dir_okay=False, path_type=Path),
)
def run_shadowing(security_rules_path: Path) -> None:
    security_rules = load_model(SecurityRule, security_rules_path)
    scenario = Shadowing(security_rules)
    process(scenario)


@main_run.command("complex_shadowing", no_args_is_help=True)
@verbose_option(logger)
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
    security_rules = load_model(SecurityRule, security_rules_path)
    address_groups = load_model(AddressGroup, address_groups_path)
    address_objects = load_model(AddressObject, address_objects_path)
    scenario = ShadowingByValue(security_rules, address_groups, address_objects)
    process(scenario)


def process(scenario: Scenario):
    """Helper function for executing and analyzing a Scenario."""
    logger.info(f"▶ Executing '{scenario.name}' scenario...")
    output = scenario.execute()
    logger.info(f"▶ Analyzing '{scenario.name}' results...")
    scenario.analyze(output)
    logger.info("✓ Analysis finished")


def load_model(
    model_cls: type[ModelClass], file_path: Path
) -> list[ModelClass]:
    """Helper function for loading models from file."""
    logger.info(f"▶ Loading {model_cls.name_plural} from {str(file_path)}")
    instances = FileHandler.load_for_model(model_cls, file_path)
    logger.info(
        f"✓ Loaded {len(instances)} {model_cls.name_plural} successfully"
    )
    return instances


examples = [
    Example(
        name="shadowing",
        args=[Path("1/policies.json")],
        cmd=run_shadowing,
    ),
    Example(
        name="shadowing_long",
        args=[Path("2/policies.json")],
        cmd=run_shadowing,
    ),
    Example(
        name="complex_shadowing",
        args=[
            Path("1/policies.json"),
            Path("1/addressgroup.json"),
            Path("1/addressobject.json"),
        ],
        cmd=run_complex_shadowing,
    ),
]


@main_run.command("example", no_args_is_help=True)
@verbose_option(logger)
@click.argument(
    "name",
    type=ExampleChoice(examples),
)
@click.pass_context
def run_example(ctx, example: Example) -> None:
    """Run one of the examples."""
    logger.info(f"▶ Selected '{example.name}' example")
    ctx.invoke(example.cmd.callback, *example.args)


if __name__ == "__main__":
    main()
