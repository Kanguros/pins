import logging

import click
import pytest
from click.testing import CliRunner

from policy_inspector.param import verbose_option


# Fixtures
@pytest.fixture
def cli_runner():
    return CliRunner()

