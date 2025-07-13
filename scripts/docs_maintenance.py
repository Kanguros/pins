#!/usr/bin/env python3
"""
Documentation maintenance automation script for Policy Inspector.

This script provides various maintenance tasks for the documentation:
- Update API documentation
- Check for outdated examples
- Validate internal links
- Generate documentation metrics
- Clean up generated files
"""

import argparse
import ast
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


class DocumentationMaintainer:
    """Main class for documentation maintenance tasks."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_dir = project_root / "docs"
        self.source_dir = self.docs_dir / "source"
        self.package_dir = project_root / "policy_inspector"

    def update_api_docs(self) -> None:
        """Update API documentation by scanning Python modules."""
        print("🔄 Updating API documentation...")

        # Find all Python modules
        modules = []
        for py_file in self.package_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            # Convert file path to module path
            relative_path = py_file.relative_to(self.package_dir)
            module_path = str(relative_path.with_suffix("")).replace(
                os.sep, "."
            )
            modules.append(f"policy_inspector.{module_path}")

        print(f"Found {len(modules)} modules")

        # Generate API documentation structure
        api_index_path = self.source_dir / "api" / "index.md"
        self._update_api_index(modules, api_index_path)

        print("✅ API documentation updated")

    def _update_api_index(
        self, modules: list[str], api_index_path: Path
    ) -> None:
        """Update the API index file with current modules."""
        # This is a simplified version - in practice you'd want more sophisticated
        # organization of modules by category

        content = """# API Reference

This section provides detailed documentation for all modules, classes, and functions in the Policy Inspector package.

## Core Modules

"""

        for module in sorted(modules):
            module_name = module.split(".")[-1]
            content += f"""
### {module_name.title().replace("_", " ")}

```{{eval-rst}}
.. automodule:: {module}
   :members:
   :undoc-members:
   :show-inheritance:
```
"""

        # Write the updated content
        api_index_path.write_text(content, encoding="utf-8")

    def check_docstring_coverage(self) -> dict[str, float]:
        """Check docstring coverage for all Python modules."""
        print("📊 Checking docstring coverage...")

        coverage_by_module = {}

        for py_file in self.package_dir.rglob("*.py"):
            if (
                py_file.name.startswith("test_")
                or py_file.name == "__init__.py"
            ):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                total_functions = 0
                documented_functions = 0

                for node in ast.walk(tree):
                    if isinstance(
                        node,
                        ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
                    ):
                        if not node.name.startswith("_"):  # Skip private
                            total_functions += 1
                            if ast.get_docstring(node):
                                documented_functions += 1

                if total_functions > 0:
                    coverage = (documented_functions / total_functions) * 100
                    module_name = str(py_file.relative_to(self.package_dir))
                    coverage_by_module[module_name] = coverage

            except Exception as e:
                print(f"Warning: Could not parse {py_file}: {e}")

        return coverage_by_module

    def validate_internal_links(self) -> list[str]:
        """Validate internal documentation links."""
        print("🔗 Validating internal links...")

        broken_links = []

        for md_file in self.source_dir.rglob("*.md"):
            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            # Find internal document references
            doc_refs = re.findall(r"\{doc\}`([^`]+)`", content)
            for ref in doc_refs:
                # Convert reference to file path
                if ref.startswith("/"):
                    ref_path = self.source_dir / ref[1:]
                else:
                    ref_path = md_file.parent / ref

                # Check if file exists (try both .md and .rst)
                if not (
                    ref_path.with_suffix(".md").exists()
                    or ref_path.with_suffix(".rst").exists()
                ):
                    broken_links.append(f"{md_file}: {ref}")

        return broken_links

    def check_outdated_examples(self) -> list[str]:
        """Check for potentially outdated code examples."""
        print("🔍 Checking for outdated examples...")

        outdated_examples = []

        for md_file in self.source_dir.rglob("*.md"):
            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            # Find code blocks with version-specific content
            version_patterns = [
                r"pins\s+--version",
                r'version\s*["\'][\d.]+["\']',
                r"Policy Inspector version [\d.]+",
            ]

            for pattern in version_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    outdated_examples.append(
                        f"{md_file}: Contains version-specific content"
                    )
                    break

        return outdated_examples

    def generate_metrics_report(self) -> None:
        """Generate comprehensive documentation metrics."""
        print("📈 Generating documentation metrics...")

        # Count documentation files
        md_files = list(self.source_dir.rglob("*.md"))
        rst_files = list(self.source_dir.rglob("*.rst"))

        # Check docstring coverage
        coverage_by_module = self.check_docstring_coverage()
        avg_coverage = (
            sum(coverage_by_module.values()) / len(coverage_by_module)
            if coverage_by_module
            else 0
        )

        # Check for broken links
        broken_links = self.validate_internal_links()

        # Check for outdated examples
        outdated_examples = self.check_outdated_examples()

        # Generate report
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""# Documentation Metrics Report

Generated on: {current_date}

## File Statistics
- Markdown files: {len(md_files)}
- reStructuredText files: {len(rst_files)}
- Total documentation files: {len(md_files) + len(rst_files)}

## Code Documentation Coverage
- Average docstring coverage: {avg_coverage:.1f}%
- Modules with low coverage (<80%):
"""

        for module, coverage in coverage_by_module.items():
            if coverage < 80:
                report += f"  - {module}: {coverage:.1f}%\n"

        report += f"""
## Link Validation
- Broken internal links: {len(broken_links)}
"""

        for link in broken_links:
            report += f"  - {link}\n"

        report += f"""
## Example Maintenance
- Potentially outdated examples: {len(outdated_examples)}
"""

        for example in outdated_examples:
            report += f"  - {example}\n"

        # Write report
        report_path = self.docs_dir / "metrics-report.md"
        report_path.write_text(report, encoding="utf-8")

        print(f"📊 Metrics report saved to: {report_path}")

    def clean_generated_files(self) -> None:
        """Clean up generated documentation files."""
        print("🧹 Cleaning generated files...")

        # Remove build directory
        build_dir = self.docs_dir / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print(f"Removed: {build_dir}")

        # Remove auto-generated RST files
        api_dir = self.source_dir / "api"
        if api_dir.exists():
            for rst_file in api_dir.glob("*.rst"):
                rst_file.unlink()
                print(f"Removed: {rst_file}")

        print("✅ Cleanup complete")

    def validate_structure(self) -> list[str]:
        """Validate documentation structure."""
        print("🏗️ Validating documentation structure...")

        issues = []

        # Check required files exist
        required_files = [
            "index.md",
            "guides/installation.md",
            "guides/quick-start.md",
            "guides/configuration.md",
            "guides/usage.md",
            "api/index.md",
            "examples/basic-usage.md",
            "development/contributing.md",
            "development/testing.md",
        ]

        for required_file in required_files:
            file_path = self.source_dir / required_file
            if not file_path.exists():
                issues.append(f"Missing required file: {required_file}")

        # Check for empty files
        for md_file in self.source_dir.rglob("*.md"):
            if md_file.stat().st_size < 50:  # Very small files
                issues.append(f"Suspiciously small file: {md_file}")

        return issues


