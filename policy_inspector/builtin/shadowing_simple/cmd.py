import click

from policy_inspector.cli.options import (
    display_option,
    export_options,
    panorama_options,
)
from policy_inspector.scenario import run_scenario
from policy_inspector.builtin.shadowing_simple.scenario import Shadowing


@click.command(name=Shadowing.name.lower())
@display_option
@export_options
@panorama_options
def shadowing_simple(**kwargs):
    """Dynamic scenario command."""
    run_scenario(Shadowing, **kwargs)
