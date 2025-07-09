import logging
from pathlib import Path
from textwrap import dedent

import rich_click as click
from rich_click import rich_config

from policy_inspector.config import AppConfig, ExampleConfig
from policy_inspector.mock_panorama import MockPanoramaConnector
from policy_inspector.panorama import PanoramaConnector
from policy_inspector.scenario import Scenario
from policy_inspector.scenarios.shadowing.advanced import AdvancedShadowing
from policy_inspector.scenarios.shadowing.simple import Shadowing
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
    scenario_cls: type[Scenario],
    config: AppConfig,
    panorama_cls: type[PanoramaConnector] = PanoramaConnector,
    **kwargs,
) -> None:
    """Common scenario execution logic for Panorama-based scenarios."""
    panorama = panorama_cls(
        hostname=config.panorama.hostname,
        username=config.panorama.username,
        password=config.panorama.password.get_secret_value(),
        verify_ssl=config.panorama.verify_ssl,
        api_version=config.panorama.api_version,
    )
    scenario = scenario_cls(panorama=panorama, **kwargs)
    scenario.execute_and_analyze()
    if config.show:
        scenario.show(config.show)
    if config.export:
        scenario.export(config.export)


def run_scenario_with_mock_data(
    scenario_cls: type[Scenario],
    config_file: Path,
    device_groups: tuple[str] = (),
    **kwargs,
) -> None:
    """Run scenario using mock data from JSON files for examples."""
    # Load example configuration
    example_config = ExampleConfig.from_yaml_file(str(config_file))

    # Get the data directory from the config file location
    data_dir = config_file.parent

    # Use the first file configuration (examples typically have one)
    file_config = example_config.files[0]

    # Create mock panorama connector
    panorama = MockPanoramaConnector(
        data_dir=data_dir,
        device_group=file_config.device_group,
    )

    # Convert tuple to list for device_groups
    device_groups_list = (
        list(device_groups) if device_groups else [file_config.device_group]
    )

    # Create and run scenario
    scenario = scenario_cls(
        panorama=panorama, device_groups=device_groups_list, **kwargs
    )
    scenario.execute_and_analyze()

    # Show and export results if configured
    if example_config.show:
        scenario.show(example_config.show)
    if example_config.export:
        scenario.export(example_config.export)


@main_run.command("shadowing", no_args_is_help=True)
@verbose_option()
@AppConfig.option()
@click.option(
    "--device-groups",
    multiple=True,
    help="Device groups to analyze (can be specified multiple times)",
)
def run_shadowing(config: AppConfig, device_groups: tuple[str]) -> None:
    """Run shadowing analysis using Panorama data."""
    run_scenario_with_panorama(Shadowing, config, device_groups=device_groups)


@main_run.command("shadowingvalue", no_args_is_help=True)
@verbose_option()
@AppConfig.option()
@click.option(
    "--device-groups",
    multiple=True,
    help="Device groups to analyze (can be specified multiple times)",
)
def run_shadowingvalue(config: AppConfig, device_groups: tuple[str]) -> None:
    """Run advanced shadowing analysis using Panorama data."""
    run_scenario_with_panorama(
        AdvancedShadowing, config, device_groups=device_groups
    )


def run_shadowing_example(config_file: Path, **kwargs) -> None:
    """Run shadowing example with mock data."""
    run_scenario_with_mock_data(Shadowing, config_file, **kwargs)


def run_shadowingvalue_example(config_file: Path, **kwargs) -> None:
    """Run advanced shadowing example with mock data."""
    run_scenario_with_mock_data(AdvancedShadowing, config_file, **kwargs)


examples = [
    Example(
        name="shadowing-basic",
        cmd=run_shadowing_example,
        args={"config_file": Path(__file__).parent / "example/1/config.yaml"},
    ),
    Example(
        name="shadowing-multiple-dg",
        cmd=run_shadowing_example,
        args={"config_file": Path(__file__).parent / "example/2/config.yaml"},
    ),
    Example(
        name="shadowingvalue-basic",
        cmd=run_shadowingvalue_example,
        args={
            "config_file": Path(__file__).parent.parent
            / "tests/data/test_shadowing_by_value/config.yaml"
        },
    ),
    Example(
        name="shadowingvalue-ssl",
        cmd=run_shadowingvalue_example,
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
    logger.info("Executing scenario with provided example configuration...")

    try:
        # Extract device groups from the file config if available
        config_file = example.args["config_file"]
        try:
            example_config = ExampleConfig.from_yaml_file(str(config_file))
            device_groups = tuple(
                file_config.device_group for file_config in example_config.files
            )
            # Add device_groups to the args
            example_args = {**example.args, "device_groups": device_groups}
        except Exception:
            # Fallback for non-example configs
            example_args = example.args

        # Run the example command
        example.cmd(**example_args)

    except Exception as ex:
        logger.error(
            "Example run failed. This is expected if required files or connectivity are missing."
        )
        logger.error(f"Error: {ex}")
    finally:
        logger.info("Example execution completed")


if __name__ == "__main__":
    main()
