import click

from policy_inspector.cli.options import (
    display_option,
    export_options,
    panorama_options,
)
from policy_inspector.scenario import run_scenario
from policy_inspector.scenarios.shadowing.scenario import AdvancedShadowing


@click.command(name=AdvancedShadowing.name.lower())
@display_option
@export_options
@panorama_options
def advanced_shadowing_command(**kwargs):
    """Dynamic scenario command."""
    run_scenario(AdvancedShadowing, **kwargs)
