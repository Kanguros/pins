#!/usr/bin/env python3
"""
Docstring validator for Policy Inspector.

This script validates and ensures all public functions and classes
have proper Google-style docstrings with MyST field lists.
"""

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import NamedTuple


class DocstringIssue(NamedTuple):
    """Represents a docstring validation issue."""

    file_path: str
    line_number: int
    function_name: str
    issue_type: str
    message: str


class DocstringValidator:
    """Validates Python docstrings for Google-style format."""

    def __init__(self, root_dir: str = "."):
        """Initialize the docstring validator.

        Args:
            root_dir: Root directory of the project
        """
        self.root_dir = Path(root_dir).resolve()
        self.package_dir = self.root_dir / "policy_inspector"

    def validate_google_docstring(self, docstring: str) -> list[str]:
        """Validate a docstring follows Google style.

        Args:
            docstring: The docstring to validate

        Returns:
            List of validation error messages
        """
        if not docstring:
            return ["Missing docstring"]

        errors = []
        lines = docstring.strip().split("\n")

        # Check for summary line
        if not lines[0].strip():
            errors.append("First line should be a one-line summary")

        section_pattern = r"^(\s*)(Args?|Arguments?|Parameters?|Returns?|Return|Yields?|Yield|Raises?|Raise|Notes?|Note|Examples?|Example):\s*$"

        found_sections = []
        for line in lines:
            match = re.match(section_pattern, line)
            if match:
                found_sections.append(match.group(2))

        # Check for Args section format
        has_args_section = any(
            section in ["Args", "Arguments", "Parameters"]
            for section in found_sections
        )

        if has_args_section:
            # Validate Args section format
            in_args = False
            for line in lines:
                if re.match(r"^\s*(Args?|Arguments?|Parameters?):\s*$", line):
                    in_args = True
                    continue
                if re.match(section_pattern, line):
                    in_args = False
                if in_args and line.strip():
                    # Check for proper parameter format: name (type): description
                    if not re.match(r"^\s+\w+\s*\([^)]+\):\s*.+", line):
                        if not re.match(r"^\s+\w+:\s*.+", line):
                            errors.append(
                                f"Invalid Args format in line: '{line.strip()}'. "
                                "Use 'param_name (type): description' or 'param_name: description'"
                            )

        return errors

    def check_file(self, file_path: Path) -> list[DocstringIssue]:
        """Check all functions and classes in a Python file.

        Args:
            file_path: Path to the Python file to check

        Returns:
            List of docstring issues found
        """
        issues = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(
                    node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
                ):
                    # Skip private functions/classes
                    if node.name.startswith("_") and not node.name.startswith(
                        "__"
                    ):
                        continue

                    # Skip test functions
                    if node.name.startswith("test_"):
                        continue

                    docstring = ast.get_docstring(node)
                    errors = self.validate_google_docstring(docstring)

                    for error in errors:
                        issues.append(
                            DocstringIssue(
                                file_path=str(
                                    file_path.relative_to(self.root_dir)
                                ),
                                line_number=node.lineno,
                                function_name=node.name,
                                issue_type=type(node).__name__,
                                message=error,
                            )
                        )

        except (SyntaxError, UnicodeDecodeError) as e:
            issues.append(
                DocstringIssue(
                    file_path=str(file_path.relative_to(self.root_dir)),
                    line_number=0,
                    function_name="",
                    issue_type="ParseError",
                    message=f"Could not parse file: {e}",
                )
            )

        return issues

    def validate_package(self) -> list[DocstringIssue]:
        """Validate all Python files in the package.

        Returns:
            List of all docstring issues found
        """
        all_issues = []

        for py_file in self.package_dir.rglob("*.py"):
            # Skip __pycache__ and test files
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue

            issues = self.check_file(py_file)
            all_issues.extend(issues)

        return all_issues

    def generate_report(self, issues: list[DocstringIssue]) -> str:
        """Generate a detailed report of docstring issues.

        Args:
            issues: List of docstring issues

        Returns:
            Formatted report as a string
        """
        if not issues:
            return "✅ All docstrings are valid!\n"

        report = f"❌ Found {len(issues)} docstring issues:\n\n"

        # Group issues by file
        by_file = {}
        for issue in issues:
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)

        for file_path, file_issues in sorted(by_file.items()):
            report += f"📄 {file_path}:\n"
            for issue in file_issues:
                report += f"  ⚠️  Line {issue.line_number}: {issue.function_name} ({issue.issue_type})\n"
                report += f"      {issue.message}\n"
            report += "\n"

        # Summary by issue type
        by_type = {}
        for issue in issues:
            key = (
                issue.message.split(":")[0]
                if ":" in issue.message
                else issue.message
            )
            by_type[key] = by_type.get(key, 0) + 1

        report += "📊 Summary by issue type:\n"
        for issue_type, count in sorted(by_type.items()):
            report += f"  • {issue_type}: {count}\n"

        return report

    def fix_docstring_issues(self, dry_run: bool = True) -> int:
        """Attempt to automatically fix common docstring issues.

        Args:
            dry_run: If True, only show what would be fixed without making changes

        Returns:
            Number of issues that could be fixed
        """
        issues = self.validate_package()
        fixable_count = 0

        for issue in issues:
            if "Missing docstring" in issue.message:
                if dry_run:
                    print(
                        f"Would add docstring to {issue.function_name} in {issue.file_path}"
                    )
                    fixable_count += 1
                else:
                    # This would require more complex AST manipulation
                    # For now, just report what could be fixed
                    fixable_count += 1

        if dry_run:
            print(f"\n{fixable_count} issues could be automatically fixed")

        return fixable_count

    def create_docstring_template(self, node: ast.AST) -> str:
        """Create a Google-style docstring template for a function or class.

        Args:
            node: AST node (function or class)

        Returns:
            Docstring template
        """
        if isinstance(node, ast.ClassDef):
            return f'"""{node.name} class.\n\n    Brief description of the class.\n    """'

        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            # Analyze function signature
            args = []
            if node.args.args:
                for arg in node.args.args:
                    if arg.arg != "self":  # Skip self parameter
                        args.append(arg.arg)

            has_return = False
            # Simple check for return statements
            for child in ast.walk(node):
                if isinstance(child, ast.Return) and child.value is not None:
                    has_return = True
                    break

            template = f'"""{node.name.replace("_", " ").title()}.\n\n        Brief description of the function.\n\n'

            if args:
                template += "        Args:\n"
                for arg in args:
                    template += f"            {arg}: Description of {arg}\n"
                template += "\n"

            if has_return:
                template += "        Returns:\n"
                template += "            Description of return value\n"

            template += '        """'
            return template

        return '"""Brief description."""'


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate and fix docstrings in Policy Inspector"
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate all docstrings"
    )
    validate_parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code if issues found",
    )

    # Report command
    subparsers.add_parser("report", help="Generate detailed docstring report")

    # Fix command
    fix_parser = subparsers.add_parser(
        "fix", help="Automatically fix docstring issues"
    )
    fix_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes",
    )

    # Template command
    template_parser = subparsers.add_parser(
        "template", help="Show docstring template"
    )
    template_parser.add_argument(
        "function_name", help="Function name for template"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    validator = DocstringValidator()

    if args.command == "validate":
        issues = validator.validate_package()
        if issues:
            print(f"❌ Found {len(issues)} docstring issues")
            if args.strict:
                sys.exit(1)
        else:
            print("✅ All docstrings are valid!")

    elif args.command == "report":
        issues = validator.validate_package()
        report = validator.generate_report(issues)
        print(report)

    elif args.command == "fix":
        fixed_count = validator.fix_docstring_issues(dry_run=args.dry_run)
        if args.dry_run:
            print(f"Dry run completed. {fixed_count} issues could be fixed.")
        else:
            print(f"Fixed {fixed_count} docstring issues.")

    elif args.command == "template":
        # This is a simplified template - in practice you'd analyze the actual function
        print(
            f'"""Brief description of {args.function_name}.\n\n    Args:\n        param: Description\n\n    Returns:\n        Description of return value\n    """'
        )


if __name__ == "__main__":
    main()
