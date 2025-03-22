from pathlib import Path


def get_example_security_rules_path() -> Path:
    data_dir = Path(__file__).parent / "example"
    return data_dir / "securityrule.example1.json"


def get_example_address_groups_path() -> Path:
    data_dir = Path(__file__).parent / "example"
    return data_dir / "addressgroup.example1.json"


def get_example_address_objects_path() -> Path:
    data_dir = Path(__file__).parent / "example"
    return data_dir / "addressobject.example1.json"


class MockObject:
    """Mock class to use in tests."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
