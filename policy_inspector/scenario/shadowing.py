import logging
from typing import TYPE_CHECKING, Callable, Literal, Optional

from rich.table import Table

from policy_inspector.model.base import AnyObj
from policy_inspector.scenario.base import CheckResult, Scenario

if TYPE_CHECKING:
    from policy_inspector.model.security_rule import SecurityRule

logger = logging.getLogger(__name__)

ShadowingCheckFunction = Callable[["SecurityRule", "SecurityRule"], CheckResult]


def check_action(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """
    Checks if both rules have the same action (like 'allow' or 'deny').
    If the actions are different, the first rule does not fully hide the second one.
    """
    result = rule.action == preceding_rule.action
    message = "Actions match" if result else "Actions differ"
    return result, message


def check_source_zone(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """
    Checks if the first rule covers all the same source zones as the second rule.
    If the first rule uses 'any' or all the same zones, it can hide the second rule.
    """
    if rule.source_zones == preceding_rule.source_zones:
        return True, "Source zones are the same"

    if preceding_rule.source_zones.issubset(rule.source_zones):
        return True, "Preceding rule source zones cover rule's source zones"

    if AnyObj in preceding_rule.source_zones:
        return True, "Preceding rule source zones is 'any'"

    return False, "Source zones differ"


def check_destination_zone(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """
    Checks if the first rule covers all the same destination zones as the second rule.
    If the first rule uses 'any' or all the same zones, it can hide the second rule.
    """
    if rule.destination_zones == preceding_rule.destination_zones:
        return True, "Destination zones are the same"

    if rule.destination_zones.issubset(preceding_rule.destination_zones):
        return (
            True,
            "Preceding rule destination zones cover rule's destination zones",
        )

    if AnyObj in preceding_rule.destination_zones:
        return True, "Preceding rule destination zones is 'any'"

    return False, "Destination zones differ"


def check_source_address(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """
    Checks if the first rule covers all the same source addresses (like IPs or groups).
    If the first rule uses 'any' or all the same addresses, it can hide the second rule.
    """
    if rule.source_addresses == preceding_rule.source_addresses:
        return True, "Source addresses are the same"

    if AnyObj in preceding_rule.source_addresses:
        return True, "Preceding rule allows any source address"

    if AnyObj in rule.source_addresses:
        return False, "Rule not covered due to 'any' source"

    if rule.source_addresses.issubset(preceding_rule.source_addresses):
        return (
            True,
            "Preceding rule source addresses cover rule's source addresses",
        )

    return False, "Source addresses not covered at all"


def check_destination_address(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """
    Checks if the first rule covers all the same destination addresses.
    If the first rule uses 'any' or all the same addresses, it can hide the second rule.
    """
    if AnyObj in preceding_rule.destination_addresses:
        return True, "Preceding rule allows any destination address"

    if rule.destination_addresses == preceding_rule.destination_addresses:
        return True, "Destination addresses are the same"

    if rule.destination_addresses.issubset(
        preceding_rule.destination_addresses,
    ):
        return (
            True,
            "Preceding rule destination addresses cover rule's destination addresses",
        )

    return False, "Destination addresses not covered at all"


def check_application(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """
    Checks if the first rule allows all the same applications as the second rule.
    If the first rule uses 'any' or all the same apps, it can hide the second rule.
    """
    rule_apps = rule.applications
    preceding_apps = preceding_rule.applications

    if rule_apps == preceding_apps:
        return True, "The same applications"

    if AnyObj in preceding_apps:
        return True, "Preceding rule allows any application"

    if rule_apps.issubset(preceding_apps):
        return True, "Preceding rule contains rule's applications"

    return False, "Rule doesn't cover"


def check_services(
    rule: "SecurityRule",
    preceding_rule: "SecurityRule",
) -> CheckResult:
    """
    Checks if the first rule allows all the same network services or ports.
    If the first rule covers all the same services, it can hide the second rule.
    """
    if rule.services == preceding_rule.services:
        return True, "Preceding rule and rule's services are the same"

    if all(service in preceding_rule.services for service in rule.services):
        return True, "Preceding rule contains rule's applications"

    return False, "Preceding rule does not contain all rule's applications"


ChecksOutputs = dict[str, CheckResult]
"""Dict with check's name as keys and its output as value."""

PrecedingRulesOutputs = dict[str, ChecksOutputs]
"""Dict with Preceding Rule's name as keys and ChecksOutputs as its value."""

ExecuteResults = dict[str, PrecedingRulesOutputs]
"""Dict with Rule's name as keys and ``PrecedingRulesOutputs`` as value."""

AnalysisResults = list[tuple["SecurityRule", list["SecurityRule"]]]
"""List of two-element tuples where first element is a ``SecurityRule`` and second element is list of shadowing rules"""


class Shadowing(Scenario):
    """
    This scenario identifies when a rule is completely shadowed by a preceding rule.

    Shadowing occurs when a rule will never be matched
    because a rule earlier in the processing order would always match first.
    """

    name: str = "Shadowing"
    checks: list[ShadowingCheckFunction] = [
        check_action,
        check_application,
        check_services,
        check_source_zone,
        check_destination_zone,
        check_source_address,
        check_destination_address,
    ]

    def __init__(self, security_rules: list["SecurityRule"]):
        self.security_rules = security_rules
        self.rules_by_name = {rule.name: rule for rule in self.security_rules}
        self.execution_results: Optional[ExecuteResults] = None
        self.analysis_results: Optional[AnalysisResults] = None

    def execute(self) -> ExecuteResults:
        rules = self.security_rules
        results = {}
        for i, rule in enumerate(rules):
            output = {}
            for j in range(i):
                preceding_rule = rules[j]
                output[preceding_rule.name] = self.run_checks(
                    rule,
                    preceding_rule,
                )
            results[rule.name] = output
        self.execution_results = results
        return results

    def analyze(
        self,
        results: ExecuteResults,
    ) -> AnalysisResults:
        analysis_results = []
        for rule_name, rule_results in results.items():
            shadowing_rules = []
            for preceding_rule_name, checks_results in rule_results.items():
                if all(
                    check_result[0] for check_result in checks_results.values()
                ):
                    shadowing_rules.append(
                        self.rules_by_name[preceding_rule_name]
                    )
            if shadowing_rules:
                analysis_results.append(
                    (self.rules_by_name[rule_name], shadowing_rules)
                )
        self.analysis_results = analysis_results
        return analysis_results

    def show(
        self,
        analysis_results: AnalysisResults,
        *formats: Literal["text", "table"],
    ):
        if not formats:
            logger.debug("No show format was provided.")
            return
        formats_map = {
            "text": self.show_as_text,
            "table": self.show_as_table,
        }
        for format_ in formats:
            format_func = formats_map.get(format_)
            if not format_func:
                logger.error(f"Show format '{format_}' unknown!")
                continue
            format_func(analysis_results)

    @staticmethod
    def show_as_text(analysis_results: AnalysisResults):
        root_logger = logging.getLogger()
        root_logger.info("Analysis results")
        root_logger.info("----------------")
        for rule, shadowing_rules in analysis_results:
            if shadowing_rules:
                root_logger.info(f"✖ '{rule.name}' shadowed by:")
                for preceding_rule in shadowing_rules:
                    root_logger.info(f"   • '{preceding_rule.name}'")
            else:
                root_logger.debug(f"✔ '{rule.name}' not shadowed")
        root_logger.info("----------------")

    @staticmethod
    def show_as_table(analysis_results: AnalysisResults):
        from rich.console import Console

        console = Console()

        for i, result in enumerate(analysis_results):
            rule, shadowing_rules = result
            if not shadowing_rules:
                continue

            table = Table(title=f"Finding {i + 1}", show_lines=True)

            main_headers = ["Attribute", "Shadowed Rule"]
            next_headers = [
                f"Preceding Rule {i}"
                for i in range(1, len(shadowing_rules) + 1)
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
