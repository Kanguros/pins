# Rules Check

It is a CLI tool to analyze _a firewall_ security policies.

Rules Checker started as a tool to detect overlapping firewall rules, known as shadowing. During development, it evolved
into a straightforward framework that allows to define different checks very easily.

## Installation

You can install _Rules Check_ using `pip`, `poetry` or `pipx`:

```sh
pip install rules_check
poetry add rules_check
pipx install rules_check
```

## Usage

Once installed, you can run it using `rulescheck` or `rc` command:

```sh
rc --help
```

To see an example how does it works, run:

```sh
rc run-example
```

To check your own firewall rules:

```sh
rc run --security-rules policies.json
```

## Example

```sh
$ rc run-example

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

```sh
git clone https://github.com/Kanguros/rules_check
cd rules_check
poetry install --with=dev
pre-commit install --install-hooks
pre-commit run --all-files
```

Feel free to open issues or submit pull requests!
