import pytest
from click.testing import CliRunner

from policy_inspector import cli


@pytest.fixture
def runner():
    return CliRunner()


# @click.command()
# @verbose_option(logging.getLogger())
# def fake_cmd_verbose():
#     logging.info("Test info message")
#     logging.debug("Test debug message")
#
#
# def test_no_verbose_option(runner):
#     result = runner.invoke(fake_cmd_verbose)
#     assert "Test info message" in result.stdout
#     assert "Test debug message" not in result.stdout
#
# def test_with_verbose_option(runner):
#     result = runner.invoke(fake_cmd_verbose, ["-v"])
#     assert "Test info message" in result.stdout
#     assert "Test debug message" in result.stdout


@pytest.mark.parametrize("args", [None, ["--help"]])
def test_main_command_help(runner, args):
    result = runner.invoke(cli.main, args, catch_exceptions=False)

    assert result.exit_code == 0
    phrases = [" Commands ", "run", "Usage"]
    for phrase in phrases:
        assert phrase in result.output


@pytest.mark.parametrize("arg", [None, "--help"])
def test_run_command(arg):
    args = ["run"]
    if arg:
        args.append(arg)
    result = CliRunner().invoke(cli.main, args)

    assert result.exit_code == 0
    for phrase in [
        " Execute Scenario.",
        "shadowing",
        "complex_shadowing",
    ]:
        assert phrase in result.output


def test_list_command(runner):
    result = runner.invoke(cli.main_list)
    assert result.exit_code == 0
    for phrase in [
        "Available Scenarios:",
        "ShadowingByValue",
        "Shadowing",
    ]:
        assert phrase in result.output


def test_list_command_verbose(runner):
    result = runner.invoke(cli.main_list, ["-v"])
    assert result.exit_code == 0
    for phrase in [
        "Available Scenarios:",
        "ShadowingByValue",
        "Shadowing",
        "check_",
    ]:
        assert phrase in result.output


@pytest.mark.parametrize("name", [example.name for example in cli.examples])
def test_run_example(name):
    result = CliRunner().invoke(
        cli.run_example, [name], color=False, catch_exceptions=False
    )
    print(result.stdout)
    assert result.exit_code == 0
