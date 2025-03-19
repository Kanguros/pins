import pytest
from click.testing import CliRunner

from policy_inspector.__main__ import main


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


# def test_command_run_example(runner):
#     result = runner.invoke(main, ["run-example"])
#     assert result.exit_code == 0
#     phrases = [
#         " [rule3-allow-dns] Rule not shadowed ",
#         "[rule-example2] Rule is shadowed by: rule-example1",
#     ]
#     for phrase in phrases:
#         assert phrase in result.output
