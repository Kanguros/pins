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
    FilePath,
    config_logger,
    exclude_check_option,
    export_formats,
    show_option,
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



# --- Begin: DRY helpers for scenario commands ---
def panorama_options(func):
    """Decorator to add common Panorama connection options to a Click command."""
    options = [
        click.option(
        "--config", "config_file", type=FilePath(), help="Path to YAML config file."
    ),
    click.option(
        "-h",
        "--host",
        "hostname",
        type=click.STRING,
        help="Panorama hostname",
        envvar="PINS_HOST",
    ), click.option(
        "-u",
        "--username",
        type=click.STRING,
        help="Panorama username",
        envvar="PINS_USERNAME",
    ), click.option(
        "-p",
        "--password",
        type=click.STRING,
        help="Panorama password",
        envvar="PINS_PASSWORD",
    ), click.option(
        "-d",
        "--device-group",
        "device_groups",
        type=click.STRING,
        help="Name of the Device Group",
        multiple=True,
        envvar="PINS_DEVICE_GROUPS",
    ), click.option(
        "--ssl",
        "verify_ssl",
        is_flag=True,
        help="Verify SSL certificates",
        envvar="PINS_VERIFY_SSL",
    )]
    for opt in reversed(options):
        func = opt(func)
    return func

def run_scenario_with_panorama(
    scenario_cls,
    config: Config,
    device_groups,
) -> None:
    """Common scenario execution logic for Panorama-based scenarios."""
    panorama = PanoramaConnector(hostname=config.panorama.hostname,
                                 username=config.panorama.username,
                                 password=config.panorama.password.get_secret_value(),
                                    verify_ssl=config.panorama.verify_ssl,
                                    api_version=config.panorama.api_version)
    scenario = scenario_cls(panorama=panorama, device_groups=list(device_groups))
    scenario.execute_and_analyze()
    if config.show:
        scenario.show(config.show)
    if config.export:
        scenario.export(config.export)


@main_run.command("shadowing", no_args_is_help=True)
@verbose_option()
def run_shadowing(
    config: Config,
    device_groups
) -> None:
    """Run shadowing analysis using Panorama data."""
    run_scenario_with_panorama(
        Shadowing,
        config,
        device_groups=device_groups
    )


@main_run.command("shadowingvalue", no_args_is_help=True)
@verbose_option()
@panorama_options
@exclude_check_option()
@show_option()
@export_formats()
def run_shadowingvalue(
    config_file,
    hostname,
    username,
    password,
    device_groups,
    verify_ssl,
    exclude_checks: tuple[str],
    show_formats: tuple[str],
    export_formats: bool,
) -> None:
    """Run advanced shadowing analysis using Panorama data."""
    run_scenario_with_panorama(
        AdvancedShadowing,
        config_file,
        hostname,
        username,
        password,
        device_groups,
        verify_ssl,
        exclude_checks,
        show_formats,
        export_formats,
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
@verbose_option()
@exclude_check_option()
@show_option()
@export_formats()
@click.pass_context
def run_example(
    ctx,
    example: Example,
    exclude_checks: tuple[str],
    show_formats: tuple[str],
    export_formats: bool,
) -> None:
    """Run one of the examples."""
    logger.info(f"▶ Selected example: '{example.name}'")
    logger.info("This is a demonstration run using example config/data. Results may not reflect your environment.")
    logger.info(f"Config file path: {example.args['config_file'].absolute()}")
    try:
        ctx.invoke(example.cmd, **example.args)
    except Exception as ex:
        logger.error("Example run failed. This is expected if required files or connectivity are missing.")
        logger.error(f"Error: {ex}")


if __name__ == "__main__":
    main()
