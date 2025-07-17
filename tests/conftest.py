from pathlib import Path

import pytest

from policy_inspector.cli.loader import ScenarioLoader


def gather_data_files(match: str):
    data_dir = Path(__file__).parent / "data"
    return list(data_dir.glob(match))


@pytest.fixture(scope="session", autouse=True)
def load_scenarios():
    """Ensure scenarios are dynamically loaded before tests."""
    scenarios_dir = (
        Path(__file__).parent.parent / "policy_inspector" / "scenarios"
    )
    loader = ScenarioLoader(scenario_directories=[str(scenarios_dir)])
    loader.discover_scenarios()
