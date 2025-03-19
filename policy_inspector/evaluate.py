import logging

from policy_inspector.check import RulesChecksResults

logger = logging.getLogger(__name__)


def analyze_checks_results(
    results: RulesChecksResults,
):
    for rule_name, rule_results in results.items():
        for preceding_rule_name, checks_results in rule_results.items():
            shadowing = True
            for _check_name, check_result in checks_results.items():
                if not check_result[0]:
                    shadowing = False
            if shadowing:
                logger.info(
                    f"[{rule_name}] Rule is shadowed by: {preceding_rule_name}"
                )

            else:
                logger.info(f"[{rule_name}] Rule not shadowed")