def main():
    """Main entry point for the documentation maintenance script."""
    parser = argparse.ArgumentParser(
        description="Policy Inspector documentation maintenance automation"
    )
    parser.add_argument(
        "command",
        choices=[
            "update-api",
            "check-coverage",
            "validate-links",
            "check-examples",
            "generate-report",
            "clean",
            "validate-structure",
            "all",
        ],
        help="Maintenance command to run",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Initialize maintainer
    maintainer = DocumentationMaintainer(args.project_root)

    # Execute command
    if args.command == "update-api":
        maintainer.update_api_docs()

    elif args.command == "check-coverage":
        coverage = maintainer.check_docstring_coverage()
        for module, cov in coverage.items():
            status = "✅" if cov >= 80 else "⚠️"
            print(f"{status} {module}: {cov:.1f}%")

    elif args.command == "validate-links":
        broken_links = maintainer.validate_internal_links()
        if broken_links:
            print("❌ Broken internal links found:")
            for link in broken_links:
                print(f"  - {link}")
            sys.exit(1)
        else:
            print("✅ All internal links are valid")

    elif args.command == "check-examples":
        outdated = maintainer.check_outdated_examples()
        if outdated:
            print("⚠️ Potentially outdated examples:")
            for example in outdated:
                print(f"  - {example}")
        else:
            print("✅ No outdated examples detected")

    elif args.command == "generate-report":
        maintainer.generate_metrics_report()

    elif args.command == "clean":
        maintainer.clean_generated_files()

    elif args.command == "validate-structure":
        issues = maintainer.validate_structure()
        if issues:
            print("❌ Documentation structure issues:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("✅ Documentation structure is valid")

    elif args.command == "all":
        print("🚀 Running all maintenance tasks...")
        maintainer.validate_structure()
        maintainer.update_api_docs()
        maintainer.validate_internal_links()
        maintainer.check_outdated_examples()
        maintainer.generate_metrics_report()
        print("✅ All maintenance tasks completed")


if __name__ == "__main__":
    main()
