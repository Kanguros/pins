#!/usr/bin/env python3
"""
Code coverage integration for Policy Inspector documentation.

This script integrates code coverage reports with documentation coverage
to provide comprehensive coverage metrics.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class CoverageMetrics(NamedTuple):
    """Coverage metrics structure."""

    code_coverage: float
    doc_coverage: float
    combined_score: float
    missing_docs: list
    uncovered_lines: int


class CoverageIntegrator:
    """Integrates code and documentation coverage."""

    def __init__(self, root_dir: str = "."):
        """Initialize the coverage integrator.

        Args:
            root_dir: Root directory of the project
        """
        self.root_dir = Path(root_dir).resolve()
        self.package_dir = self.root_dir / "policy_inspector"

    def get_code_coverage(self) -> dict:
        """Get code coverage metrics from pytest-cov.

        Returns:
            Code coverage data
        """
        # Run pytest with coverage
        cmd = [
            "poetry",
            "run",
            "pytest",
            "--cov=policy_inspector",
            "--cov-report=json",
            "--cov-report=term-missing",
            "--quiet",
        ]

        try:
            subprocess.run(
                cmd,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            # Read coverage JSON report
            coverage_file = self.root_dir / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, encoding="utf-8") as f:
                    return json.load(f)

        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            print(f"Error getting code coverage: {e}")

        return {"totals": {"percent_covered": 0}}

    def get_documentation_coverage(self) -> dict:
        """Get documentation coverage metrics.

        Returns:
            Documentation coverage data
        """
        try:
            # Use interrogate for docstring coverage
            cmd = [
                "poetry",
                "run",
                "interrogate",
                "--generate-badge",
                ".",
                "--badge-format",
                "svg",
                "--output",
                "docs/build/",
                "--quiet-level",
                "2",
                str(self.package_dir),
            ]

            result = subprocess.run(
                cmd,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            # Parse output for coverage percentage
            output = result.stdout
            coverage_line = [
                line
                for line in output.split("\n")
                if "%" in line and "documented" in line
            ]

            if coverage_line:
                # Extract percentage from output like "85.0% documented"
                percent_str = coverage_line[0].split("%")[0].split()[-1]
                coverage_percent = float(percent_str)
            else:
                coverage_percent = 0.0

            # Get list of missing docstrings
            cmd_detailed = [
                "poetry",
                "run",
                "interrogate",
                "--verbose",
                "2",
                str(self.package_dir),
            ]

            result_detailed = subprocess.run(
                cmd_detailed,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            missing_docs = []
            for line in result_detailed.stdout.split("\n"):
                if "MISSING" in line or "missing docstring" in line:
                    missing_docs.append(line.strip())

            return {
                "coverage_percent": coverage_percent,
                "missing_docs": missing_docs,
            }

        except (subprocess.SubprocessError, ValueError) as e:
            print(f"Error getting documentation coverage: {e}")
            return {"coverage_percent": 0.0, "missing_docs": []}

    def calculate_combined_metrics(self) -> CoverageMetrics:
        """Calculate combined coverage metrics.

        Returns:
            Combined coverage metrics
        """
        code_data = self.get_code_coverage()
        doc_data = self.get_documentation_coverage()

        code_coverage = code_data.get("totals", {}).get("percent_covered", 0)
        doc_coverage = doc_data.get("coverage_percent", 0)

        # Combined score: weighted average (code coverage 60%, docs 40%)
        combined_score = (code_coverage * 0.6) + (doc_coverage * 0.4)

        missing_docs = doc_data.get("missing_docs", [])
        uncovered_lines = code_data.get("totals", {}).get("missing_lines", 0)

        return CoverageMetrics(
            code_coverage=code_coverage,
            doc_coverage=doc_coverage,
            combined_score=combined_score,
            missing_docs=missing_docs,
            uncovered_lines=uncovered_lines,
        )

    def generate_coverage_report(self) -> str:
        """Generate a comprehensive coverage report.

        Returns:
            Coverage report as markdown string
        """
        metrics = self.calculate_combined_metrics()

        report = f"""# Coverage Report

## Summary

- **Code Coverage**: {metrics.code_coverage:.1f}%
- **Documentation Coverage**: {metrics.doc_coverage:.1f}%
- **Combined Score**: {metrics.combined_score:.1f}%

## Code Coverage Details

"""

        if metrics.uncovered_lines > 0:
            report += f"- **Uncovered Lines**: {metrics.uncovered_lines}\n"

        report += """
## Documentation Coverage Details

"""

        if metrics.missing_docs:
            report += "### Missing Docstrings\n\n"
            for missing in metrics.missing_docs[:10]:  # Limit to first 10
                report += f"- {missing}\n"

            if len(metrics.missing_docs) > 10:
                report += f"- ... and {len(metrics.missing_docs) - 10} more\n"
        else:
            report += "All functions and classes have docstrings! 🎉\n"

        report += f"""
## Quality Gates

