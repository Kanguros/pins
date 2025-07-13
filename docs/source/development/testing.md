# Testing Guide

This guide covers testing strategies, tools, and best practices for Policy Inspector.

## Test Categories

### Unit Tests

Test individual functions and classes in isolation:

```python
# tests/test_utils.py
import pytest
from policy_inspector.utils import parse_cidr, resolve_hostname

class TestParsingFunctions:
    """Test utility parsing functions."""

    def test_parse_cidr_valid(self):
        """Test parsing valid CIDR notation."""
        result = parse_cidr("192.168.1.0/24")
        assert result['network'] == "192.168.1.0"
        assert result['mask'] == 24
        assert result['hosts'] == 254

    def test_parse_cidr_invalid(self):
        """Test parsing invalid CIDR notation."""
        with pytest.raises(ValueError):
            parse_cidr("invalid-cidr")

    @pytest.mark.parametrize("hostname,expected", [
        ("localhost", "127.0.0.1"),
        ("invalid-hostname-12345", None),
    ])
    def test_resolve_hostname(self, hostname, expected):
        """Test hostname resolution."""
        result = resolve_hostname(hostname)
        assert result == expected
```

### Integration Tests

Test component interactions:

```python
# tests/test_integration/test_panorama_integration.py
import pytest
from unittest.mock import Mock, patch
from policy_inspector.panorama import PanoramaClient
from policy_inspector.scenario import ShadowingScenario

@pytest.mark.integration
class TestPanoramaIntegration:
    """Test Panorama API integration."""

    def setup_method(self):
        """Set up test client."""
        self.client = PanoramaClient(
            host="test-panorama.local",
            username="test",
            password="test"
        )

    @patch('policy_inspector.panorama.requests.get')
    def test_get_device_groups(self, mock_get):
        """Test retrieving device groups."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': {
                'device-group': [
                    {'@name': 'Production'},
                    {'@name': 'Staging'}
                ]
            }
        }
        mock_get.return_value = mock_response

        # Test the integration
        device_groups = self.client.get_device_groups()
        assert len(device_groups) == 2
        assert "Production" in device_groups
        assert "Staging" in device_groups

    @patch('policy_inspector.panorama.requests.get')
    def test_analyze_shadowing_end_to_end(self, mock_get):
        """Test complete shadowing analysis workflow."""
        # Mock rules response
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': {
                'security': {
                    'rules': {
                        'entry': [
                            {
                                '@name': 'rule1',
                                'source': 'any',
                                'destination': 'any',
                                'action': 'allow'
                            },
                            {
                                '@name': 'rule2',
                                'source': '192.168.1.0/24',
                                'destination': '10.0.0.0/8',
                                'action': 'allow'
                            }
                        ]
                    }
                }
            }
        }
        mock_get.return_value = mock_response

        # Run analysis
        rules = self.client.get_security_rules("Production")
        scenario = ShadowingScenario()
        results = scenario.analyze(rules)

        # Verify results
        assert len(results) > 0
        assert any(r['shadowed_rule'] == 'rule2' for r in results)
```

### API Tests

Test external API interactions:

```python
# tests/test_api/test_panorama_api.py
import pytest
import responses
from policy_inspector.panorama import PanoramaClient

@pytest.mark.api
class TestPanoramaAPI:
    """Test Panorama API calls."""

    @responses.activate
    def test_authentication(self):
        """Test API authentication."""
        # Mock authentication endpoint
        responses.add(
            responses.GET,
            "https://test-panorama.local/api/?type=keygen",
            json={"result": {"key": "test-api-key"}},
            status=200
        )

        client = PanoramaClient("test-panorama.local", "user", "pass")
        assert client.authenticate()
        assert client.api_key == "test-api-key"

    @responses.activate
    def test_get_rules_with_pagination(self):
        """Test retrieving rules with pagination."""
        # Mock paginated responses
        responses.add(
            responses.GET,
            "https://test-panorama.local/api/?type=config&action=get",
            json={
                "result": {
                    "security": {"rules": {"entry": [
                        {"@name": "rule1"},
                        {"@name": "rule2"}
                    ]}},
                    "@more": "true"
                }
            },
            status=200
        )

        responses.add(
            responses.GET,
            "https://test-panorama.local/api/?type=config&action=get&start=2",
            json={
                "result": {
                    "security": {"rules": {"entry": [
                        {"@name": "rule3"}
                    ]}}
                }
            },
            status=200
        )

        client = PanoramaClient("test-panorama.local", "user", "pass")
        rules = client.get_security_rules("Production")

        assert len(rules) == 3
        assert rules[0].name == "rule1"
        assert rules[2].name == "rule3"
```

