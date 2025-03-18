import pytest
from click.testing import CliRunner

from rules_check.__main__ import main


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.mark.parametrize("args", [None, ["--help"]])
def test_command_rc_help(runner, args):
    result = runner.invoke(main, args, color=False)

    assert result.exit_code == 0
    phrases = [" Commands ", "run", "Usage"]
    for phrase in phrases:
        assert phrase in result.output


def test_command_run(runner):
    result = runner.invoke(main, "run", color=False)
    assert result.exit_code == 0
    phrases = [" Commands ", "run", "Usage"]
    for phrase in phrases:
        assert phrase in result.output
