#!/usr/bin/env python3
"""Test script to debug the example issue."""

from pathlib import Path
from policy_inspector.mock_panorama import MockPanoramaConnector
from policy_inspector.scenarios.shadowing.simple import Shadowing

def test_scenario():
    print("Testing scenario creation...")
    
    # Create mock connector
    data_dir = Path("policy_inspector/example/1")
    mock = MockPanoramaConnector(data_dir, "Example 1")
    print("✓ Mock connector created")
    
    # Create scenario
    scenario = Shadowing(panorama=mock, device_groups=["Example 1"])
    print("✓ Scenario created")
    print(f"Device groups: {scenario.device_groups}")
    print(f"Security rules by DG: {list(scenario.security_rules_by_dg.keys())}")
    
    # Check the checks list
    print(f"Number of checks: {len(scenario.checks)}")
    for i, check in enumerate(scenario.checks):
        print(f"Check {i}: {check} (type: {type(check)})")
        if not callable(check):
            print(f"  ❌ Check {i} is not callable!")
    
    # Try to execute and analyze
    print("Running execute_and_analyze...")
    try:
        scenario.execute_and_analyze()
        print("✓ Execute and analyze completed")
    except Exception as e:
        print(f"❌ Error during execution: {e}")

if __name__ == "__main__":
    test_scenario()