### CLI Tests

Test command-line interface:

```python
# tests/test_cli.py
import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock
from policy_inspector.cli import main

class TestCLI:
    """Test command-line interface."""

    def setup_method(self):
        """Set up CLI test runner."""
        self.runner = CliRunner()

    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert "Policy Inspector" in result.output

    def test_help_command(self):
        """Test help command."""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "show" in result.output
        assert "export" in result.output

    @patch('policy_inspector.panorama.PanoramaClient')
    def test_show_shadowing_command(self, mock_client):
        """Test show shadowing command."""
        # Mock the client and analysis
        mock_instance = Mock()
        mock_instance.get_security_rules.return_value = []
        mock_client.return_value = mock_instance

        result = self.runner.invoke(main, [
            '--panorama-host', 'test.local',
            '--username', 'test',
            '--password', 'test',
            'show', 'shadowing'
        ])

        assert result.exit_code == 0

    def test_invalid_command(self):
        """Test invalid command handling."""
        result = self.runner.invoke(main, ['invalid-command'])
        assert result.exit_code != 0
        assert "No such command" in result.output

    @patch('policy_inspector.config.load_config')
    def test_config_file_loading(self, mock_load_config):
        """Test configuration file loading."""
        mock_load_config.return_value = {
            'panorama': {
                'host': 'config-host.local',
                'username': 'config-user'
            }
        }

        result = self.runner.invoke(main, [
            '--config', 'test-config.yaml',
            'show', 'device-groups'
        ])

        mock_load_config.assert_called_once_with('test-config.yaml')
```

## Test Configuration

### Pytest Configuration

```ini
# pytest.ini
[tool:pytest]
minversion = 8.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --cov=policy_inspector
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    slow: Slow tests
    requires_panorama: Tests requiring Panorama connection
```

### Test Environment Setup

```python
# tests/conftest.py
import pytest
import tempfile
import json
from pathlib import Path
from policy_inspector.model import SecurityRule, AddressObject

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    return Path(__file__).parent / "data"

@pytest.fixture
def temp_config_file():
    """Create temporary configuration file."""
    config = {
        'panorama': {
            'host': 'test-panorama.local',
            'username': 'test',
            'password': 'test'
        },
        'device_groups': ['test-group']
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        import yaml
        yaml.dump(config, f)
        yield f.name

    Path(f.name).unlink()

@pytest.fixture
def sample_security_rules():
    """Provide sample security rules for testing."""
    return [
        SecurityRule(
            name='allow-web-all',
            from_zone=['trust'],
            to_zone=['untrust'],
            source=['any'],
            destination=['any'],
            service=['web-browsing'],
            action='allow',
            enabled=True
        ),
        SecurityRule(
            name='allow-web-specific',
            from_zone=['trust'],
            to_zone=['untrust'],
            source=['192.168.1.0/24'],
            destination=['10.0.0.0/8'],
            service=['tcp-80'],
            action='allow',
            enabled=True
        ),
        SecurityRule(
            name='deny-all',
            from_zone=['any'],
            to_zone=['any'],
            source=['any'],
            destination=['any'],
            service=['any'],
            action='deny',
            enabled=True
        )
    ]

@pytest.fixture
def mock_panorama_client():
    """Provide mock Panorama client."""
    from unittest.mock import Mock

    client = Mock()
    client.get_device_groups.return_value = ['Production', 'Staging']
    client.get_security_rules.return_value = []
    client.get_address_objects.return_value = []

    return client
```

## Test Data Management

### Static Test Data

Organize test data in the `tests/data/` directory:

```
tests/data/
├── sample_rules.json
├── address_objects.json
├── device_groups.json
├── config_files/
│   ├── valid_config.yaml
│   └── invalid_config.yaml
└── api_responses/
    ├── auth_success.json
    └── rules_response.json
```

