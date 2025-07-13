#!/usr/bin/env python3
"""
Final validation script for Policy Inspector documentation system.

This script performs comprehensive validation of the documentation system
to ensure all components are working correctly.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


class DocumentationValidator:
    """Validates the complete documentation system."""

    def __init__(self, root_dir: str = "."):
        """Initialize the validator.

        Args:
            root_dir: Root directory of the project
        """
        self.root_dir = Path(root_dir).resolve()
        self.docs_dir = self.root_dir / "docs"
        self.errors = []
        self.warnings = []

    def check_file_exists(self, file_path: Path, description: str) -> bool:
        """Check if a required file exists.

        Args:
            file_path: Path to check
            description: Description for error reporting

        Returns:
            True if file exists, False otherwise
        """
        if not file_path.exists():
            self.errors.append(f"Missing {description}: {file_path}")
            return False
        return True

    def check_directory_structure(self) -> bool:
        """Check that all required directories and files exist.

        Returns:
            True if structure is valid, False otherwise
        """
        print("🔍 Checking directory structure...")

        required_files = [
            (self.docs_dir / "source" / "conf.py", "Sphinx configuration"),
            (self.docs_dir / "source" / "index.md", "Main index file"),
            (self.docs_dir / "Makefile", "Makefile"),
            (self.docs_dir / "build.sh", "Unix build script"),
            (self.docs_dir / "build.bat", "Windows build script"),
            (
                self.root_dir / "requirements-docs.txt",
                "Documentation requirements",
            ),
        ]

        required_dirs = [
            (self.docs_dir / "source" / "guides", "Guides directory"),
            (self.docs_dir / "source" / "api", "API directory"),
            (self.docs_dir / "source" / "examples", "Examples directory"),
            (self.docs_dir / "source" / "development", "Development directory"),
            (self.docs_dir / "source" / "_static", "Static files directory"),
        ]

        success = True

        for file_path, description in required_files:
            if not self.check_file_exists(file_path, description):
                success = False

        for dir_path, description in required_dirs:
            if not dir_path.exists():
                self.errors.append(f"Missing {description}: {dir_path}")
                success = False

        return success

    def check_configuration(self) -> bool:
        """Check Sphinx configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        print("⚙️ Checking Sphinx configuration...")

        conf_file = self.docs_dir / "source" / "conf.py"
        if not conf_file.exists():
            return False

        try:
            with open(conf_file, encoding="utf-8") as f:
                conf_content = f.read()

            required_extensions = [
                "sphinx.ext.autodoc",
                "sphinx.ext.viewcode",
                "sphinx.ext.napoleon",
                "myst_parser",
            ]

            missing_extensions = []
            for ext in required_extensions:
                if ext not in conf_content:
                    missing_extensions.append(ext)

            if missing_extensions:
                self.errors.append(
                    f"Missing Sphinx extensions: {missing_extensions}"
                )
                return False

            # Check for MyST configuration
            if "myst_enable_extensions" not in conf_content:
                self.warnings.append("MyST extensions configuration not found")

            # Check for theme configuration
            if "sphinx_rtd_theme" not in conf_content:
                self.warnings.append("RTD theme not configured")

            return True

        except Exception as e:
            self.errors.append(f"Error reading configuration: {e}")
            return False

    def check_dependencies(self) -> bool:
        """Check that all required dependencies are installed.

        Returns:
            True if dependencies are available, False otherwise
        """
        print("📦 Checking dependencies...")

        required_packages = [
            "sphinx",
            "myst_parser",
            "sphinx_rtd_theme",
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            self.errors.append(f"Missing packages: {missing_packages}")
            return False

        return True

    def check_build_process(self) -> bool:
        """Test the documentation build process.

        Returns:
            True if build succeeds, False otherwise
        """
        print("🏗️ Testing build process...")

        try:
            # Test build
            cmd = [
                "poetry",
                "run",
                "sphinx-build",
                "-W",
                "-b",
                "html",
                str(self.docs_dir / "source"),
                str(self.docs_dir / "build" / "test"),
            ]

            result = subprocess.run(
                cmd,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                self.errors.append(f"Build failed: {result.stderr}")
                return False

            # Check that HTML files were generated
            html_dir = self.docs_dir / "build" / "test"
            if not (html_dir / "index.html").exists():
                self.errors.append("No HTML output generated")
                return False

            return True

        except Exception as e:
            self.errors.append(f"Build test failed: {e}")
            return False

    def check_linkcheck(self) -> bool:
        """Test link checking functionality.

        Returns:
            True if linkcheck works, False otherwise
        """
        print("🔗 Testing link checking...")

        try:
            cmd = [
                "poetry",
                "run",
                "sphinx-build",
                "-b",
                "linkcheck",
                str(self.docs_dir / "source"),
                str(self.docs_dir / "build" / "linkcheck"),
            ]

            result = subprocess.run(
                cmd,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            # Linkcheck can have warnings but shouldn't fail completely
            if result.returncode > 1:  # Allow for warnings (return code 1)
                self.warnings.append(f"Link check issues: {result.stderr}")

            return True

        except Exception as e:
            self.warnings.append(f"Link check test failed: {e}")
            return True  # Don't fail validation for linkcheck issues

    def check_scripts(self) -> bool:
        """Check that maintenance scripts work.

        Returns:
            True if scripts work, False otherwise
        """
        print("🛠️ Testing maintenance scripts...")

        scripts_dir = self.root_dir / "scripts"
        if not scripts_dir.exists():
            self.warnings.append("Scripts directory not found")
            return True

        scripts_to_test = [
            "docs_maintenance.py",
            "docs_versioning.py",
            "coverage_integration.py",
            "docstring_validator.py",
        ]

        for script_name in scripts_to_test:
            script_path = scripts_dir / script_name
            if not script_path.exists():
                self.warnings.append(f"Script not found: {script_name}")
                continue

            try:
                # Test script help
                cmd = ["poetry", "run", "python", str(script_path), "--help"]
                result = subprocess.run(
                    cmd,
                    cwd=self.root_dir,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode != 0:
                    self.warnings.append(f"Script {script_name} help failed")

            except Exception as e:
                self.warnings.append(f"Error testing script {script_name}: {e}")

        return True

    def check_github_actions(self) -> bool:
        """Check GitHub Actions workflow configuration.

        Returns:
            True if workflow is configured, False otherwise
        """
        print("🔄 Checking GitHub Actions configuration...")

        workflow_file = self.root_dir / ".github" / "workflows" / "docs.yml"
        if not workflow_file.exists():
            self.warnings.append("GitHub Actions workflow not found")
            return True

        try:
            with open(workflow_file, encoding="utf-8") as f:
                workflow_content = f.read()

            required_elements = [
                "sphinx-build",
                "github-pages",
                "upload-pages-artifact",
                "deploy-pages",
            ]

            missing_elements = []
            for element in required_elements:
                if element not in workflow_content:
                    missing_elements.append(element)

            if missing_elements:
                self.warnings.append(
                    f"Missing workflow elements: {missing_elements}"
                )

            return True

        except Exception as e:
            self.warnings.append(f"Error reading workflow: {e}")
            return True

    def validate_all(self) -> bool:
        """Run complete validation.

        Returns:
            True if all validations pass, False otherwise
        """
        print("🚀 Starting comprehensive documentation validation...\n")

        checks = [
            ("Directory Structure", self.check_directory_structure),
            ("Configuration", self.check_configuration),
            ("Dependencies", self.check_dependencies),
            ("Build Process", self.check_build_process),
            ("Link Checking", self.check_linkcheck),
            ("Scripts", self.check_scripts),
            ("GitHub Actions", self.check_github_actions),
        ]

        success_count = 0
        total_checks = len(checks)

        for check_name, check_func in checks:
            try:
                if check_func():
                    print(f"✅ {check_name}: PASSED")
                    success_count += 1
                else:
                    print(f"❌ {check_name}: FAILED")
            except Exception as e:
                print(f"💥 {check_name}: ERROR - {e}")

        print("\n📊 Validation Summary:")
        print(f"  ✅ Passed: {success_count}/{total_checks}")
        print(f"  ❌ Failed: {total_checks - success_count}/{total_checks}")

        if self.errors:
            print(f"\n🚨 Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        # Overall success if no errors
        overall_success = len(self.errors) == 0

        if overall_success:
            print("\n🎉 Documentation system validation PASSED!")
            print("   All critical components are working correctly.")
        else:
            print("\n💔 Documentation system validation FAILED!")
            print("   Please fix the errors above before proceeding.")

        return overall_success

    def generate_report(self) -> dict:
        """Generate a validation report.

        Returns:
            Validation report as dictionary
        """
        return {
            "validation_passed": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Policy Inspector documentation system"
    )

    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )

    args = parser.parse_args()

    validator = DocumentationValidator()

    if args.json:
        success = validator.validate_all()
        report = validator.generate_report()
        print(json.dumps(report, indent=2))
    else:
        success = validator.validate_all()

    # Exit with appropriate code
    if not success or (args.strict and validator.warnings):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
