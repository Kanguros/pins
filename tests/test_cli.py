import logging

import click
import pytest
from click.testing import CliRunner

from policy_inspector import cli
from policy_inspector.utils import verbose_option


@click.command()
@verbose_option()
def fake_cmd_verbose():
    logging.debug("Test debug message")


def test_verbose_option_in_help():
    result = CliRunner().invoke(fake_cmd_verbose, ["--help"])
    assert "--verbose" in result.stdout


@pytest.mark.parametrize("args", [None, ["--help"]])
def test_main_command_help(args):
    result = CliRunner().invoke(cli.main, args, color=True)

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
    phrases = [
        " Execute Scenario.",
        "shadowing",
        "complex_shadowing",
    ]
    for phrase in phrases:
        assert phrase in result.output


@pytest.mark.parametrize("arg", [None, "--help"])
def test_run_list_command(arg):
    args = ["list"]
    if arg:
        args.append(arg)

    result = CliRunner().invoke(cli.main, args)
    assert result.exit_code == 0


# @pytest.mark.parametrize("name", list(cli.examples_by_name.keys()))
# def test_run_example(name):
#     result = CliRunner().invoke(
#         cli.run_example, [name], color=False, catch_exceptions=False
#     )
#     print(result.stdout)
#     assert result.exit_code == 0
