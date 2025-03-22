from pathlib import Path


class MockObject:
    """Mock class to use in tests."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
