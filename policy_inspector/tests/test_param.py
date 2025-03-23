import json
import logging

import click
import pytest
from click.testing import CliRunner

from policy_inspector.param import model_argument, verbose_option


# Fixtures
@pytest.fixture
def cli_runner():
    return CliRunner()


class TestModel:
    @classmethod
    def parse_json(cls, data):
        return cls()


@click.command()
@verbose_option()
def test_cmd_verbose():
    logging.debug("Test debug message")


def test_verbose_option_in_help(cli_runner):
    result = cli_runner.invoke(test_cmd_verbose, ["--help"])
    assert "--verbose" in result.stdout


@click.command()
@model_argument(TestModel, "models")
def test_cmd_model(models):
    click.echo(f"Loaded: {len(models)} items")


def test_model_argument_file_loading(cli_runner, tmp_path):
    test_file = tmp_path / "valid.json"
    test_file.write_text(json.dumps([{"name": "test"}]))
    result = cli_runner.invoke(test_cmd_model, [str(test_file)])
    assert result.exit_code == 0
    assert "Loaded: 1 items" in result.output


def test_model_argument_file_not_found(cli_runner):
    result = cli_runner.invoke(test_cmd_model, ["missing.json"])
    assert result.exit_code == 2
    assert "File 'missing.json' not found" in str(result.output)
