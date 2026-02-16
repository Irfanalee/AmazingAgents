"""Parser for package.json and other dependency files."""

import json
from pathlib import Path
from typing import Optional, List, Dict

from pydantic import BaseModel, Field


class PackageDependency(BaseModel):
    """Represents a software package dependency."""

    name: str
    version: str
    type: str = "runtime"  # runtime, dev, peer, optional
    vendor: Optional[str] = None

    def get_vendor(self) -> str:
        """Extract vendor from package name."""
        if self.vendor:
            return self.vendor

        if self.name.startswith("@"):
            parts = self.name[1:].split("/")
            return parts[0] if parts else "unknown"

        parts = self.name.split("-")
        return parts[0] if parts else self.name

    def get_product(self) -> str:
        """Extract product name from package name."""
        if self.name.startswith("@"):
            parts = self.name[1:].split("/")
            return parts[1] if len(parts) > 1 else self.name

        return self.name

    def clean_version(self) -> str:
        """Clean version string by removing operators and ranges."""
        version = self.version.strip()

        # Remove common version operators
        for prefix in ["^", "~", ">=", "<=", ">", "<", "=", "v"]:
            version = version.lstrip(prefix)

        # Handle version ranges (take the first version)
        if " - " in version:
            version = version.split(" - ")[0]
        if " || " in version:
            version = version.split(" || ")[0]
        if " " in version:
            version = version.split(" ")[0]

        return version.strip()


class PackageManifest(BaseModel):
    """Represents a package manifest file (package.json, etc.)."""

    name: Optional[str] = None
    version: Optional[str] = None
    dependencies: List[PackageDependency] = Field(default_factory=list)

    @property
    def all_dependencies(self) -> List[PackageDependency]:
        """Get all dependencies."""
        return self.dependencies

    @property
    def runtime_dependencies(self) -> List[PackageDependency]:
        """Get only runtime dependencies."""
        return [dep for dep in self.dependencies if dep.type == "runtime"]

    @property
    def total_count(self) -> int:
        """Get total number of dependencies."""
        return len(self.dependencies)


class PackageParser:
    """Parser for various package manifest files."""

    @staticmethod
    def parse_package_json(file_path: str | Path) -> PackageManifest:
        """
        Parse a package.json file.

        Args:
            file_path: Path to package.json file

        Returns:
            PackageManifest object

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        manifest = PackageManifest(
            name=data.get("name"),
            version=data.get("version")
        )

        # Parse dependencies
        dependencies = data.get("dependencies", {})
        for name, version in dependencies.items():
            manifest.dependencies.append(
                PackageDependency(name=name, version=version, type="runtime")
            )

        # Parse devDependencies
        dev_dependencies = data.get("devDependencies", {})
        for name, version in dev_dependencies.items():
            manifest.dependencies.append(
                PackageDependency(name=name, version=version, type="dev")
            )

        # Parse peerDependencies
        peer_dependencies = data.get("peerDependencies", {})
        for name, version in peer_dependencies.items():
            manifest.dependencies.append(
                PackageDependency(name=name, version=version, type="peer")
            )

        # Parse optionalDependencies
        optional_dependencies = data.get("optionalDependencies", {})
        for name, version in optional_dependencies.items():
            manifest.dependencies.append(
                PackageDependency(name=name, version=version, type="optional")
            )

        return manifest

    @staticmethod
    def parse_requirements_txt(file_path: str | Path) -> PackageManifest:
        """
        Parse a requirements.txt file (Python).

        Args:
            file_path: Path to requirements.txt file

        Returns:
            PackageManifest object
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        manifest = PackageManifest()

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue

                # Parse package==version or package>=version
                if "==" in line:
                    name, version = line.split("==", 1)
                elif ">=" in line:
                    name, version = line.split(">=", 1)
                elif "~=" in line:
                    name, version = line.split("~=", 1)
                else:
                    # No version specified
                    name = line
                    version = "*"

                manifest.dependencies.append(
                    PackageDependency(
                        name=name.strip(),
                        version=version.strip(),
                        type="runtime"
                    )
                )

        return manifest

    @staticmethod
    def auto_detect_and_parse(file_path: str | Path) -> PackageManifest:
        """
        Auto-detect file type and parse accordingly.

        Args:
            file_path: Path to the manifest file

        Returns:
            PackageManifest object
        """
        file_path = Path(file_path)
        file_name = file_path.name.lower()

        if file_name == "package.json":
            return PackageParser.parse_package_json(file_path)
        elif file_name in ["requirements.txt", "requirements.in"]:
            return PackageParser.parse_requirements_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_name}")
