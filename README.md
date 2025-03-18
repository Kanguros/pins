# Rules Check

It is a CLI tool to analyze _a firewall_ security policies.

Rules Checker started as a tool to detect overlapping firewall rules, known as shadowing. During development, it evolved
into a straightforward framework that allows to define different checks very easily.

## Installation

You can install _Rules Check_ using `pip`, `poetry` or `pipx`:

```sh
pip install rules_checker
```

or with Poetry:

```sh
poetry add rules_checker
```

## Usage

Once installed, you can run it using `rulescheck` or `rc` command:

```sh
rc <options>
```

For example, to check firewall rules from a configuration file:

```sh
rc check my_firewall_config.json
```

## Configuration

Rules Checker allows defining custom validation rules using a simple configuration format. Users can specify different
checks, such as:

- Detecting shadowed rules.
- Ensuring a specific deny rule blocks all preceding traffic.
- Validating that rules follow best practices for security and performance.

## Contribution & Development

If you'd like to contribute, follow these steps:

1. Clone the repository.
2. Install dependencies using `poetry install`.
3. Use `pre-commit` for linting, testing, and validation.

To run tests and ensure code quality:

```sh
git clone https://github.com/Kanguros/rules_check
cd rules_check
poetry install --with=dev
pre-commit install --install-hooks
pre-commit run --all-files
```

Feel free to open issues or submit pull requests!
