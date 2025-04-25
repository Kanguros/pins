import inspect
from datetime import datetime
from html import escape
from typing import TYPE_CHECKING

from policy_inspector.scenario.shadowing import ShadowingCheckFunction

if TYPE_CHECKING:
    from policy_inspector.scenario.shadowing import (
        AnalysisResults,
        ExecuteResults,
    )

_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Firewall Policy Analysis Report</title>
    <style>
        :root {
            --primary-color: #FF6B35;
            --secondary-color: #FF9F1C;
            --accent-color: #EE4B2B;
            --text-color: #333333;
            --bg-cream: #FFF9F0;
        }

        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            line-height: 1.5;
            margin: 0 auto;
            background-color: white;
            color: var(--text-color);
            max-width: 1000px;
            padding: 1rem;
        }

        .container {
            width: 100%;
            box-shadow: 0 0 10px rgba(0,0,0,0.05);
            border-radius: 8px;
            overflow: hidden;
        }

        .report-header {
            text-align: center;
            padding: 1.2rem;
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
            color: white;
            margin-bottom: 1rem;
        }

        .report-header h1 {
            margin: 0;
            font-size: 1.6rem;
        }

        .report-header p {
            margin: 0.3rem 0 0;
            font-size: 0.9rem;
        }

        .content {
            padding: 0 1.5rem 1.5rem;
        }
        
        /* Two-column layout */
        .top-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .toc {
            background: white;
            border-bottom: 1px solid #eee;
            padding-bottom: 1rem;
        }

        .toc h2 {
            margin-top: 0.5rem;
            font-size: 1.2rem;
            color: var(--primary-color);
            margin-bottom: 0.8rem;
        }

        .toc-list {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }

        .toc-list li {
            margin-bottom: 0.4rem;
        }

        .toc-list a {
            display: grid;
            grid-template-columns: auto max-content;
            text-decoration: none;
            color: var(--text-color);
            align-items: end;
            position: relative;
            overflow: hidden;
        }

        .toc-list a:hover {
            color: var(--primary-color);
        }

        .toc-list a::after {
            content: "";
            position: absolute;
            bottom: 0.3em;
            width: 100%;
            border-bottom: 1px dotted #ccc;
            margin-right: -1rem;
            margin-left: 0.3rem;
        }

        .toc-list a span.title {
            position: relative;
            background: white;
            padding-right: 0.5rem;
            z-index: 1;
        }

        .toc-list a span.page {
            position: relative;
            background: white;
            padding-left: 0.5rem;
            z-index: 1;
            font-weight: 500;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.8rem;
        }

        .summary-card {
            background: white;
            border-radius: 4px;
            padding: 0.7rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            border: 1px solid #eee;
            border-left: 3px solid var(--secondary-color);
        }

        .summary-card h3 {
            margin: 0 0 0.3rem 0;
            font-size: 0.9rem;
            color: var(--primary-color);
        }

        .summary-card p {
            margin: 0;
            font-size: 1rem;
            font-weight: 500;
        }

        .finding-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            background: white;
            border: 1px solid #eee;
        }

        .finding-table th {
            background-color: var(--primary-color);
            color: white;
            padding: 0.5rem;
            text-align: left;
            font-size: 0.85rem;
        }

        .finding-table td {
            padding: 0.5rem;
            border-bottom: 1px solid #eee;
            font-size: 0.85rem;
        }

        .finding-table td:first-child {
            background-color: rgba(255, 107, 53, 0.08);
            font-weight: 500;
            max-width: 180px;
        }

        .finding-table tr:hover {
            background-color: rgba(255, 159, 28, 0.03);
        }

        h2.finding-header, h2.checks-header {
            color: var(--accent-color);
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            padding-bottom: 0.3rem;
            border-bottom: 1px solid var(--secondary-color);
            font-size: 1.2rem;
        }
        
        .checks-list {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }
        
        .check-item {
            margin-bottom: 1rem;
            padding: 0.8rem;
            background-color: rgba(255, 159, 28, 0.05);
            border-radius: 4px;
            border-left: 3px solid var(--secondary-color);
        }
        
        .check-name {
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }
        
        .check-doc {
            margin: 0;
            font-size: 0.9rem;
            line-height: 1.4;
        }
    </style>
</head>
<body>
"""
_FOOTER = """
</body>
</html>
"""


def export_as_html(
    analysis_results: "AnalysisResults",
    scenario_results: "ExecuteResults",
    checks: list[ShadowingCheckFunction],
) -> str:
    html = []
    html.append(f"""
    <div class="container">
        <div class="report-header">
            <h1>Firewall Policy Analysis Report</h1>
            <p>Generated: {datetime.now().strftime("%B %d, %Y %H:%M:%S")}</p>
        </div>
        
        <div class="content">
            <div class="top-section">
                <div class="toc">
                    <h2>Table of Contents</h2>
                    <ul class="toc-list">
                        {
        "".join(
            f'<li><a href="#finding-{i + 1}"><span class="title">Finding {i + 1}</span><span class="page">{i + 1}</span></a></li>'
            for i in range(len(analysis_results))
        )
    }
                        <li><a href="#checks"><span class="title">Checks</span><span class="page">C</span></a></li>
                    </ul>
                </div>

                <div>
                    <div class="summary-grid">
                        <div class="summary-card">
                            <h3>Total Policies Analyzed</h3>
                            <p>{len(scenario_results)}</p>
                        </div>
                        <div class="summary-card">
                            <h3>Shadowing Findings</h3>
                            <p>{len(analysis_results)}</p>
                        </div>
                        <div class="summary-card">
                            <h3>Affected Rules</h3>
                            <p>{
        sum(len(shadowing) + 1 for _, shadowing in analysis_results)
    }</p>
                        </div>
                        <div class="summary-card">
                            <h3>Analysis Date</h3>
                            <p>{datetime.now().strftime("%Y-%m-%d")}</p>
                        </div>
                    </div>
                </div>
            </div>""")

    # Findings
    for i, (rule, shadowing_rules) in enumerate(analysis_results):
        html.append(
            f'<h2 class="finding-header" id="finding-{i + 1}">Finding {i + 1}</h2>'
        )
        html.append('<table class="finding-table">')

        # Table headers
        headers = ["Attribute", "Shadowed Rule"] + [
            f"Preceding Rule {j}" for j in range(1, len(shadowing_rules) + 1)
        ]
        html.append(
            "<tr>" + "".join(f"<th>{escape(h)}</th>" for h in headers) + "</tr>"
        )

        # Table rows
        for attr in rule.__pydantic_fields__:
            values = [getattr(r, attr) for r in [rule] + shadowing_rules]
            formatted = []
            for v in values:
                if isinstance(v, (list, set)):
                    formatted_val = "<br>".join(escape(str(x)) for x in v)
                else:
                    formatted_val = escape(str(v))
                formatted.append(f"<td>{formatted_val}</td>")

            html.append(f"<tr><td>{escape(attr)}</td>{''.join(formatted)}</tr>")

        html.append("</table>")

    # Checks section
    html.append('<h2 class="checks-header" id="checks">Checks</h2>')
    html.append('<div class="checks-list">')
    for check in checks:
        check_name = check.__name__
        doc = inspect.getdoc(check) or "No description available"
        html.append(f"""
        <div class="check-item">
            <div class="check-name">{escape(check_name)}</div>
            <p class="check-doc">{escape(doc)}</p>
        </div>
        """)
    html.append("</div>")

    html.append("</div></div>")
    return "\n".join((_TEMPLATE, *html, _FOOTER))
