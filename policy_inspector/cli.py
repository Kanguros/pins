import logging
from pathlib import Path
from textwrap import dedent

import rich_click as click

from policy_inspector.config import (
    export_show_options,
    panorama_options,
    yaml_config_option,
)
from policy_inspector.mock_panorama import MockPanoramaConnector
from policy_inspector.panorama import PanoramaConnector
from policy_inspector.scenario import Scenario
from policy_inspector.scenarios.shadowing.advanced import AdvancedShadowing
from policy_inspector.scenarios.shadowing.simple import Shadowing
from policy_inspector.utils import (
    Example,
    ExampleChoice,
    VerboseGroup,
    config_logger,
)

config_logger()

click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.TEXT_MARKUP = "markdown"
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_METAVARS_COLUMN = True

logger = logging.getLogger(__name__)


@click.group(no_args_is_help=True, add_help_option=True, cls=VerboseGroup)
def main():
    """*PINS*
    as Policy Inspector
    """


@main.command("list")
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


@main.group("run", no_args_is_help=True, cls=VerboseGroup)
def main_run():
    """Execute a Scenario.


    To see how it works, run one of the examples


    ```
    pins run example

    ```

    """


def run_scenario_with_panorama(
    scenario_cls: type[Scenario],
    panorama_hostname: str,
    panorama_username: str,
    panorama_password: str,
    panorama_api_version: str = "v11.1",
    panorama_verify_ssl: bool = False,
    export: tuple[str, ...] = (),
    show: tuple[str, ...] = ("text",),
    panorama_cls: type[PanoramaConnector] = PanoramaConnector,
    **kwargs,
) -> None:
    """Common scenario execution logic for Panorama-based scenarios."""
    panorama = panorama_cls(
        hostname=panorama_hostname,
        username=panorama_username,
        password=panorama_password,
        verify_ssl=panorama_verify_ssl,
        api_version=panorama_api_version,
    )
    scenario = scenario_cls(panorama=panorama, **kwargs)
    scenario.execute_and_analyze()
    if show:
        scenario.show(show)
    if export:
        scenario.export(export)


def run_scenario_with_mock_data(
    scenario_cls: type[Scenario],
    data_dir: Path,
    device_group: str,
    device_groups: tuple[str] = (),
    show: tuple[str, ...] = (),
    export: tuple[str, ...] = (),
    **kwargs,
) -> None:
    """Run scenario using mock data from JSON files."""
    # Create mock panorama connector
    panorama = MockPanoramaConnector(
        data_dir=data_dir,
        device_group=device_group,
    )

    # Use provided device_groups or default to the main device_group
    device_groups_list = (
        list(device_groups) if device_groups else [device_group]
    )

    # Create and run scenario
    scenario = scenario_cls(
        panorama=panorama, device_groups=device_groups_list, **kwargs
    )
    scenario.execute_and_analyze()
    if show:
        scenario.show(show)
    if export:
        scenario.export(export)


@main_run.command("shadowing", no_args_is_help=True)
@yaml_config_option()
@panorama_options
@export_show_options
@click.option(
    "--device-groups",
    multiple=True,
    help="Device groups to analyze (can be specified multiple times)",
)
def run_shadowing(
    panorama_hostname: str,
    panorama_username: str,
    panorama_password: str,
    panorama_api_version: str,
    panorama_verify_ssl: bool,
    export: tuple[str, ...],
    show: tuple[str, ...],
    device_groups: tuple[str],
) -> None:
    """Run shadowing analysis using Panorama data."""
    run_scenario_with_panorama(
        Shadowing,
        panorama_hostname=panorama_hostname,
        panorama_username=panorama_username,
        panorama_password=panorama_password,
        panorama_api_version=panorama_api_version,
        panorama_verify_ssl=panorama_verify_ssl,
        export=export,
        show=show,
        device_groups=device_groups,
    )


@main_run.command("shadowingvalue", no_args_is_help=True)
@yaml_config_option()
@panorama_options
@export_show_options
@click.option(
    "--device-groups",
    multiple=True,
    help="Device groups to analyze (can be specified multiple times)",
)
def run_shadowingvalue(
    panorama_hostname: str,
    panorama_username: str,
    panorama_password: str,
    panorama_api_version: str,
    panorama_verify_ssl: bool,
    export: tuple[str, ...],
    show: tuple[str, ...],
    device_groups: tuple[str],
) -> None:
    """Run advanced shadowing analysis using Panorama data."""
    run_scenario_with_panorama(
        AdvancedShadowing,
        panorama_hostname=panorama_hostname,
        panorama_username=panorama_username,
        panorama_password=panorama_password,
        panorama_api_version=panorama_api_version,
        panorama_verify_ssl=panorama_verify_ssl,
        export=export,
        show=show,
        device_groups=device_groups,
    )


examples = [
    Example(
        name="shadowing-basic",
        scenario=Shadowing,
        data_dir="1",
        device_group="Example 1",
    ),
    Example(
        name="shadowing-multiple-dg",
        scenario=Shadowing,
        data_dir="2",
        device_group="Example 2",
    ),
    Example(
        name="shadowingvalue-basic",
        scenario=AdvancedShadowing,
        data_dir="3",
        device_group="Example 3 - Advanced",
        show=("table",),
    ),
    Example(
        name="shadowingvalue-with-export",
        scenario=AdvancedShadowing,
        data_dir="3",
        device_group="Example 3 - Advanced",
        show=("text",),
        export=("json",),
        args={"verify_ssl": True},
    ),
]


@main_run.command("example", no_args_is_help=True)
@export_show_options
@click.argument(
    "example",
    type=ExampleChoice(examples),
)
@click.option(
    "--device-groups",
    multiple=True,
    help="Device groups to analyze (can be specified multiple times)",
)
def run_example(
    export: tuple[str, ...],
    show: tuple[str, ...],
    device_groups: tuple[str],
    example: Example,
) -> None:
    """Run one of the examples."""
    logger.info(f"▶ Selected example: '{example.name}'")
    logger.info(
        "This is a demonstration run using example config/data. Results may not reflect your environment."
    )

    # Get the data directory from the example
    data_dir = example.get_data_dir()
    logger.info(f"Data directory: {data_dir.absolute()}")
    logger.info("Executing scenario with provided example data...")

    try:
        # Determine show and export options - CLI options override example defaults
        final_show = show if show else example.show
        final_export = export if export else example.export

        # Call run_scenario_with_mock_data directly
        run_scenario_with_mock_data(
            scenario_cls=example.scenario,
            data_dir=data_dir,
            device_group=example.device_group,
            device_groups=device_groups,
            show=final_show,
            export=final_export,
            **example.args,
        )

    except Exception as ex:
        logger.error(
            "Example run failed. This is expected if required files or connectivity are missing."
        )
        logger.error(f"Error: {ex}")
    finally:
        logger.info("Example execution completed")


if __name__ == "__main__":
    main()
