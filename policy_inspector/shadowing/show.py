import logging
from typing import TYPE_CHECKING

from rich.table import Table

if TYPE_CHECKING:
    from .base import AnalysisResults

logger = logging.getLogger(__name__)


def show_as_text(analysis_results: "AnalysisResults") -> None:
    logger.info("Analysis results")
    logger.info("----------------")
    for rule, shadowing_rules in analysis_results:
        if shadowing_rules:
            logger.info(f"✖ '{rule.name}' shadowed by:")
            for preceding_rule in shadowing_rules:
                logger.info(f"   • '{preceding_rule.name}'")
        else:
            logger.debug(f"✔ '{rule.name}' not shadowed")
    logger.info("----------------")


def show_as_table(analysis_results: "AnalysisResults") -> None:
    from rich.console import Console

    console = Console()

    for i, result in enumerate(analysis_results):
        rule, shadowing_rules = result
        if not shadowing_rules:
            continue

        table = Table(title=f"Finding {i + 1}", show_lines=True)

        main_headers = ["Attribute", "Shadowed Rule"]
        next_headers = [
            f"Preceding Rule {i}" for i in range(1, len(shadowing_rules) + 1)
        ]
        for header in main_headers + next_headers:
            table.add_column(header)

        rules = [rule] + shadowing_rules

        for attribute_name in rule.__pydantic_fields__:
            attribute_values = []
            for rule in rules:
                rule_attribute = getattr(rule, attribute_name)
                if isinstance(rule_attribute, (set, list)):
                    value = "\n".join(f"- {str(v)}" for v in rule_attribute)
                else:
                    value = str(rule_attribute)
                attribute_values.append(value)
            table.add_row(attribute_name, *attribute_values)

        console.print(table)
