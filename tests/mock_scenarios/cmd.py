import click

from .example_scenario import ExampleScenario


@click.command(ExampleScenario.name.lower())
def mock_scenarios():
    """Example click command for testing."""
    scenario = ExampleScenario(name="example")
    scenario.run()
    click.echo("Example scenario executed.")
