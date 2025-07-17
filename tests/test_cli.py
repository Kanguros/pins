import pytest
from click.testing import CliRunner

from policy_inspector import __main__
from policy_inspector.scenario import Scenario


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli_setup():
    """Initialize ScenarioCLI for tests with scenario directories."""
    from policy_inspector.lazy_group import ScenarioCLI

    scenario_directories = ["d:\\Projects\\policy_inspector\\policy_inspector\\scenarios"]
    __main__.main.cls = ScenarioCLI(scenario_directories=scenario_directories)
    return __main__


@pytest.mark.parametrize("args", [None, ["--help"]])
def test_main_command_help(runner, args):
    result = runner.invoke(__main__.main, args, catch_exceptions=False)
    assert result.exit_code == 0
    phrases = [" Commands ", "run", "Usage"]
    for phrase in phrases:
        assert phrase in result.output


@pytest.mark.parametrize("arg", [None, "--help"])
def test_run_command(runner, arg):
    args = ["run"]
    if arg:
        args.append(arg)
    result = runner.invoke(__main__.main, args)
    assert result.exit_code == 0
    phrases = ["Usage", "COMMAND", "Execute Policy Inspector scenarios"]
    for phrase in phrases:
        assert phrase in result.output


def test_list_command(runner):
    Scenario.get_available()
    result = runner.invoke(__main__.main, "list", catch_exceptions=False)
    assert result.exit_code == 0, (
        f"Non-zero exit code. Output:\n{result.output}"
    )
    assert (
        "Shadowing" in result.output or "AdvancedShadowing" in result.output
    ), f"No scenario name found in output:\n{result.output}"


def test_list_command_verbose(runner):
    Scenario.get_available()
    result = runner.invoke(__main__.main, ["list", "-vvv"])
    assert result.exit_code == 0
    for phrase in [
        "check_",
        "Shadowing",
        "AdvancedShadowing",
    ]:
        assert phrase in result.output


@pytest.mark.parametrize(
    "name",
    [
        "shadowing-basic",
        "shadowing-multiple-dg",
    ],
)
def test_run_example(runner, name):
    result = runner.invoke(__main__.run_example, [name], catch_exceptions=True)
    phrases = [
        f"Selected example: '{name}'",
        "Executing scenario with",
        "Example execution completed",
    ]
    assert result.exit_code == 0, (
        f"Exit code {result.exit_code}, output: {result.output}"
    )
    for phrase in phrases:
        assert phrase in result.output


@pytest.mark.parametrize(
    "name,export_format",
    [
        ("shadowing-basic", "json"),
        ("shadowing-basic", "html"),
        ("shadowing-multiple-dg", "json"),
        ("shadowing-multiple-dg", "csv"),
    ],
)
def test_run_example_with_export(runner, name, export_format):
    """Test examples with different export formats."""
    result = runner.invoke(
        __main__.run_example,
        [name, "--export", export_format],
        catch_exceptions=True,
    )
    phrases = [
        f"Selected example: '{name}'",
        "Executing scenario with",
        "Example execution completed",
    ]
    assert result.exit_code == 0, (
        f"Exit code {result.exit_code}, output: {result.output}"
    )
    for phrase in phrases:
        assert phrase in result.output


@pytest.mark.parametrize(
    "name,show_format",
    [
        ("shadowing-basic", "text"),
        ("shadowing-basic", "table"),
        ("shadowing-multiple-dg", "text"),
        ("shadowing-multiple-dg", "table"),
    ],
)
def test_run_example_with_show(runner, name, show_format):
    """Test examples with different show formats."""
    result = runner.invoke(
        __main__.run_example, [name, "--show", show_format], catch_exceptions=True
    )
    phrases = [
        f"Selected example: '{name}'",
        "Executing scenario with",
        "Example execution completed",
    ]
    assert result.exit_code == 0, (
        f"Exit code {result.exit_code}, output: {result.output}"
    )
    for phrase in phrases:
        assert phrase in result.output


@pytest.mark.parametrize(
    "name",
    [
        "shadowing-basic",
        "shadowing-multiple-dg",
    ],
)
def test_run_example_with_device_groups(runner, name):
    """Test examples with custom device groups."""
    result = runner.invoke(
        __main__.run_example,
        [name, "--device-groups", "CustomDG1", "--device-groups", "CustomDG2"],
        catch_exceptions=True,
    )
    phrases = [
        f"Selected example: '{name}'",
        "Executing scenario with",
        "Example execution completed",
    ]
    assert result.exit_code == 0, (
        f"Exit code {result.exit_code}, output: {result.output}"
    )
    for phrase in phrases:
        assert phrase in result.output


def test_run_example_with_combined_options(runner):
    """Test example with multiple options combined."""
    result = runner.invoke(
        __main__.run_example,
        [
            "shadowing-basic",
            "--export",
            "json",
            "--show",
            "table",
            "--device-groups",
            "TestDG",
        ],
        catch_exceptions=True,
    )
    phrases = [
        "Selected example: 'shadowing-basic'",
        "Executing scenario with",
        "Example execution completed",
    ]
    assert result.exit_code == 0, (
        f"Exit code {result.exit_code}, output: {result.output}"
    )
    for phrase in phrases:
        assert phrase in result.output
