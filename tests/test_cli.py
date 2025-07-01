import pytest
from click.testing import CliRunner

from policy_inspector import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.parametrize("args", [None, ["--help"]])
def test_main_command_help(runner, args):
    result = runner.invoke(cli.main, args, catch_exceptions=False)

    assert result.exit_code == 0
    phrases = [" Commands ", "run", "Usage"]
    for phrase in phrases:
        assert phrase in result.output


@pytest.mark.parametrize("arg", [None, "--help"])
def test_run_command(runner, arg):
    args = ["run"]
    if arg:
        args.append(arg)
    result = runner.invoke(cli.main, args)
    assert result.exit_code == 0
    phrases = ["Scenarios", "Execute a Scenario.", "example"]
    for phrase in phrases:
        assert phrase in result.output


def test_list_command(runner):
    cli.Scenario.get_available()
    result = runner.invoke(cli.main_list)
    assert result.exit_code == 0
    for phrase in [
        "check_",
    ]:
        assert phrase in result.output


def test_list_command_verbose(runner):
    cli.Scenario.get_available()
    result = runner.invoke(cli.main_list, ["-vvv"])
    assert result.exit_code == 0
    for phrase in [
        "check_",
    ]:
        assert phrase in result.output


@pytest.mark.parametrize(
    "name",
    [
        pytest.param(
            "shadowingvalue-basic",
            marks=pytest.mark.skip(reason="requires panorama connection"),
        ),
        pytest.param(
            "shadowingvalue-ssl",
            marks=pytest.mark.skip(reason="requires panorama connection"),
        ),
        "shadowing-basic",
        "shadowing-multiple-dg",
    ],
)
def test_run_example(runner, name):
    result = runner.invoke(cli.run_example, [name], catch_exceptions=True)
    phrases = [
        f"Selected example: '{name}'",
        "Executing scenario with",
        "results",
    ]
    assert result.exit_code == 0
    for phrase in phrases:
        assert phrase in result.output
