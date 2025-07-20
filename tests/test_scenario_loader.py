import sys
from pathlib import Path

import pytest

# Add mock_scenarios directory to Python path
mock_scenarios_path = Path(__file__).parent / "mock_scenarios"
if str(mock_scenarios_path) not in sys.path:
    sys.path.insert(0, str(mock_scenarios_path))

from policy_inspector.cli.loader import ScenarioLoader


@pytest.fixture
def mock_scenario_loader():
    """Fixture for creating a mock ScenarioLoader instance."""
    return ScenarioLoader(scenario_directories=[str(mock_scenarios_path)])


def test_discover_scenarios(mock_scenario_loader):
    """Test the discover_scenarios method."""
    scenarios = mock_scenario_loader.discover_scenarios()
    assert isinstance(scenarios, dict)
    assert "example" in scenarios


def test_handle_example_command(mock_scenario_loader, caplog):
    """Test the handle_example_command method."""
    with caplog.at_level("INFO"):
        mock_scenario_loader.handle_example_command()
    assert "Running example scenario..." in caplog.text


@pytest.fixture
def mock_builtin_scenarios(tmp_path):
    """Fixture to create mock built-in scenarios."""
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir()

    # Create mock scenario folders and cmd modules
    for name in ["scenario_a", "scenario_b"]:
        scenario_folder = scenarios_dir / name
        scenario_folder.mkdir()
        cmd_file = scenario_folder / "cmd.py"
        cmd_file.write_text(
            """
            import click

            @click.command()
            def click_command():
                pass
            """
        )

    return str(scenarios_dir)


def test_load_builtin_scenarios(mock_builtin_scenarios):
    """Test loading built-in scenarios."""
    loader = ScenarioLoader()
    loader.scenario_directories = [mock_builtin_scenarios]
    scenarios = loader._load_builtin_scenarios()
    assert "scenario_a" in scenarios
    assert "scenario_b" in scenarios


def test_load_custom_scenarios(mock_builtin_scenarios):
    """Test loading custom scenarios."""
    loader = ScenarioLoader(scenario_directories=[mock_builtin_scenarios])
    scenarios = loader._load_scenarios_from_directory(mock_builtin_scenarios)
    assert "scenario_a" in scenarios
    assert "scenario_b" in scenarios
