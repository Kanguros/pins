# Contributing to Policy Inspector

We welcome contributions to Policy Inspector! This guide will help you get started with contributing to the project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management
- Git for version control

### Setting Up the Development Environment

1. **Clone the repository:**

```bash
git clone https://github.com/your-org/policy-inspector.git
cd policy-inspector
```

2. **Install dependencies:**

```bash
# Install all dependencies including dev dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

3. **Verify the setup:**

```bash
# Run tests
poetry run pytest

# Run linting
poetry run ruff check

# Check formatting
poetry run ruff format --check
```

## Code Standards

### Style Guidelines

- Follow PEP 8 style guidelines
- Use Black-compatible formatting (configured via Ruff)
- Line length: 80 characters
- Use snake_case for variables and functions
- Use PascalCase for classes

### Type Annotations

All public functions and methods must have type annotations:

```python
from typing import List, Dict, Optional
from policy_inspector.model import SecurityRule

def analyze_rules(
    rules: List[SecurityRule],
    config: Dict[str, str]
) -> Optional[List[Dict[str, str]]]:
    """Analyze security rules for issues.

    Args:
        rules: List of security rules to analyze
        config: Configuration parameters

    Returns:
        List of analysis results or None if no issues found
    """
    # Implementation here
    pass
```

### Documentation Standards

- All public functions must have docstrings
- Use Google-style docstrings
- Include type information in docstrings
- Provide examples where helpful

Example:

```python
def detect_shadowing(
    rules: List[SecurityRule],
    algorithm: str = "overlap"
) -> List[ShadowingResult]:
    """Detect shadowed rules in a security policy.

    This function analyzes a list of security rules to identify rules
    that will never match due to preceding rules with broader scope.

    Args:
        rules: List of security rules to analyze, in order of evaluation
        algorithm: Detection algorithm to use ('overlap', 'subnet', 'port')

    Returns:
        List of shadowing results, each containing the shadowed rule,
        shadowing rule, and explanation

    Raises:
        ValueError: If algorithm is not supported

    Example:
        >>> rules = [rule1, rule2, rule3]
        >>> results = detect_shadowing(rules, algorithm='overlap')
        >>> for result in results:
        ...     print(f"{result.shadowed_rule} is shadowed by {result.shadowing_rule}")
    """
    # Implementation here
    pass
```

## Testing

### Test Structure

Tests are organized in the `tests/` directory:

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_cli.py             # CLI testing
├── test_scenario.py        # Scenario testing
├── test_model/             # Model testing
│   ├── test_security_rule.py
│   └── test_address_object.py
└── data/                   # Test data files
    ├── sample_rules.json
    └── test_config.yaml
```

### Writing Tests

Use pytest for all tests:

```python
import pytest
from policy_inspector.model import SecurityRule
from policy_inspector.scenarios.shadowing import ShadowingScenario

class TestShadowingScenario:
    """Test shadowing detection scenario."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scenario = ShadowingScenario()
        self.rules = [
            SecurityRule(
                name='allow-web-all',
                source='any',
                destination='any',
                ports=['80', '443']
            ),
            SecurityRule(
                name='allow-web-specific',
                source='192.168.1.0/24',
                destination='10.0.0.0/8',
                ports=['80']
            )
        ]

    def test_detect_simple_shadowing(self):
        """Test detection of simple shadowing case."""
        results = self.scenario.analyze(self.rules)

        assert len(results) == 1
        assert results[0]['shadowed_rule'] == 'allow-web-specific'
        assert results[0]['shadowing_rule'] == 'allow-web-all'

    def test_no_shadowing_detected(self):
        """Test that no shadowing is detected when none exists."""
        non_shadowed_rules = [
            SecurityRule(
                name='allow-web',
                source='192.168.1.0/24',
                destination='10.0.0.0/8',
                ports=['80']
            ),
            SecurityRule(
                name='allow-ssh',
                source='192.168.1.0/24',
                destination='10.0.0.0/8',
                ports=['22']
            )
        ]

        results = self.scenario.analyze(non_shadowed_rules)
        assert len(results) == 0

    @pytest.mark.parametrize("algorithm", ["overlap", "subnet", "port"])
    def test_different_algorithms(self, algorithm):
        """Test different shadowing detection algorithms."""
        scenario = ShadowingScenario(config={'algorithm': algorithm})
        results = scenario.analyze(self.rules)

        # All algorithms should detect the same basic shadowing
        assert len(results) >= 1
```

### Test Data and Fixtures

Create reusable test data using pytest fixtures:

```python
# conftest.py
import pytest
from policy_inspector.model import SecurityRule

@pytest.fixture
def sample_rules():
    """Provide sample security rules for testing."""
    return [
        SecurityRule(
            name='allow-web-all',
            source='any',
            destination='any',
            ports=['80', '443'],
            action='allow',
            enabled=True
        ),
        SecurityRule(
            name='deny-all',
            source='any',
            destination='any',
            ports=['any'],
            action='deny',
            enabled=True
        )
    ]

@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        'panorama': {
            'host': 'test-panorama.local',
            'username': 'testuser',
            'password': 'testpass'
        },
        'device_groups': ['test-group']
    }
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_scenario.py

# Run with coverage
poetry run pytest --cov=policy_inspector

# Run with verbose output
poetry run pytest -v

# Run only unit tests (exclude integration tests)
poetry run pytest -m "not integration"
```