### Dynamic Test Data Generation

```python
# tests/factories.py
import factory
from policy_inspector.model import SecurityRule, AddressObject

class SecurityRuleFactory(factory.Factory):
    """Factory for creating test security rules."""

    class Meta:
        model = SecurityRule

    name = factory.Sequence(lambda n: f"rule-{n}")
    from_zone = factory.List(['trust'])
    to_zone = factory.List(['untrust'])
    source = factory.List(['any'])
    destination = factory.List(['any'])
    service = factory.List(['any'])
    action = 'allow'
    enabled = True

class AddressObjectFactory(factory.Factory):
    """Factory for creating test address objects."""

    class Meta:
        model = AddressObject

    name = factory.Sequence(lambda n: f"addr-{n}")
    type = 'ip-netmask'
    value = factory.Faker('ipv4_network')

# Usage in tests
def test_with_generated_data():
    rules = SecurityRuleFactory.create_batch(10)
    assert len(rules) == 10
    assert all(rule.name.startswith('rule-') for rule in rules)
```

## Performance Testing

### Load Testing

```python
# tests/test_performance.py
import pytest
import time
from policy_inspector.scenarios.shadowing import ShadowingScenario
from tests.factories import SecurityRuleFactory

@pytest.mark.slow
class TestPerformance:
    """Performance tests for Policy Inspector."""

    def test_shadowing_performance_large_ruleset(self):
        """Test shadowing analysis performance with large rule set."""
        # Generate large number of rules
        rules = SecurityRuleFactory.create_batch(1000)

        scenario = ShadowingScenario()

        start_time = time.time()
        results = scenario.analyze(rules)
        end_time = time.time()

        execution_time = end_time - start_time

        # Performance assertions
        assert execution_time < 30  # Should complete within 30 seconds
        assert len(results) >= 0  # Should return valid results

        print(f"Analyzed {len(rules)} rules in {execution_time:.2f} seconds")

    def test_memory_usage(self):
        """Test memory usage with large datasets."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create large dataset
        rules = SecurityRuleFactory.create_batch(5000)
        scenario = ShadowingScenario()
        results = scenario.analyze(rules)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory assertions (should not use more than 100MB)
        assert memory_increase < 100 * 1024 * 1024

        print(f"Memory increase: {memory_increase / 1024 / 1024:.2f} MB")
```

### Benchmark Tests

```python
# tests/test_benchmarks.py
import pytest
import time
from policy_inspector.resolver import AddressResolver

@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests for critical functions."""

    def test_address_resolution_benchmark(self, benchmark):
        """Benchmark address resolution performance."""
        resolver = AddressResolver()
        addresses = ['192.168.1.1', '10.0.0.1', 'google.com']

        def resolve_addresses():
            return [resolver.resolve(addr) for addr in addresses]

        result = benchmark(resolve_addresses)
        assert len(result) == 3

    def test_rule_parsing_benchmark(self, benchmark):
        """Benchmark rule parsing performance."""
        from policy_inspector.parser import parse_security_rule

        rule_data = {
            'name': 'test-rule',
            'source': 'any',
            'destination': 'any',
            'service': 'any',
            'action': 'allow'
        }

        result = benchmark(parse_security_rule, rule_data)
        assert result.name == 'test-rule'
```

## Test Automation

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on:
    push:
        branches: [main, develop]
    pull_request:
        branches: [main]

