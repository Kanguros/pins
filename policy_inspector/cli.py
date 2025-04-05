import logging
from pathlib import Path

import rich_click as click
from rich_click import Path as ClickPath
from rich_click import UsageError, rich_config

from policy_inspector.loader import Loader, ModelClass
from policy_inspector.model.address_group import AddressGroup
from policy_inspector.model.address_object import AddressObject
from policy_inspector.model.security_rule import SecurityRule
from policy_inspector.scenario import Scenario
from policy_inspector.scenario.shadowing import Shadowing
from policy_inspector.scenario.shadowing_by_value import ShadowingByValue
from policy_inspector.utils import (
    Example,
    ExampleChoice,
    config_logger,
    verbose_option,
)

logger = logging.getLogger()
config_logger(logger)
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.TEXT_MARKUP = "markdown"
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_METAVARS_COLUMN = True


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
@rich_config(
    help_config={
        "style_argument": "bold yellow",
        "commands_panel_title": "Scenarios",
    }
)
def main_run():
    """Execute a Scenario.


    To see how it works, run one of the examples


    ```
    pins run example

    ```

    """


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


@main_run.command("shadowingvalue", no_args_is_help=True)
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
def run_shadowingvalue(
    security_rules_path: Path,
    address_groups_path: Path,
    address_objects_path: Path,
) -> None:
    security_rules = load_model(SecurityRule, security_rules_path)
    address_groups = load_model(AddressGroup, address_groups_path)
    address_objects = load_model(AddressObject, address_objects_path)
    scenario = ShadowingByValue(security_rules, address_objects, address_groups)
    process(scenario)


def process(scenario: Scenario):
    """Helper function for executing and analyzing a Scenario."""
    logger.info(f"→ Executing '{scenario.name}' scenario")
    try:
        output = scenario.execute()
        logger.info("")
        logger.info("▶ Results")
        logger.info("―――――――――")
        scenario.analyze(output)
    except Exception as ex:  # noqa: BLE001
        raise UsageError(str(ex))  # noqa: B904


def load_model(
    model_cls: type[ModelClass], file_path: Path
) -> list[ModelClass]:
    """Helper function for loading models from file."""
    logger.info(f"↺ Loading {model_cls.plural}")
    instances = Loader.load_model(model_cls, file_path)
    logger.debug(f"✓ Loaded {len(instances)} {model_cls.plural} successfully")
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
        name="shadowing_with_addresses",
        args=[
            Path("1/policies.json"),
            Path("1/address_groups.json"),
            Path("1/address_objects.json"),
        ],
        cmd=run_shadowingvalue,
    ),
    Example(
        name="shadowing_with_addresses2",
        args=[
            Path("2/policies.json"),
            Path("2/address_groups.json"),
            Path("2/address_objects.json"),
        ],
        cmd=run_shadowingvalue,
    ),
]


@main_run.command("example", no_args_is_help=True)
@verbose_option(logger)
@click.argument(
    "example",
    type=ExampleChoice(examples),
)
@click.pass_context
def run_example(ctx, example: Example) -> None:
    """Run one of the examples."""
    logger.info(f"▶ Selected '{example.name}' example")
    ctx.invoke(example.cmd.callback, *example.args)


if __name__ == "__main__":
    main()