## Making Contributions

### Workflow

1. **Create a feature branch:**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**

    - Write code following the style guidelines
    - Add tests for new functionality
    - Update documentation as needed

3. **Run quality checks:**

```bash
# Run tests
poetry run pytest

# Run linting
poetry run ruff check

# Run formatting
poetry run ruff format

# Run type checking
poetry run mypy policy_inspector/
```

4. **Commit your changes:**

```bash
git add .
git commit -m "feat: add new shadowing detection algorithm"
```

5. **Push and create a pull request:**

```bash
git push origin feature/your-feature-name
```

### Commit Message Format

Use conventional commit messages:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

Examples:

```
feat: add subnet-based shadowing detection
fix: handle IPv6 addresses in resolver
docs: update installation instructions
test: add integration tests for CLI
```

### Pull Request Guidelines

- Provide a clear description of the changes
- Include tests for new functionality
- Update documentation if needed
- Ensure all CI checks pass
- Reference related issues if applicable

## Adding New Features

### Creating New Scenarios

To add a new analysis scenario:

1. **Create the scenario class:**

```python
# policy_inspector/scenarios/custom.py
from typing import List, Dict, Any
from policy_inspector.scenario import BaseScenario
from policy_inspector.model import SecurityRule

class CustomScenario(BaseScenario):
    """Custom analysis scenario."""

    name = "custom"
    description = "Custom security analysis"
    version = "1.0.0"

    def analyze(self, rules: List[SecurityRule]) -> List[Dict[str, Any]]:
        """Perform custom analysis on security rules."""
        results = []

        for rule in rules:
            # Your analysis logic here
            if self.has_issue(rule):
                results.append({
                    'rule': rule.name,
                    'issue': 'custom_issue',
                    'severity': 'medium',
                    'description': 'Custom issue description'
                })

        return results

    def has_issue(self, rule: SecurityRule) -> bool:
        """Check if rule has a custom issue."""
        # Implement your logic here
        return False
```

2. **Register the scenario:**

```python
# policy_inspector/scenarios/__init__.py
from .custom import CustomScenario

SCENARIOS = {
    'custom': CustomScenario,
    # ... other scenarios
}
```

3. **Add tests:**

```python
# tests/test_scenarios/test_custom.py
import pytest
from policy_inspector.scenarios.custom import CustomScenario

class TestCustomScenario:
    def test_custom_analysis(self):
        # Test your scenario
        pass
```

### Adding New Model Types

To add new data model types:

1. **Create the model class:**

```python
# policy_inspector/model/new_object.py
from typing import List, Optional
from pydantic import BaseModel, Field

class NewObject(BaseModel):
    """Represents a new object type."""

    name: str = Field(..., description="Object name")
    type: str = Field(..., description="Object type")
    properties: Optional[List[str]] = Field(default=None, description="Object properties")

    class Config:
        """Pydantic configuration."""
        extra = "forbid"
        validate_assignment = True
```

2. **Add to model exports:**

```python
# policy_inspector/model/__init__.py
from .new_object import NewObject

__all__ = ['NewObject', ...]
```

3. **Add tests:**

```python
# tests/test_model/test_new_object.py
import pytest
from policy_inspector.model import NewObject

class TestNewObject:
    def test_create_new_object(self):
        obj = NewObject(name="test", type="example")
        assert obj.name == "test"
        assert obj.type == "example"
```

## Documentation

### Building Documentation

```bash
# Install documentation dependencies
poetry install --extras docs

# Build HTML documentation
cd docs
make html

# View documentation
open build/html/index.html
```

### Writing Documentation

- Use MyST Markdown for all documentation
- Include code examples where relevant
- Update API documentation when adding new modules
- Add usage examples for new features

## Release Process

### Versioning

We use semantic versioning (SemVer):

- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

### Creating a Release

1. **Update version:**

```bash
# Update version in pyproject.toml
poetry version patch  # or minor, major
```

2. **Update changelog:**

```markdown
# CHANGELOG.md

## [0.2.2] - 2025-07-12

### Added

- New shadowing detection algorithm

### Fixed

- Handle IPv6 addresses correctly

### Changed

- Improved performance for large rule sets
```

3. **Create release:**

```bash
git add .
git commit -m "chore: bump version to 0.2.2"
git tag v0.2.2
git push origin main --tags
```

## Getting Help

- **Issues**: Report bugs and request features on GitHub Issues
- **Discussions**: Ask questions on GitHub Discussions
- **Code Review**: All pull requests receive code review
- **Documentation**: Check the documentation for detailed guides

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and contribute
- Follow the code of conduct

Thank you for contributing to Policy Inspector!