jobs:
    test:
        runs-on: ubuntu-latest
        strategy:
            matrix:
                python-version: ["3.10", "3.11", "3.12"]

        steps:
            - uses: actions/checkout@v3

            - name: Set up Python ${{ matrix.python-version }}
              uses: actions/setup-python@v4
              with:
                  python-version: ${{ matrix.python-version }}

            - name: Install Poetry
              uses: snok/install-poetry@v1

            - name: Install dependencies
              run: poetry install

            - name: Run linting
              run: poetry run ruff check

            - name: Run type checking
              run: poetry run mypy policy_inspector/

            - name: Run unit tests
              run: poetry run pytest tests/ -m "not integration and not slow"

            - name: Run integration tests
              run: poetry run pytest tests/ -m "integration"
              env:
                  PANORAMA_HOST: ${{ secrets.TEST_PANORAMA_HOST }}
                  PANORAMA_USERNAME: ${{ secrets.TEST_PANORAMA_USERNAME }}
                  PANORAMA_PASSWORD: ${{ secrets.TEST_PANORAMA_PASSWORD }}

            - name: Upload coverage reports
              uses: codecov/codecov-action@v3
              with:
                  file: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.1.0
      hooks:
          - id: ruff
            args: [--fix, --exit-non-zero-on-fix]
          - id: ruff-format

    - repo: https://github.com/pre-commit/pre-commit-hooks
      rev: v4.4.0
      hooks:
          - id: trailing-whitespace
          - id: end-of-file-fixer
          - id: check-yaml
          - id: check-added-large-files

    - repo: https://github.com/pre-commit/mirrors-mypy
      rev: v1.5.1
      hooks:
          - id: mypy
            additional_dependencies: [types-requests, types-PyYAML]

    - repo: local
      hooks:
          - id: tests
            name: Run tests
            entry: poetry run pytest tests/ -m "not slow"
            language: system
            pass_filenames: false
            always_run: true
```

## Test Coverage

### Coverage Configuration

```ini
# .coveragerc
[run]
source = policy_inspector
omit =
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = htmlcov
```

### Coverage Goals

- **Minimum Coverage**: 80%
- **Unit Tests**: 90% coverage for core modules
- **Integration Tests**: Cover all major workflows
- **CLI Tests**: Cover all command paths

### Running Coverage

```bash
# Run tests with coverage
poetry run pytest --cov=policy_inspector --cov-report=html

# View coverage report
open htmlcov/index.html

# Coverage summary
poetry run coverage report

# Find uncovered lines
poetry run coverage report --show-missing
```

## Debugging Tests

### Debug Mode

```bash
# Run tests in debug mode
poetry run pytest -v -s --tb=long

# Run specific test with debugging
poetry run pytest tests/test_scenario.py::TestShadowingScenario::test_detect_shadowing -v -s

# Run with pdb on failure
poetry run pytest --pdb
```

### Test Isolation

```python
# Use monkeypatch for isolation
def test_with_environment_variable(monkeypatch):
    monkeypatch.setenv("PANORAMA_HOST", "test.local")
    # Test code that uses the environment variable

# Use temporary directories
def test_with_temp_file(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    # Test code that uses the file
```

## Continuous Testing

### Test Automation Strategy

1. **Fast Feedback Loop**: Run unit tests on every commit
2. **Integration Testing**: Run on pull requests
3. **Performance Testing**: Run nightly on main branch
4. **End-to-End Testing**: Run before releases

### Test Environment Management

```bash
# Development testing
poetry run pytest tests/ -m "not slow and not integration"

# CI testing
poetry run pytest tests/ -m "not slow" --junitxml=test-results.xml

# Nightly testing
poetry run pytest tests/ --cov=policy_inspector --cov-report=xml

# Release testing
poetry run pytest tests/ --cov=policy_inspector --cov-fail-under=80
```

## Best Practices

### Test Design Principles

1. **Fast**: Tests should run quickly
2. **Independent**: Tests should not depend on each other
3. **Repeatable**: Tests should produce consistent results
4. **Self-Validating**: Tests should clearly pass or fail
5. **Timely**: Tests should be written close to the code

### Common Patterns

```python
# Arrange-Act-Assert pattern
def test_rule_analysis():
    # Arrange
    rule = SecurityRule(name="test", action="allow")
    analyzer = RuleAnalyzer()

    # Act
    result = analyzer.analyze(rule)

    # Assert
    assert result.is_valid
    assert result.score > 0

# Test data builders
def create_allow_rule(name="test-rule", source="any"):
    return SecurityRule(
        name=name,
        source=source,
        destination="any",
        action="allow"
    )

# Context managers for setup/teardown
@pytest.fixture
def temp_config():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
        yaml.dump({'test': 'config'}, f)
        f.flush()
        yield f.name
```

Testing is crucial for maintaining code quality and reliability. Follow these guidelines to ensure comprehensive test coverage and maintainable test code.
