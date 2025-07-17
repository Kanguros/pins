from datetime import datetime, timezone
from pathlib import Path

from policy_inspector.output.exporter import Exporter
from policy_inspector.utils import load_jinja_template


class ShadowingExporter(Exporter):
    def export_html(
        self, scenario, *args, output_path: str = None, **kwargs
    ) -> str:
        """
        Render the HTML report using a Jinja2 template (report_template.html).
        If output_path is provided, save the HTML to that file.
        """
        template_dir = Path(__file__).parent
        template = load_jinja_template(template_dir, "report_template.html")
        current_date = datetime.now(tz=timezone.utc).strftime(
            "%B %d, %Y %H:%M:%S"
        )

        # Calculate total policies correctly
        total_policies = sum(
            len(rules) for rules in scenario.security_rules_by_dg.values()
        )

        html = template.render(
            scenario=scenario,
            scenario_doc=getattr(scenario, "__doc__", None),
            address_groups_count=len(getattr(scenario, "address_groups", [])),
            address_objects_count=len(getattr(scenario, "address_objects", [])),
            total_policies=total_policies,
            current_date=current_date,
        )

        if output_path:
            out_path = Path(output_path)
            out_path.write_text(html, encoding="utf-8")
        return html
