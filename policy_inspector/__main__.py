import logging

from policy_inspector.cli.options import config_option

try:
    import rich_click as click

    click.rich_click.SHOW_ARGUMENTS = True
    click.rich_click.TEXT_MARKUP = "markdown"
    click.rich_click.USE_MARKDOWN = True
    click.rich_click.SHOW_METAVARS_COLUMN = True
except ImportError:
    import click

from policy_inspector.cli.groups import LazyGroup, VerboseGroup
from policy_inspector.cli.loader import ScenarioLoader
from policy_inspector.utils import (
    config_logger,
)

config_logger()


logger = logging.getLogger(__name__)


@click.group(no_args_is_help=True, cls=VerboseGroup)
@config_option
@click.pass_context
def main(ctx: click.Context):
    """Policy Inspector - Analyze Palo Alto firewall policies.

    Enhanced version with dynamic scenario loading and better export/display capabilities.
    Scenarios can be loaded from built-in modules or custom directories specified in config.
    """


@main.command("list", cls=LazyGroup)
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


@main.group("run", cls=LazyGroup)
@click.pass_context
def main_run(ctx: click.Context):
    """Execute Policy Inspector scenarios.

    Run security policy analysis scenarios against your Panorama.
    """
