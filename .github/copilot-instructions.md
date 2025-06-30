---
applyTo: "**"
---

# Project Overview

## Coding Standards

- Use Black-compatible formatting (see Ruff config for line length and exclusions).
- All public functions and classes should have type annotations.
- Use snake_case for variable and function names.

## Development Workflow

- Use `poetry` for dependency management and virtual environment.
- Run `pytest`, all tests must pass.
- Use `pre-commit`.
- Do not hardcode credentials; use environment variables or config files for secrets.

## File Structure

- `policy_inspector/`: Core library code.
- `tests/`: Unit and integration tests.

## Key Guidelines

- Write docstrings for all public functions and classes.
- Prefer context managers for resource handling.
- Avoid hardcoding sensitive data.
- Keep each instruction and code change focused and atomic.

## Tools and Dependencies

- Python 3.10+
- Pydantic v2 for data models
- Ruff for linting and formatting
- Pytest for testing
- Pre-commit for enforcing code quality

## Testing

- Place all tests in the `tests/` directory.
- Use pytest fixtures for reusable test setup.
- All new features must include corresponding tests.

## Miscellaneous

- Organize code with clear separation between core logic, examples, scripts, and tests.
- Store this file in version control and update as standards change.
