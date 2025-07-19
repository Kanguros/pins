import click

from policy_inspector.scenarios.shadowing.scenario import Shadowing


@click.command(name=Shadowing.name.lower())
@display_option
@export_options
@click.pass_context
def shadowing(ctx: click.Context, **kwargs):
    """Dynamic scenario command."""
    v = "\n".join([f"{k}={v}" for k, v in ctx.__dict__.items()])
    print(f"SCENARIO COMMAND:\n{v}")

    run_scenario(Shadowing, **kwargs)