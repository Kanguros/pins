from typing import TYPE_CHECKING

from rich.table import Table

if TYPE_CHECKING:
    from policy_inspector.model.security_rule import SecurityRule


def display_rules(*rules: "SecurityRule", title: str = "Rules"):
    table = Table(title=title)

    main_headers = ("Attribute", "Security Rule")
    next_headers = [f"Preceding Rule {i}" for i in range(len(rules) - 1)]
    map(table.add_column, main_headers, next_headers)

    for attribute in SecurityRule.model_fields.keys():
        rules_attribute = [getattr(rule, attribute) for rule in rules]
        table.add_row(attribute, *rules_attribute)

    print(table)
