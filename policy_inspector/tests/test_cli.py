import pytest
from click.testing import CliRunner

from policy_inspector.__main__ import main


@pytest.mark.parametrize("args", [None, ["--help"]])
def test_main_command_help(args):
    result = CliRunner().invoke(main, args, color=True)

    assert result.exit_code == 0
    phrases = [" Commands ", "run", "Usage"]
    for phrase in phrases:
        assert phrase in result.output


@pytest.mark.parametrize("arg", [None, "--help"])
def test_run_command(arg):
    args = ["run"]
    if arg:
        args.append(arg)
    result = CliRunner().invoke(main, args)

    assert result.exit_code == 0
    phrases = [
        " Execute one of the predefined scenarios. ",
        "shadowing",
        "complex_shadowing",
    ]
    for phrase in phrases:
        assert phrase in result.output


@pytest.mark.parametrize("arg", [None, "--help"])
def test_run_list(arg):
    args = ["list"]
    if arg:
        args.append(arg)

    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0
    phrases = [
        " Execute one of the predefined scenarios. ",
        "shadowing",
        "complex_shadowing",
    ]
    for phrase in phrases:
        assert phrase in result.output
