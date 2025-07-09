from datetime import datetime, timezone
from pathlib import Path

from policy_inspector.scenarios.shadowing.advanced import AdvancedShadowing
from policy_inspector.scenarios.shadowing.simple import Shadowing
from policy_inspector.utils import load_jinja_template, register_export


@register_export(scenario_cls=Shadowing, fmt="html")
@register_export(scenario_cls=AdvancedShadowing, fmt="html")
def export_as_html(scenario, *args, **kwargs) -> str:
    """
    Render the HTML report using a Jinja2 template (report_template.html).
    """
    template_dir = Path(__file__).parent
    template = load_jinja_template(template_dir, "report_template.html")
    current_date = datetime.now(tz=timezone.utc).strftime("%B %d, %Y %H:%M:%S")
    return template.render(
        scenario=scenario,
        device_groups=getattr(scenario, "device_groups", []),
        address_groups_count=len(getattr(scenario, "address_groups", [])),
        address_objects_count=len(getattr(scenario, "address_objects", [])),
        total_policies=sum(
            len(rules)
            for rules in getattr(
                scenario, "security_rules_by_dg", {{}}
            ).values()
        ),
        current_date=current_date,
    )
