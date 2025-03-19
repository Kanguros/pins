> [!CAUTION]
> Package is under active development. Things might and will change.

# Policy Inspector

Analysis of a firewall security policies.

## What _Policy Inspector_ really is?

It is a CLI tool which main purpose is to analyze firewall security policies against a predefined checks.

It started as a tool to detect shadowing firewall rules. During development, it evolved
into a small framework that allows to define different checks very easily.

## How does it work?

It's pretty straightforward.

1. Loads security policies from file.
2. Filter them to exclude unwanted policies.
3. Execute selected list of checks for each security policy.
4. Gather outputs from each check for all security policy.

## What _checks_ are?

A _check_ is simply a function. It takes security policy or policies as an argument, assess whether the policies fulfill a check or not.

## Installation

You can install using:

```shell
pip install policy_inspector
```

```shell
poetry add policy_inspector
```

```shell
pipx install policy_inspector
```

## Usage

Once installed, you can run it using `policyinspector` or just `pi` command:

```shell
pi --help
```

To see an example how does it works, run:

```shell
pi run-example
```

To check your own firewall rules:

```shell
pi run --security-rules policies.json
```

## Example

```shell
$ pi run-example

INFO     Running an example
INFO     Starting shadowed Rules detection
INFO     Number of Rules to check: 3
INFO     Number of Checks: 7
INFO     Finished shadowed Rules detection. Analyzing results
INFO     [1/3][rule-example1] Checking rule against 0 preceding Rules
INFO     [1/3][rule-example1] Checking rule finished.
INFO     [2/3][rule-example2] Checking rule against 1 preceding Rules
INFO     [2/3][rule-example2] Checking rule finished.
INFO     [3/3][rule3-allow-dns] Checking rule against 2 preceding Rules
INFO     [3/3][rule3-allow-dns] Checking rule finished.
INFO     Shadowed rules detection complete
INFO     [rule-example2] Rule is shadowed by: rule-example1
INFO     [rule3-allow-dns] Rule not shadowed
INFO     [rule3-allow-dns] Rule not shadowed
{
    'rule-example1': {},
    'rule-example2': {
        'rule-example1': {
            'check_action': (True, 'Actions match'),
            'check_application': (True, "Preceding rule contains rule's applications"),
            'check_services': (True, "Preceding rule and rule's services are the same"),
            'check_source_zone': (True, 'Source zones are the same'),
            'check_destination_zone': (True, 'Source zones are the same'),
            'check_source_address': (True, 'Preceding rule allows any source address'),
            'check_destination_address': (True, 'Preceding rule allows any destination address')
        }
    },
    'rule3-allow-dns': {
        'rule-example1': {
            'check_action': (True, 'Actions match'),
            'check_application': (False, "Preceding rule does not contain all rule's applications"),
            'check_services': (True, "Preceding rule and rule's services are the same"),
            'check_source_zone': (False, 'Source zones differ'),
            'check_destination_zone': (True, 'Source zones are the same'),
            'check_source_address': (True, 'Preceding rule allows any source address'),
            'check_destination_address': (True, 'Preceding rule allows any destination address')
        },
        'rule-example2': {
            'check_action': (True, 'Actions match'),
            'check_application': (False, "Preceding rule does not contain all rule's applications"),
            'check_services': (True, "Preceding rule and rule's services are the same"),
            'check_source_zone': (False, 'Source zones differ'),
            'check_destination_zone': (True, 'Source zones are the same'),
            'check_source_address': (False, 'Source addresses not covered at all'),
            'check_destination_address': (False, 'Destination addresses not covered at all')
        }
    }
}


```

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
