"""
Enhanced shadowing scenario using the new architecture.

This is an example of how to create scenarios using the new enhanced
scenario architecture with separate exporter and displayer classes.
"""

import logging
from typing import TYPE_CHECKING

import rich_click as click

from policy_inspector.scenario import Scenario
from policy_inspector.scenarios.shadowing.checks import (
    check_action,
    check_application,
    check_destination_address,
    check_destination_zone,
    check_services,
    check_source_address,
    check_source_zone,
)

if TYPE_CHECKING:
    from policy_inspector.panorama import PanoramaConnector

logger = logging.getLogger(__name__)


class EnhancedShadowingScenario(Scenario):
    """
    Enhanced shadowing detection scenario.
    
    Detects firewall rules that are shadowed by preceding rules with broader conditions.
    This enhanced version uses the new architecture with better export and display capabilities.
    """

    name = "Enhanced Shadowing Detection"

    def __init__(self, panorama: "PanoramaConnector", **kwargs):
        """
        Initialize the enhanced shadowing scenario.

        Args:
            panorama: PanoramaConnector instance
            **kwargs: Additional arguments including device_groups, exclude_checks, etc.
        """
        super().__init__(panorama, **kwargs)
        
        # Scenario-specific attributes
        self.device_groups = kwargs.get('device_groups', [])
        self.exclude_checks = kwargs.get('exclude_checks', [])
        self.include_disabled = kwargs.get('include_disabled', False)
        
        # Define the checks to run
        self.checks = [
            check_source_zone,
            check_destination_zone,
            check_source_address,
            check_destination_address,
            check_services,
            check_application,
            check_action,
        ]
        
        # Filter out excluded checks
        if self.exclude_checks:
            self.checks = [
                check for check in self.checks
                if not any(keyword in check.__name__ for keyword in self.exclude_checks)
            ]

    @classmethod
    def get_cli_options(cls) -> list[click.Option]:
        """
        Get CLI options specific to the shadowing scenario.
        
        Returns:
            List of Click option decorators
        """
        return [
            click.option(
                '--device-groups',
                multiple=True,
                help='Device groups to analyze (can be specified multiple times)'
            ),
            click.option(
                '--exclude-checks',
                multiple=True,
                help='Keywords to exclude checks (e.g., "zone", "address")'
            ),
            click.option(
                '--include-disabled',
                is_flag=True,
                help='Include disabled rules in analysis'
            ),
        ]

    def execute(self) -> dict[str, dict[str, dict[str, dict]]]:
        """
        Execute the shadowing detection scenario.

        Returns:
            Dictionary with analysis results for each rule and device group
        """
        logger.info("Executing enhanced shadowing detection...")
        
        if not self.device_groups:
            logger.warning("No device groups specified for analysis")
            return {}

        results = {}
        
        for device_group in self.device_groups:
            logger.info(f"Analyzing device group: {device_group}")
            
            # Get security rules from Panorama
            security_rules = self.panorama.get_security_rules(
                device_group=device_group,
                include_disabled=self.include_disabled
            )
            
            if not security_rules:
                logger.warning(f"No security rules found in device group: {device_group}")
                continue
            
            # Analyze each rule for shadowing
            device_group_results = {}
            
            for rule_index, rule in enumerate(security_rules):
                rule_name = rule.name
                logger.debug(f"Analyzing rule {rule_index + 1}/{len(security_rules)}: {rule_name}")
                
                # Check against all preceding rules
                preceding_rules = security_rules[:rule_index]
                rule_results = {}
                
                for preceding_rule in preceding_rules:
                    preceding_rule_name = preceding_rule.name
                    check_results = {}
                    
                    # Run all checks against the preceding rule
                    for check in self.checks:
                        try:
                            result = check(rule, preceding_rule)
                            check_results[check.__name__] = {
                                'result': result.result,
                                'message': result.message,
                                'details': result.details
                            }
                        except Exception as e:
                            logger.error(f"Check {check.__name__} failed for rule {rule_name}: {e}")
                            check_results[check.__name__] = {
                                'result': False,
                                'message': f"Check failed: {e}",
                                'details': {}
                            }
                    
                    rule_results[preceding_rule_name] = check_results
                
                device_group_results[rule_name] = rule_results
            
            results[device_group] = device_group_results
        
        logger.info("Enhanced shadowing detection completed")
        return results

    def analyze(self, results: dict[str, dict[str, dict[str, dict]]]) -> list[dict]:
        """
        Analyze the execution results to identify shadowed rules.

        Args:
            results: Raw execution results

        Returns:
            List of analysis results with shadowed rules information
        """
        logger.info("Analyzing shadowing results...")
        
        analysis_results = []
        
        for device_group, device_group_results in results.items():
            for rule_name, rule_results in device_group_results.items():
                shadowing_rules = []
                
                for preceding_rule_name, check_results in rule_results.items():
                    # Check if all checks passed (indicating shadowing)
                    all_checks_passed = all(
                        check_result['result'] for check_result in check_results.values()
                    )
                    
                    if all_checks_passed:
                        shadowing_rules.append({
                            'name': preceding_rule_name,
                            'checks': check_results
                        })
                
                if shadowing_rules:
                    analysis_results.append({
                        'device_group': device_group,
                        'shadowed_rule': rule_name,
                        'shadowing_rules': shadowing_rules,
                        'shadowing_count': len(shadowing_rules)
                    })
        
        logger.info(f"Found {len(analysis_results)} shadowed rules")
        return analysis_results

    def get_data_for_display(self) -> dict:
        """
        Prepare data for display in a user-friendly format.
        
        Returns:
            Dictionary with display-ready data
        """
        if self._analysis is None:
            return {}
        
        # Create a summary for display
        summary = {
            'total_shadowed_rules': len(self._analysis),
            'shadowed_rules': []
        }
        
        for result in self._analysis:
            rule_info = {
                'device_group': result['device_group'],
                'rule_name': result['shadowed_rule'],
                'shadowing_count': result['shadowing_count'],
                'shadowing_rules': [sr['name'] for sr in result['shadowing_rules']]
            }
            summary['shadowed_rules'].append(rule_info)
        
        return summary

    def get_data_for_export(self) -> dict:
        """
        Prepare data for export with full details.
        
        Returns:
            Dictionary with export-ready data including full analysis
        """
        if self._analysis is None:
            return {}
        
        export_data = {
            'scenario': 'enhanced_shadowing',
            'timestamp': self._get_timestamp(),
            'configuration': {
                'device_groups': self.device_groups,
                'exclude_checks': self.exclude_checks,
                'include_disabled': self.include_disabled,
                'checks_used': [check.__name__ for check in self.checks]
            },
            'summary': {
                'total_shadowed_rules': len(self._analysis),
                'device_groups_analyzed': len({r['device_group'] for r in self._analysis})
            },
            'results': self._analysis
        }

        return export_data

    def _get_timestamp(self) -> str:
        """Get current timestamp for export metadata."""
        from datetime import datetime, timezone
        return datetime.now(tz=timezone.utc).isoformat()

    def get_description(self) -> str:
        """Get scenario description."""
        return "Detect firewall rules shadowed by preceding broader rules"

    def get_help_text(self) -> str:
        """Get detailed help text."""
        return """
        Enhanced Shadowing Detection Scenario
        
        This scenario analyzes firewall security rules to identify rules that are
        "shadowed" by preceding rules with broader conditions. A shadowed rule
        will never be triggered because traffic matching it will always match
        a preceding rule first.
        
        The analysis includes checks for:
        - Source zones and addresses
        - Destination zones and addresses  
        - Services and applications
        - Rule actions
        
        Use --exclude-checks to skip specific check types if needed.
        
        Examples:
          pins run enhanced_shadowing --device-groups "Production" --show table
          pins run enhanced_shadowing --device-groups "Prod" "Test" --export json yaml
          pins run enhanced_shadowing --exclude-checks zone --include-disabled
        """
