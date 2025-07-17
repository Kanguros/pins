import logging
from textwrap import dedent

try:
    import rich_click as click

    click.rich_click.SHOW_ARGUMENTS = True
    click.rich_click.TEXT_MARKUP = "markdown"
    click.rich_click.USE_MARKDOWN = True
    click.rich_click.SHOW_METAVARS_COLUMN = True
except ImportError:
    import click

from policy_inspector.cli.lazy_group import ScenarioCLI, add_panorama_options
from policy_inspector.cli.loader import ScenarioLoader
from policy_inspector.cli.base_group import VerboseGroup
from policy_inspector.cli.base_group import VerboseGroup
from policy_inspector.config import (
    config_option,
    get_scenario_directories_from_config,
)
from policy_inspector.mock_panorama import MockPanoramaConnector
from policy_inspector.utils import (
    Example,
    ExampleChoice,
    config_logger,
)

config_logger()


logger = logging.getLogger(__name__)


@click.group(no_args_is_help=True, add_help_option=True, cls=VerboseGroup)
@click.option("--config", default="config.yaml", help="Configuration file path")
@click.pass_context
def main(ctx: click.Context, config: str):
    """Policy Inspector - Analyze Palo Alto firewall policies.

    Enhanced version with dynamic scenario loading and better export/display capabilities.
    Scenarios can be loaded from built-in modules or custom directories specified in config.
    """
    ctx.ensure_object(dict)
    ctx.obj["config_file"] = config


@main.command("list")
@click.pass_context
def main_list(ctx: click.Context) -> None:
    """List available analysis scenarios with descriptions."""
    config_file = ctx.obj.get("config_file", "config.yaml")
    scenario_directories = get_scenario_directories_from_config(config_file)

    loader = ScenarioLoader(scenario_directories)
    scenarios = loader.discover_scenarios()

    click.echo("")
    click.echo("-" * 60)
    click.echo("")
    click.echo(f"Found {len(scenarios)} available scenarios:")
    click.echo("")

    for scenario_name in sorted(scenarios.keys()):
        scenario_info = loader.get_scenario_info(scenario_name)
        if scenario_info:
            click.echo(f"→ '{scenario_name}'")
            click.echo(f"  {scenario_info['description']}")

            # Show available formats
            if "export_formats" in scenario_info:
                export_formats = ", ".join(scenario_info["export_formats"])
                click.echo(f"  Export formats: {export_formats}")

            if "display_formats" in scenario_info:
                display_formats = ", ".join(scenario_info["display_formats"])
                click.echo(f"  Display formats: {display_formats}")

            click.echo("")

    click.echo("-" * 60)
    click.echo("")


@main.group("run", no_args_is_help=True, cls=ScenarioCLI)
@config_option()
@add_panorama_options
@click.pass_context
def main_run(
    ctx: click.Context,
    panorama_hostname: str,
    panorama_username: str,
    panorama_password: str,
    panorama_api_version: str = "v11.1",
    panorama_verify_ssl: bool = False,
    **kwargs,
):
    """Execute Policy Inspector scenarios.

    Run security policy analysis scenarios against your Panorama.
    """
    # Get scenario directories from config
    config_file = ctx.obj.get("config_file", "config.yaml")
    scenario_directories = get_scenario_directories_from_config(config_file)

    if not hasattr(main_run, "_scenario_cli_initialized"):
        main_run.cls = ScenarioCLI(scenario_directories=scenario_directories)
        main_run._scenario_cli_initialized = True

    ctx.ensure_object(dict)
    ctx.obj.update(
        {
            "panorama_hostname": panorama_hostname,
            "panorama_username": panorama_username,
            "panorama_password": panorama_password,
            "panorama_api_version": panorama_api_version,
            "panorama_verify_ssl": panorama_verify_ssl,
            "config_file": config_file,
            "scenario_directories": scenario_directories,
        }
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


@main.command("example", no_args_is_help=True)
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
@click.option(
    "--device-groups",
    multiple=True,
    help="Device groups to analyze (can be specified multiple times)",
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


@main.command("info")
@click.argument("scenario_name")
@click.pass_context
def scenario_info(ctx: click.Context, scenario_name: str) -> None:
    """Get detailed information about a specific scenario."""
    config_file = ctx.obj.get("config_file", "config.yaml")
    scenario_directories = get_scenario_directories_from_config(config_file)

    loader = ScenarioLoader(scenario_directories)
    info = loader.get_scenario_info(scenario_name)

    if not info:
        click.echo(f"Scenario '{scenario_name}' not found.", err=True)
        return

    click.echo(f"Scenario: {info['name']}")
    click.echo(f"Class: {info['class_name']}")
    click.echo(f"Module: {info['module']}")
    click.echo(f"Description: {info['description']}")
    click.echo("")
    click.echo("Help:")
    click.echo(dedent(info["help_text"]))

    if "export_formats" in info:
        click.echo(
            f"Available export formats: {', '.join(info['export_formats'])}"
        )

    if "display_formats" in info:
        click.echo(
            f"Available display formats: {', '.join(info['display_formats'])}"
        )
