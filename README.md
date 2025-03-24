> [!CAUTION]
> Package is under active development. Things might and will change.

![logo.png](logo.png)

# Policy Inspector

Analysis of a firewall security policies.

## What _Policy Inspector_ really is?

It is a CLI tool to analyze firewall security policies against a
predefined scenarios.

It started as a tool to detect shadowing firewall rules. It evolved
into a small framework that allows to define different scenario very
easily.

## Installation

You can install using:

### pip

```shell
# pip
pip install policy_inspector

# poetry
poetry add policy_inspector

# pipx
pipx install policy_inspector

```

## Usage

Once installed, you can run it using `policyinspector` or just `pi`
command:

```shell
pi --help
```

To see an example how does it works, run:

```shell
pi run example1
```

To check your own firewall rules:

```shell
pi run shadowing policies.json
```

## Example

```shell
[1/3][rule-example1] Checking rule against 0 preceding Rules
[1/3][rule-example1] Checking rule finished.
[2/3][rule-example2] Checking rule against 1 preceding Rules
[2/3][rule-example2] Checking rule finished.
[3/3][rule3-allow-dns] Checking rule against 2 preceding Rules
[3/3][rule3-allow-dns] Checking rule finished.
Shadowed rules detection complete
[rule-example1] Rule not shadowed
[rule-example2] Rule is shadowed by: rule-example1
[rule3-allow-dns] Rule not shadowed

```

## Details

### How does it work?

It's pretty straightforward.

1. Get desire scenario.
2. Loads security policies from file.
3. Filter them to exclude unwanted policies.
4. Execute selected scenario's checks for each security policy.
5. Evaluate check's results.

```mermaid
flowchart TD
    SelectScenario[Select Scenario]
    SelectScenario --> LoadRules[Load Security Rules]
    LoadRules --> FilterRules[Filter Security Rules]
    FilterRules --> RunChecks[Run Checks for each Rule]
    RunChecks --> Analyze[Analyze Results]
    Analyze --> Report[Create Report]
```

### Scenarios

A scenario is a set of checks that evaluate firewall rules against
specific issues or configurations. Each scenario is designed to
identify particular problem.

### Checks

A _check_ is simply a function. It takes security policy or policies
as an argument, assess whether the policies fulfill a check or not.

## Contribution & Development

If you'd like to contribute, follow these steps:

```shell
git clone https://github.com/Kanguros/policy_inspector
cd policy_inspector
poetry install --with=dev
pre-commit install --install-hooks
pre-commit run --all-files
```

Feel free to open issues or submit pull requests!
