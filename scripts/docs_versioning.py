#!/usr/bin/env python3
"""
Documentation versioning script for Policy Inspector.

This script helps manage documentation versions for different releases.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


class DocumentationVersionManager:
    """Manages documentation versions and deployments."""

    def __init__(self, root_dir: str = "."):
        """Initialize the version manager.

        Args:
            root_dir: Root directory of the project
        """
        self.root_dir = Path(root_dir).resolve()
        self.docs_dir = self.root_dir / "docs"
        self.versions_file = self.docs_dir / "versions.json"
        self.build_dir = self.docs_dir / "build"

    def get_current_version(self) -> str:
        """Get the current version from pyproject.toml.

        Returns:
            Current version string
        """
        pyproject_file = self.root_dir / "pyproject.toml"
        if not pyproject_file.exists():
            raise FileNotFoundError("pyproject.toml not found")

        with open(pyproject_file, encoding="utf-8") as f:
            content = f.read()

        # Simple version extraction (can be improved with toml library)
        for line in content.split("\n"):
            if line.strip().startswith("version ="):
                return line.split("=")[1].strip().strip('"').strip("'")

        raise ValueError("Version not found in pyproject.toml")

    def load_versions(self) -> dict:
        """Load version configuration.

        Returns:
            Version configuration dictionary
        """
        if self.versions_file.exists():
            with open(self.versions_file, encoding="utf-8") as f:
                return json.load(f)

        return {"versions": [], "latest": None, "stable": None}

    def save_versions(self, config: dict) -> None:
        """Save version configuration.

        Args:
            config: Version configuration dictionary
        """
        with open(self.versions_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def add_version(
        self, version: str, is_latest: bool = False, is_stable: bool = False
    ) -> None:
        """Add a new version to the configuration.

        Args:
            version: Version string to add
            is_latest: Whether this is the latest version
            is_stable: Whether this is the stable version
        """
        config = self.load_versions()

        # Check if version already exists
        existing_versions = [v["name"] for v in config["versions"]]
        if version in existing_versions:
            print(f"Version {version} already exists")
            return

        # Add new version
        version_info = {
            "name": version,
            "url": f"/{version}/",
            "title": f"v{version}",
        }

        config["versions"].append(version_info)

        # Sort versions (latest first)
        config["versions"].sort(key=lambda x: x["name"], reverse=True)

        # Update latest and stable
        if is_latest or not config["latest"]:
            config["latest"] = version

        if is_stable or not config["stable"]:
            config["stable"] = version

        self.save_versions(config)
        print(f"Added version {version}")

    def build_version(self, version: str) -> None:
        """Build documentation for a specific version.

        Args:
            version: Version to build
        """
        print(f"Building documentation for version {version}")

        # Create version-specific build directory
        version_build_dir = self.build_dir / version
        version_build_dir.mkdir(parents=True, exist_ok=True)

        # Build documentation
        cmd = [
            "poetry",
            "run",
            "sphinx-build",
            "-b",
            "html",
            "docs/source",
            str(version_build_dir),
            "-D",
            f"version={version}",
            "-D",
            f"release={version}",
        ]

        result = subprocess.run(
            cmd, cwd=self.root_dir, capture_output=True, text=True, check=False
        )

        if result.returncode != 0:
            print(f"Build failed for version {version}")
            print(result.stderr)
            sys.exit(1)

        print(f"Successfully built documentation for version {version}")

    def create_version_selector(self) -> None:
        """Create version selector JavaScript."""
        config = self.load_versions()

        js_content = f"""