| Metric | Current | Target | Status |
|--------|---------|--------|---------|
| Code Coverage | {metrics.code_coverage:.1f}% | 80% | {"✅" if metrics.code_coverage >= 80 else "❌"} |
| Doc Coverage | {metrics.doc_coverage:.1f}% | 90% | {"✅" if metrics.doc_coverage >= 90 else "❌"} |
| Combined Score | {metrics.combined_score:.1f}% | 85% | {"✅" if metrics.combined_score >= 85 else "❌"} |

## Recommendations

"""

        if metrics.code_coverage < 80:
            report += "- Add more unit tests to improve code coverage\n"

        if metrics.doc_coverage < 90:
            report += "- Add docstrings to missing functions and classes\n"

        if metrics.combined_score < 85:
            report += "- Focus on both code tests and documentation\n"

        if metrics.combined_score >= 85:
            report += "- Great job! Coverage targets are met 🎉\n"

        return report

    def save_coverage_badge(self, metrics: CoverageMetrics) -> None:
        """Save coverage badges for use in documentation.

        Args:
            metrics: Coverage metrics
        """
        badges_dir = self.root_dir / "docs" / "source" / "_static" / "badges"
        badges_dir.mkdir(parents=True, exist_ok=True)

        # Generate SVG badges (simplified version)
        def create_badge_svg(label: str, value: str, color: str) -> str:
            """Create a simple SVG badge."""
            return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="104" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <clipPath id="a">
        <rect width="104" height="20" rx="3" fill="#fff"/>
    </clipPath>
    <g clip-path="url(#a)">
        <path fill="#555" d="M0 0h63v20H0z"/>
        <path fill="{color}" d="M63 0h41v20H63z"/>
        <path fill="url(#b)" d="M0 0h104v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">
        <text x="325" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="530">{label}</text>
        <text x="325" y="140" transform="scale(.1)" textLength="530">{label}</text>
        <text x="825" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="310">{value}</text>
        <text x="825" y="140" transform="scale(.1)" textLength="310">{value}</text>
    </g>
</svg>"""

        # Create badges
        badges = [
            (
                "coverage",
                f"{metrics.code_coverage:.0f}%",
                "#4c1" if metrics.code_coverage >= 80 else "#e05d44",
            ),
            (
                "docs",
                f"{metrics.doc_coverage:.0f}%",
                "#4c1" if metrics.doc_coverage >= 90 else "#e05d44",
            ),
            (
                "combined",
                f"{metrics.combined_score:.0f}%",
                "#4c1" if metrics.combined_score >= 85 else "#e05d44",
            ),
        ]

        for label, value, color in badges:
            badge_path = badges_dir / f"{label}-badge.svg"
            with open(badge_path, "w", encoding="utf-8") as f:
                f.write(create_badge_svg(label, value, color))

        print(f"Coverage badges saved to {badges_dir}")

    def run_full_coverage_check(self) -> bool:
        """Run full coverage check and generate reports.

        Returns:
            True if all coverage targets are met, False otherwise
        """
        print("Running comprehensive coverage analysis...")

        metrics = self.calculate_combined_metrics()

        # Generate and save report
        report = self.generate_coverage_report()
        report_path = self.root_dir / "docs" / "build" / "coverage-report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"Coverage report saved to {report_path}")

        # Save badges
        self.save_coverage_badge(metrics)

        # Print summary
        print("\n" + "=" * 50)
        print("COVERAGE SUMMARY")
        print("=" * 50)
        print(f"Code Coverage:    {metrics.code_coverage:.1f}%")
        print(f"Doc Coverage:     {metrics.doc_coverage:.1f}%")
        print(f"Combined Score:   {metrics.combined_score:.1f}%")
        print("=" * 50)

        # Check if targets are met
        targets_met = (
            metrics.code_coverage >= 80
            and metrics.doc_coverage >= 90
            and metrics.combined_score >= 85
        )

        if targets_met:
            print("✅ All coverage targets met!")
        else:
            print("❌ Coverage targets not met")
            if metrics.code_coverage < 80:
                print(
                    f"  - Code coverage below 80% ({metrics.code_coverage:.1f}%)"
                )
            if metrics.doc_coverage < 90:
                print(
                    f"  - Doc coverage below 90% ({metrics.doc_coverage:.1f}%)"
                )
            if metrics.combined_score < 85:
                print(
                    f"  - Combined score below 85% ({metrics.combined_score:.1f}%)"
                )

        return targets_met


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Integrate code and documentation coverage for Policy Inspector"
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    # Run command
    subparsers.add_parser("run", help="Run full coverage analysis")

    # Report command
    subparsers.add_parser("report", help="Generate coverage report only")

    # Badges command
    subparsers.add_parser("badges", help="Generate coverage badges only")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    integrator = CoverageIntegrator()

    if args.command == "run":
        success = integrator.run_full_coverage_check()
        sys.exit(0 if success else 1)
    elif args.command == "report":
        report = integrator.generate_coverage_report()
        print(report)
    elif args.command == "badges":
        metrics = integrator.calculate_combined_metrics()
        integrator.save_coverage_badge(metrics)


if __name__ == "__main__":
    main()
