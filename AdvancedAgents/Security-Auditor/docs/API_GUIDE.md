# API Usage Guide

This guide covers the Python API for Security Auditor, allowing you to integrate vulnerability scanning into your own applications.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [NVD Client](#nvd-client)
3. [Package Parser](#package-parser)
4. [Vulnerability Analyzer](#vulnerability-analyzer)
5. [Report Generation](#report-generation)
6. [Advanced Examples](#advanced-examples)

## Basic Usage

### Simple Audit Example

```python
import asyncio
from security_auditor.nvd_client import NVDClient
from security_auditor.package_parser import PackageParser
from security_auditor.analyzer import VulnerabilityAnalyzer
from security_auditor.report import ExecutiveSummaryGenerator

async def audit_package_file(file_path: str):
    """Audit a package file for vulnerabilities."""

    # Parse the package file
    manifest = PackageParser.auto_detect_and_parse(file_path)
    print(f"Found {manifest.total_count} dependencies")

    # Initialize NVD client
    async with NVDClient(api_key="your-api-key-here") as nvd_client:
        # Create analyzer
        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=["CRITICAL", "HIGH"]
        )

        # Analyze dependencies
        result = await analyzer.analyze_manifest(manifest)

        # Generate and print report
        report = ExecutiveSummaryGenerator.generate_text_summary(result)
        print(report)

        return result

# Run the audit
result = asyncio.run(audit_package_file("package.json"))
```

## NVD Client

The NVD Client handles all communication with the NIST National Vulnerability Database API.

### Initialization

```python
from security_auditor.nvd_client import NVDClient

# Without API key (5 requests per 30 seconds)
client = NVDClient()

# With API key (50 requests per 30 seconds)
client = NVDClient(
    api_key="your-api-key",
    rate_limit=50,
    timeout=30
)

# Use as async context manager
async with NVDClient(api_key="your-api-key") as client:
    # Your code here
    pass
```

### Search for CVEs

```python
async def search_examples(client: NVDClient):
    # Search by CVE ID
    cve = await client.get_cve_by_id("CVE-2024-1234")
    if cve:
        print(f"Severity: {cve.severity}")
        print(f"Score: {cve.score}")
        print(f"Description: {cve.description}")

    # Search by keyword
    cves = await client.search_cves(
        keyword="nodejs buffer overflow",
        cvss_v3_severity="CRITICAL",
        results_per_page=10
    )

    # Search by product
    cves = await client.search_by_product(
        vendor="nodejs",
        product="node.js",
        version="14.0.0",
        severity_filter=["CRITICAL", "HIGH"]
    )

    # Search with date range
    from datetime import datetime, timedelta

    start_date = datetime.now() - timedelta(days=30)
    cves = await client.search_cves(
        keyword="express",
        published_start=start_date
    )
```

### CVE Data Structure

```python
from security_auditor.nvd_client import CVEData

# CVEData attributes
cve = await client.get_cve_by_id("CVE-2024-1234")

print(cve.cve_id)              # CVE identifier
print(cve.description)         # Vulnerability description
print(cve.published_date)      # Publication date
print(cve.last_modified_date)  # Last modification date
print(cve.severity)            # Severity level (CRITICAL, HIGH, etc.)
print(cve.score)               # CVSS score (0-10)
print(cve.references)          # List of reference URLs
print(cve.cpe_matches)         # List of affected CPE strings

# CVSS metrics (v3 or v2)
if cve.cvss_v3:
    print(cve.cvss_v3.base_score)
    print(cve.cvss_v3.base_severity)
    print(cve.cvss_v3.vector_string)
```

## Package Parser

The Package Parser extracts dependency information from manifest files.

### Parsing Different File Types

```python
from security_auditor.package_parser import PackageParser

# Auto-detect and parse
manifest = PackageParser.auto_detect_and_parse("package.json")

# Parse specific formats
npm_manifest = PackageParser.parse_package_json("package.json")
python_manifest = PackageParser.parse_requirements_txt("requirements.txt")
```

### Working with Manifests

```python
from security_auditor.package_parser import PackageManifest

manifest = PackageParser.parse_package_json("package.json")

# Get project info
print(manifest.name)
print(manifest.version)

# Get all dependencies
all_deps = manifest.all_dependencies
print(f"Total dependencies: {manifest.total_count}")

# Get only runtime dependencies (excludes dev dependencies)
runtime_deps = manifest.runtime_dependencies

# Iterate through dependencies
for dep in manifest.dependencies:
    print(f"{dep.name}@{dep.version} ({dep.type})")
    print(f"  Vendor: {dep.get_vendor()}")
    print(f"  Product: {dep.get_product()}")
    print(f"  Clean version: {dep.clean_version()}")
```

### Creating Manifests Programmatically

```python
from security_auditor.package_parser import PackageManifest, PackageDependency

manifest = PackageManifest(
    name="my-project",
    version="1.0.0",
    dependencies=[
        PackageDependency(name="express", version="^4.17.1", type="runtime"),
        PackageDependency(name="lodash", version="~4.17.20", type="runtime"),
        PackageDependency(name="jest", version="^27.0.0", type="dev"),
    ]
)
```

## Vulnerability Analyzer

The Vulnerability Analyzer matches dependencies to CVEs and generates analysis results.

### Basic Analysis

```python
from security_auditor.analyzer import VulnerabilityAnalyzer

async def analyze_dependencies():
    # Parse manifest
    manifest = PackageParser.parse_package_json("package.json")

    # Initialize analyzer
    async with NVDClient(api_key="your-key") as nvd_client:
        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=["CRITICAL", "HIGH"],
            include_dev_dependencies=False
        )

        # Analyze
        result = await analyzer.analyze_manifest(manifest)

        # Access results
        print(f"Total vulnerabilities: {result.severity_stats.total}")
        print(f"Critical: {result.severity_stats.critical}")
        print(f"High: {result.severity_stats.high}")
```

### Working with Analysis Results

```python
from security_auditor.analyzer import AnalysisResult

# Get actionable vulnerabilities (CRITICAL + HIGH)
actionable = result.get_actionable_vulnerabilities()

# Get by severity
critical = result.get_critical_vulnerabilities()
high = result.get_high_vulnerabilities()

# Get recent vulnerabilities (last 30 days)
recent = result.get_recent_vulnerabilities(days=30)

# Group by package
by_package = result.get_vulnerabilities_by_package()
for package_name, vulnerabilities in by_package.items():
    print(f"{package_name}: {len(vulnerabilities)} vulnerabilities")
    for vuln in vulnerabilities:
        print(f"  - {vuln.cve.cve_id} [{vuln.cve.severity}]")
```

### Custom Severity Filtering

```python
# Only CRITICAL
analyzer = VulnerabilityAnalyzer(
    nvd_client=nvd_client,
    severity_filter=["CRITICAL"]
)

# All severities
analyzer = VulnerabilityAnalyzer(
    nvd_client=nvd_client,
    severity_filter=["CRITICAL", "HIGH", "MEDIUM", "LOW"]
)

# Time-based filtering
result = await analyzer.analyze_manifest(
    manifest,
    days_back=30  # Only CVEs from last 30 days
)
```

## Report Generation

Generate executive summaries in multiple formats.

### Text Reports

```python
from security_auditor.report import ExecutiveSummaryGenerator

# Generate detailed text report
text_report = ExecutiveSummaryGenerator.generate_text_summary(
    result,
    include_details=True
)
print(text_report)

# Generate summary without details
brief_report = ExecutiveSummaryGenerator.generate_text_summary(
    result,
    include_details=False
)
```

### Markdown Reports

```python
# Generate markdown report
markdown_report = ExecutiveSummaryGenerator.generate_markdown_summary(result)

# Save to file
with open("security-report.md", "w") as f:
    f.write(markdown_report)
```

### JSON Reports

```python
import json

# Generate JSON summary
json_summary = ExecutiveSummaryGenerator.generate_json_summary(result)

# Save to file
with open("security-report.json", "w") as f:
    json.dump(json_summary, f, indent=2)

# Access data
print(json_summary["summary"]["total_vulnerabilities"])
print(json_summary["severity_breakdown"])
print(json_summary["risk_level"])
```

## Advanced Examples

### Parallel Analysis of Multiple Files

```python
async def analyze_multiple_projects():
    async with NVDClient(api_key="your-key") as nvd_client:
        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=["CRITICAL", "HIGH"]
        )

        files = ["project1/package.json", "project2/package.json"]

        tasks = []
        for file_path in files:
            manifest = PackageParser.auto_detect_and_parse(file_path)
            task = analyzer.analyze_manifest(manifest)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        for file_path, result in zip(files, results):
            print(f"\n{file_path}:")
            print(f"  Vulnerabilities: {result.severity_stats.total}")
```

### Custom Reporting

```python
def generate_custom_report(result: AnalysisResult) -> str:
    """Generate a custom security report."""
    lines = []

    # Custom header
    lines.append("🔒 SECURITY SCAN RESULTS")
    lines.append("=" * 50)

    # Summary
    actionable = result.severity_stats.actionable
    if actionable > 0:
        lines.append(f"⚠️  {actionable} ACTIONABLE ISSUES FOUND!")
    else:
        lines.append("✅ No critical issues detected")

    # Per-package breakdown
    by_package = result.get_vulnerabilities_by_package()
    lines.append(f"\n📦 Affected Packages: {len(by_package)}")

    for pkg_name, vulns in sorted(by_package.items()):
        lines.append(f"\n  {pkg_name}:")
        for vuln in vulns[:3]:
            lines.append(f"    • {vuln.cve.cve_id} - {vuln.cve.severity}")

    return "\n".join(lines)

# Use custom report
custom_report = generate_custom_report(result)
print(custom_report)
```

### Integration with CI/CD

```python
async def ci_security_check(package_file: str) -> int:
    """
    Security check for CI/CD pipeline.

    Returns:
        0 if no critical/high vulnerabilities
        1 if high vulnerabilities found
        2 if critical vulnerabilities found
    """
    manifest = PackageParser.auto_detect_and_parse(package_file)

    async with NVDClient(api_key=os.getenv("NVD_API_KEY")) as nvd_client:
        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=["CRITICAL", "HIGH"]
        )

        result = await analyzer.analyze_manifest(manifest)

        # Generate report
        report = ExecutiveSummaryGenerator.generate_markdown_summary(result)

        # Save report
        with open("security-audit.md", "w") as f:
            f.write(report)

        # Return appropriate exit code
        if result.severity_stats.critical > 0:
            return 2
        elif result.severity_stats.high > 0:
            return 1
        else:
            return 0
```

### Caching Results

```python
import pickle
from pathlib import Path

async def analyze_with_cache(package_file: str, cache_file: str = "cache.pkl"):
    """Analyze with result caching."""
    cache_path = Path(cache_file)

    # Check cache
    if cache_path.exists():
        with open(cache_path, "rb") as f:
            cached_result = pickle.load(f)

        # Check if cache is recent (less than 24 hours old)
        age = datetime.now() - cached_result.analysis_date
        if age.total_seconds() < 86400:
            print("Using cached results")
            return cached_result

    # Perform fresh analysis
    manifest = PackageParser.auto_detect_and_parse(package_file)

    async with NVDClient(api_key="your-key") as nvd_client:
        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=["CRITICAL", "HIGH"]
        )

        result = await analyzer.analyze_manifest(manifest)

    # Cache results
    with open(cache_path, "wb") as f:
        pickle.dump(result, f)

    return result
```

## Error Handling

```python
async def safe_audit(file_path: str):
    """Audit with comprehensive error handling."""
    try:
        # Parse file
        try:
            manifest = PackageParser.auto_detect_and_parse(file_path)
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
            return None
        except ValueError as e:
            print(f"Error: Unsupported file format: {e}")
            return None

        # Analyze
        async with NVDClient(api_key="your-key") as nvd_client:
            analyzer = VulnerabilityAnalyzer(
                nvd_client=nvd_client,
                severity_filter=["CRITICAL", "HIGH"]
            )

            try:
                result = await analyzer.analyze_manifest(manifest)
                return result
            except Exception as e:
                print(f"Error during analysis: {e}")
                return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## Best Practices

1. **Always use async context managers** for NVDClient to ensure proper cleanup
2. **Respect rate limits** - use an API key for larger projects
3. **Cache results** when appropriate to avoid redundant API calls
4. **Filter by severity** to focus on actionable vulnerabilities
5. **Handle errors gracefully** - network issues and API errors can occur
6. **Use appropriate timeouts** for API requests
7. **Save reports** for documentation and compliance purposes

## Next Steps

- Explore the [CLI documentation](../README.md#usage)
- Review the [Quick Start Guide](QUICKSTART.md)
- Check out the [example files](examples/)