// Version selector for Policy Inspector documentation
(function() {{
    const versions = {json.dumps(config, indent=2)};

    function createVersionSelector() {{
        const selector = document.createElement('select');
        selector.className = 'version-selector';
        selector.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
            background: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 5px;
        `;

        // Add current version option
        const currentPath = window.location.pathname;
        let currentVersion = 'latest';

        versions.versions.forEach(function(version) {{
            if (currentPath.includes('/' + version.name + '/')) {{
                currentVersion = version.name;
            }}
        }});

        // Create options
        versions.versions.forEach(function(version) {{
            const option = document.createElement('option');
            option.value = version.name;
            option.textContent = version.title;
            option.selected = version.name === currentVersion;
            selector.appendChild(option);
        }});

        # Handle selection change
        selector.addEventListener('change', function() {{
            const selectedVersion = this.value;
            const newPath = window.location.pathname.replace(
                /\\/v?\\d+\\.\\d+\\.\\d+\\//,
                '/' + selectedVersion + '/'
            );
            window.location.href = newPath;
        }});

        document.body.appendChild(selector);
    }}

    // Create selector when page loads
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', createVersionSelector);
    }} else {{
        createVersionSelector();
    }}
}})();
"""

        # Save to static directory
        static_dir = self.docs_dir / "source" / "_static"
        static_dir.mkdir(exist_ok=True)

        with open(
            static_dir / "version-selector.js", "w", encoding="utf-8"
        ) as f:
            f.write(js_content)

        print("Created version selector")

    def deploy_version(self, version: str, target_dir: str) -> None:
        """Deploy a version to a target directory.

        Args:
            version: Version to deploy
            target_dir: Target deployment directory
        """
        source_dir = self.build_dir / version
        target_path = Path(target_dir) / version

        if not source_dir.exists():
            print(f"Build directory for version {version} not found")
            return

        # Create target directory
        target_path.mkdir(parents=True, exist_ok=True)

        # Copy files
        shutil.copytree(source_dir, target_path, dirs_exist_ok=True)

        print(f"Deployed version {version} to {target_path}")

    def list_versions(self) -> None:
        """List all configured versions."""
        config = self.load_versions()

        print("Configured versions:")
        for version in config["versions"]:
            tags = []
            if version["name"] == config.get("latest"):
                tags.append("latest")
            if version["name"] == config.get("stable"):
                tags.append("stable")

            tag_str = f" ({', '.join(tags)})" if tags else ""
            print(f"  - {version['name']}{tag_str}")

    def current_version_command(self) -> None:
        """Show current version and add it to versions."""
        current_version = self.get_current_version()
        print(f"Current version: {current_version}")

        # Ask if user wants to add this version
        response = input(
            f"Add version {current_version} to documentation? (y/N): "
        )
        if response.lower() in ["y", "yes"]:
            self.add_version(current_version, is_latest=True)
            self.create_version_selector()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Manage documentation versions for Policy Inspector"
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    # Current version command
    subparsers.add_parser(
        "current", help="Show current version and optionally add to docs"
    )

    # Add version command
    add_parser = subparsers.add_parser("add", help="Add a new version")
    add_parser.add_argument("version", help="Version to add")
    add_parser.add_argument(
        "--latest", action="store_true", help="Mark as latest version"
    )
    add_parser.add_argument(
        "--stable", action="store_true", help="Mark as stable version"
    )

    # Build command
    build_parser = subparsers.add_parser("build", help="Build documentation")
    build_parser.add_argument("version", help="Version to build")

    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy documentation")
    deploy_parser.add_argument("version", help="Version to deploy")
    deploy_parser.add_argument("target", help="Target directory")

    # List command
    subparsers.add_parser("list", help="List all versions")

    # Create selector command
    subparsers.add_parser("create-selector", help="Create version selector")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = DocumentationVersionManager()

    if args.command == "current":
        manager.current_version_command()
    elif args.command == "add":
        manager.add_version(args.version, args.latest, args.stable)
    elif args.command == "build":
        manager.build_version(args.version)
    elif args.command == "deploy":
        manager.deploy_version(args.version, args.target)
    elif args.command == "list":
        manager.list_versions()
    elif args.command == "create-selector":
        manager.create_version_selector()


if __name__ == "__main__":
    main()
