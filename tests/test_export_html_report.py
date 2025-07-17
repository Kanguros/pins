# import tempfile
# from pathlib import Path

# import pytest

# from policy_inspector.model.security_rule import SecurityRule
# from policy_inspector.scenarios.shadowing.advanced import AdvancedShadowing
# from policy_inspector.scenarios.shadowing.exporter import export_as_html
# from policy_inspector.scenarios.shadowing.simple import Shadowing


# class DummyPanorama:
#     def get_security_rules(self, device_group, rulebase):
#         return []


# def make_scenario(scenario_cls):
#     panorama = DummyPanorama()
#     scenario = scenario_cls(panorama=panorama, device_groups=["dg1"])
#     # Minimal required attributes for export
#     scenario.security_rules_by_dg = {
#         "dg1": [SecurityRule(name="rule1", action="allow")]
#     }  # type: ignore
#     scenario.address_groups = []
#     scenario.address_objects = []
#     scenario.device_groups = ["dg1"]
#     scenario.analysis_results_by_dg = {
#         "dg1": [(scenario.security_rules_by_dg["dg1"][0], [])]
#     }
#     return scenario


# @pytest.mark.skip(
#     reason="This test generates a large HTML report for manual inspection"
# )
# def test_export_as_html_big_report():
#     """
#     Generate a big HTML report with many device groups, rules, findings, address groups/objects.
#     Save it to the current directory for manual inspection.
#     """

#     class BigPanorama:
#         def get_security_rules(self, device_group, rulebase):
#             return []

#     from policy_inspector.model.security_rule import SecurityRule
#     from policy_inspector.scenarios.shadowing.simple import Shadowing

#     num_rules_per_dg = 6

#     device_groups = ["Branch_1_FW", "Branch_2_FW", "HQ_FW"]
#     address_groups = ["AG_Internal", "AG_DMZ", "AG_Guest"]
#     address_objects = [
#         "AO_WebSrv",
#         "AO_DB",
#         "AO_AppSrv",
#         "AO_AdminPC",
#         "AO_GuestPC",
#         "AO_VPNUser",
#     ]

#     # Realistic rules
#     rules_data = [
#         {
#             "name": "Allow_Trust_to_DMZ",
#             "action": "allow",
#             "source_zones": {"Trust"},
#             "destination_zones": {"DMZ"},
#             "source_addresses": {"CorpNet"},
#             "destination_addresses": {"Web-Servers"},
#             "applications": {"web-browsing"},
#             "services": {"tcp-80", "tcp-443"},
#         },
#         {
#             "name": "Deny_Guest_to_Internal",
#             "action": "deny",
#             "source_zones": {"Guest"},
#             "destination_zones": {"Internal"},
#             "source_addresses": {"Guest-WiFi"},
#             "destination_addresses": {"App-Servers"},
#             "applications": {"sql"},
#             "services": {"tcp-1433"},
#         },
#         {
#             "name": "Allow_VPN_to_Internal",
#             "action": "allow",
#             "source_zones": {"VPN"},
#             "destination_zones": {"Internal"},
#             "source_addresses": {"VPN-Users"},
#             "destination_addresses": {"DB-Servers"},
#             "applications": {"ssh"},
#             "services": {"tcp-22"},
#         },
#         {
#             "name": "Allow_Admin_to_Firewall",
#             "action": "allow",
#             "source_zones": {"Trust"},
#             "destination_zones": {"Untrust"},
#             "source_addresses": {"AdminPC"},
#             "destination_addresses": {"Firewall"},
#             "applications": {"ssh"},
#             "services": {"tcp-22"},
#         },
#         {
#             "name": "Allow_Monitoring_to_Servers",
#             "action": "allow",
#             "source_zones": {"Trust"},
#             "destination_zones": {"DMZ", "Internal"},
#             "source_addresses": {"Monitoring"},
#             "destination_addresses": {"Web-Servers", "DB-Servers"},
#             "applications": {"dns"},
#             "services": {"udp-53"},
#         },
#         {
#             "name": "Deny_All",
#             "action": "deny",
#             "source_zones": {"any"},
#             "destination_zones": {"any"},
#             "source_addresses": {"any"},
#             "destination_addresses": {"any"},
#             "applications": {"any"},
#             "services": {"any"},
#         },
#     ]

#     security_rules_by_dg = {}
#     analysis_results_by_dg = {}
#     for dg in device_groups:
#         rules = []
#         for j in range(num_rules_per_dg):
#             rule_info = rules_data[j % len(rules_data)]
#             rule = SecurityRule(
#                 name=f"{rule_info['name']}_{dg}_{j + 1}",
#                 action=rule_info["action"],
#                 source_zones=rule_info["source_zones"],
#                 destination_zones=rule_info["destination_zones"],
#                 source_addresses=rule_info["source_addresses"],
#                 destination_addresses=rule_info["destination_addresses"],
#                 applications=rule_info["applications"],
#                 services=rule_info["services"],
#             )
#             rules.append(rule)
#         security_rules_by_dg[dg] = rules
#         findings = []
#         for idx in range(1, len(rules)):
#             rule = rules[idx]
#             preceding = rules[max(0, idx - 3) : idx]
#             findings.append((rule, preceding))
#         analysis_results_by_dg[dg] = findings

#     scenario = Shadowing(panorama=BigPanorama(), device_groups=device_groups)
#     scenario.security_rules_by_dg = security_rules_by_dg  # type: ignore
#     scenario.address_groups = address_groups
#     scenario.address_objects = address_objects
#     scenario.device_groups = device_groups
#     scenario.analysis_results_by_dg = analysis_results_by_dg

#     html = export_as_html(scenario)
#     out_path = Path(__file__).parent / "big_report.html"
#     out_path.write_text(f"{html}\n", encoding="utf-8")
#     assert out_path.exists()
#     # Optionally check some expected content
#     assert "Firewall Policy Analysis Report" in html
