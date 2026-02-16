"""Tests for package parser."""

import pytest
from pathlib import Path
import json
import tempfile

from security_auditor.package_parser import PackageParser, PackageDependency, PackageManifest


def test_parse_package_json():
    """Test parsing a package.json file."""
    # Create a temporary package.json
    package_data = {
        "name": "test-app",
        "version": "1.0.0",
        "dependencies": {
            "express": "^4.17.1",
            "lodash": "~4.17.20"
        },
        "devDependencies": {
            "jest": "^27.0.0"
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(package_data, f)
        temp_path = f.name

    try:
        manifest = PackageParser.parse_package_json(temp_path)

        assert manifest.name == "test-app"
        assert manifest.version == "1.0.0"
        assert len(manifest.dependencies) == 3
        assert len(manifest.runtime_dependencies) == 2

        # Check runtime dependencies
        runtime_deps = {dep.name: dep for dep in manifest.runtime_dependencies}
        assert "express" in runtime_deps
        assert runtime_deps["express"].version == "^4.17.1"

    finally:
        Path(temp_path).unlink()


def test_parse_requirements_txt():
    """Test parsing a requirements.txt file."""
    requirements_content = """
# Comment line
requests==2.25.1
django>=3.2.0
numpy~=1.19.5
flask
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(requirements_content)
        temp_path = f.name

    try:
        manifest = PackageParser.parse_requirements_txt(temp_path)

        assert len(manifest.dependencies) == 4

        deps = {dep.name: dep for dep in manifest.dependencies}
        assert "requests" in deps
        assert deps["requests"].version == "2.25.1"
        assert "django" in deps
        assert deps["django"].version == "3.2.0"

    finally:
        Path(temp_path).unlink()


def test_clean_version():
    """Test version string cleaning."""
    dep1 = PackageDependency(name="test", version="^4.17.1")
    assert dep1.clean_version() == "4.17.1"

    dep2 = PackageDependency(name="test", version="~4.17.20")
    assert dep2.clean_version() == "4.17.20"

    dep3 = PackageDependency(name="test", version=">=3.2.0")
    assert dep3.clean_version() == "3.2.0"

    dep4 = PackageDependency(name="test", version="1.0.0 - 2.0.0")
    assert dep4.clean_version() == "1.0.0"


def test_get_vendor_and_product():
    """Test vendor and product extraction."""
    # Scoped package
    dep1 = PackageDependency(name="@angular/core", version="12.0.0")
    assert dep1.get_vendor() == "angular"
    assert dep1.get_product() == "core"

    # Regular package
    dep2 = PackageDependency(name="express", version="4.17.1")
    assert dep2.get_product() == "express"

    # Package with vendor set
    dep3 = PackageDependency(name="foo", version="1.0.0", vendor="custom-vendor")
    assert dep3.get_vendor() == "custom-vendor"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
