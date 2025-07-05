import logging
from pathlib import Path
from textwrap import dedent
from typing import TypeVar

import rich_click as click
from rich_click import rich_config

from policy_inspector.config import Config
from policy_inspector.panorama import PanoramaConnector
from policy_inspector.scenario import Scenario
from policy_inspector.scenarios.shadowing.advanced import AdvancedShadowing
from policy_inspector.scenarios.shadowing.base import Shadowing
from policy_inspector.utils import (
    Example,
    ExampleChoice,
    config_logger,
    verbose_option,
)

config_logger()

click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.TEXT_MARKUP = "markdown"
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_METAVARS_COLUMN = True

logger = logging.getLogger(__name__)

ConcreteScenario = TypeVar("ConcreteScenario", bound="Scenario")


@click.group(no_args_is_help=True, add_help_option=True)
@verbose_option()
def main():
    """*PINS*
    as Policy Inspector
    """


@main.command("list")
@verbose_option()
def main_list() -> None:
    """List available Scenarios."""
    logger.info("")
    logger.info("-----------------------")
    logger.info("")
    for scenario in Scenario.get_available().values():
        logger.info(f"→ '{scenario.name}'")
        scenario_doc = scenario.__doc__
        if scenario_doc:
            doc = dedent(scenario_doc)
            logger.info(f"{doc}")
        checks = getattr(scenario, "checks", None)
        if checks:
            for check in scenario.checks:
                logger.info(f"\t▶ '{check.__name__}'")
                doc = check.__doc__.replace("\n", "")
                logger.info(f"\t  {doc}")
        logger.info("")
        logger.info("-----------------------")
        logger.info("")


@main.group("run", no_args_is_help=True)
@verbose_option()
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


def run_scenario_with_panorama(
    scenario_cls,
    config: Config,
    device_groups,
) -> None:
    """Common scenario execution logic for Panorama-based scenarios."""
    panorama = PanoramaConnector(
        hostname=config.panorama.hostname,
        username=config.panorama.username,
        password=config.panorama.password.get_secret_value(),
        verify_ssl=config.panorama.verify_ssl,
        api_version=config.panorama.api_version,
    )
    scenario = scenario_cls(
        panorama=panorama, device_groups=list(device_groups)
    )
    scenario.execute_and_analyze()
    if config.show:
        scenario.show(config.show)
    if config.export:
        scenario.export(config.export)


@main_run.command("shadowing", no_args_is_help=True)
@verbose_option()
@Config.option()
def run_shadowing(config: Config, device_groups) -> None:
    """Run shadowing analysis using Panorama data."""
    run_scenario_with_panorama(Shadowing, config, device_groups=device_groups)


@main_run.command("shadowingvalue", no_args_is_help=True)
@verbose_option()
@Config.option()
def run_shadowingvalue(config: Config, device_groups: tuple[str]) -> None:
    """Run advanced shadowing analysis using Panorama data."""
    run_scenario_with_panorama(
        AdvancedShadowing, config, device_groups=device_groups
    )


examples = [
    Example(
        name="shadowing-basic",
        cmd=run_shadowingvalue,
        args={"config_file": Path(__file__).parent / "example/1/config.yaml"},
    ),
    Example(
        name="shadowing-multiple-dg",
        cmd=run_shadowingvalue,
        args={"config_file": Path(__file__).parent / "example/2/config.yaml"},
    ),
    Example(
        name="shadowingvalue-basic",
        cmd=run_shadowingvalue,
        args={
            "config_file": Path(__file__).parent.parent
            / "tests/data/test_shadowing_by_value/config.yaml"
        },
    ),
    Example(
        name="shadowingvalue-ssl",
        cmd=run_shadowingvalue,
        args={
            "config_file": Path(__file__).parent.parent
            / "tests/data/test_shadowing_by_value/config.yaml",
            "verify_ssl": True,
        },
    ),
]


@main_run.command("example", no_args_is_help=True)
@click.argument(
    "example",
    type=ExampleChoice(examples),
)
@click.pass_context
def run_example(
    ctx,
    example: Example,
) -> None:
    """Run one of the examples."""
    logger.info(f"▶ Selected example: '{example.name}'")
    logger.info(
        "This is a demonstration run using example config/data. Results may not reflect your environment."
    )
    logger.info(f"Config file path: {example.args['config_file'].absolute()}")
    try:
        ctx.invoke(example.cmd, **example.args)
    except Exception as ex:
        logger.error(
            "Example run failed. This is expected if required files or connectivity are missing."
        )
        logger.error(f"Error: {ex}")


if __name__ == "__main__":
    main()
