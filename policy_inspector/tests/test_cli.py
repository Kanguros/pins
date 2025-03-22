import os

import pytest
from click.testing import CliRunner

from policy_inspector.__main__ import main

os.environ["DISABLE_RICH_CLICK"] = "1"


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.mark.parametrize("args", [None, ["--help"]])
def test_main_command_help(runner, args):
    result = runner.invoke(main, args, color=False)

    assert result.exit_code == 0
    phrases = [" Commands ", "run", "Usage"]
    for phrase in phrases:
        assert phrase in result.output


# def test_run_command(runner):
#     result = runner.invoke(main, ["run"])
#     assert result.exit_code == 0
#     phrases = [
#         " [rule3-allow-dns] Rule not shadowed ",
#         "[rule-example2] Rule is shadowed by: rule-example1",
#     ]
#     for phrase in phrases:
#         assert phrase in result.output
