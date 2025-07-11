import tempfile
from pathlib import Path

from policy_inspector.model.security_rule import SecurityRule
from policy_inspector.scenarios.shadowing.advanced import AdvancedShadowing
from policy_inspector.scenarios.shadowing.export import export_as_html
from policy_inspector.scenarios.shadowing.simple import Shadowing


class DummyPanorama:
    def get_security_rules(self, device_group, rulebase):
        return []


def make_scenario(scenario_cls):
    panorama = DummyPanorama()
    scenario = scenario_cls(panorama=panorama, device_groups=["dg1"])
    # Minimal required attributes for export
    scenario.security_rules_by_dg = {
        "dg1": [SecurityRule(name="rule1", action="allow")]
    }  # type: ignore
    scenario.address_groups = []
    scenario.address_objects = []
    scenario.device_groups = ["dg1"]
    scenario.analysis_results_by_dg = {
        "dg1": [(scenario.security_rules_by_dg["dg1"][0], [])]
    }
    return scenario


def test_export_as_html_creates_file_and_content():
    scenario = make_scenario(Shadowing)
    html = export_as_html(scenario)
    assert "<html" in html.lower()
    assert "Firewall Policy Analysis Report" in html
    # Save to temp file
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "report.html"
        out_path.write_text(html, encoding="utf-8")
        assert out_path.exists()
        content = out_path.read_text(encoding="utf-8")
        assert "Firewall Policy Analysis Report" in content


def test_export_as_html_advanced():
    scenario = make_scenario(AdvancedShadowing)
    html = export_as_html(scenario)
    assert "<html" in html.lower()
    assert "Firewall Policy Analysis Report" in html
