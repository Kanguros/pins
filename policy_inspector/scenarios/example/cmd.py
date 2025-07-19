import click

from policy_inspector.cli.loader import ScenarioLoader
from policy_inspector.config import (
    get_scenario_directories_from_config,
)
from policy_inspector.mock_panorama import MockPanoramaConnector
from policy_inspector.utils import (
    Example,
    ExampleChoice,
)

examples = [
    Example(
        name="shadowing-basic",
        scenario=None,  # Will be loaded dynamically
        data_dir="1",
        device_group="Example 1",
    ),
    Example(
        name="shadowing-multiple-dg",
        scenario=None,  # Will be loaded dynamically
        data_dir="2",
        device_group="Example 2",
    ),
]


@click.command("example", no_args_is_help=True)
@click.option(
    "--show",
    multiple=True,
    type=click.Choice(["text", "json", "table", "rich"]),
    default=["text"],
    help="Display formats (can be specified multiple times)",
)
@click.option(
    "--export",
    multiple=True,
    type=click.Choice(["json", "yaml", "csv", "html"]),
    help="Export formats (can be specified multiple times)",
)
@click.option(
    "--export-dir", default=".", help="Directory to save exported files"
)
@click.argument(
    "example",
    type=ExampleChoice(examples),
)
@click.pass_context
def run_example(
    ctx: click.Context,
    show: tuple[str, ...],
    export: tuple[str, ...],
    export_dir: str,
    device_groups: tuple[str],
    example: Example,
) -> None:
    """Run built-in examples with sample data.

    Try Policy Inspector with included sample data before connecting
    to your Panorama. No credentials required.

    Available examples:
    - shadowing-basic: Simple shadowing detection
    - shadowing-multiple-dg: Multiple device group analysis
    """
    logger.info(f"▶ Selected example: '{example.name}'")
    logger.info(
        "This is a demonstration run using example config/data. Results may not reflect your environment."
    )

    # Get the data directory from the example
    data_dir = example.get_data_dir()
    logger.info(f"Data directory: {data_dir.absolute()}")
    logger.info("Executing scenario with provided example data...")

    try:
        # Create mock panorama connector
        panorama = MockPanoramaConnector(
            data_dir=data_dir,
            device_group=example.device_group,
        )

        # Get scenario directories from config
        config_file = ctx.obj.get("config_file", "config.yaml")
        scenario_directories = get_scenario_directories_from_config(config_file)

        # Load scenario dynamically
        loader = ScenarioLoader(scenario_directories)
        scenarios = loader.discover_scenarios()

        # Try to find a shadowing scenario
        scenario_cls = None
        for name, cls in scenarios.items():
            if "shadow" in name.lower():
                scenario_cls = cls
                break

        if not scenario_cls:
            logger.error("No shadowing scenario found for example")
            return

        # Use provided device_groups or default to the main device_group
        device_groups_list = (
            list(device_groups) if device_groups else [example.device_group]
        )

        # Create and run scenario
        scenario = scenario_cls(
            panorama=panorama,
            device_groups=device_groups_list,
            export_dir=export_dir,
            **example.args,
        )

        scenario.execute_and_analyze()

        if show:
            scenario.show(show)
        if export:
            exported_files = scenario.export(export, export_dir)
            for format_name, file_path in exported_files.items():
                logger.info(f"Exported {format_name.upper()}: {file_path}")

    except Exception as ex:
        logger.error(
            "Example run failed. This is expected if required files or connectivity are missing."
        )
        logger.error(f"Error: {ex}")
    finally:
        logger.info("Example execution completed")