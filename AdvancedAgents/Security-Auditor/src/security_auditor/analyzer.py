"""Vulnerability analyzer and severity filtering."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from pydantic import BaseModel, Field

from .nvd_client import CVEData, NVDClient
from .package_parser import PackageDependency, PackageManifest


class VulnerabilityMatch(BaseModel):
    """Represents a vulnerability matched to a package dependency."""

    dependency: PackageDependency
    cve: CVEData
    confidence: str = "medium"  # low, medium, high


class SeverityStats(BaseModel):
    """Statistics for vulnerabilities by severity."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    unknown: int = 0

    @property
    def total(self) -> int:
        """Total number of vulnerabilities."""
        return self.critical + self.high + self.medium + self.low + self.unknown

    @property
    def actionable(self) -> int:
        """Number of actionable (CRITICAL and HIGH) vulnerabilities."""
        return self.critical + self.high


class AnalysisResult(BaseModel):
    """Result of vulnerability analysis."""

    manifest: PackageManifest
    vulnerabilities: List[VulnerabilityMatch] = Field(default_factory=list)
    severity_stats: SeverityStats = Field(default_factory=SeverityStats)
    analysis_date: datetime = Field(default_factory=datetime.now)
    packages_analyzed: int = 0
    packages_with_vulnerabilities: int = 0

    def get_critical_vulnerabilities(self) -> List[VulnerabilityMatch]:
        """Get all CRITICAL severity vulnerabilities."""
        return [
            v for v in self.vulnerabilities
            if v.cve.severity == "CRITICAL"
        ]

    def get_high_vulnerabilities(self) -> List[VulnerabilityMatch]:
        """Get all HIGH severity vulnerabilities."""
        return [
            v for v in self.vulnerabilities
            if v.cve.severity == "HIGH"
        ]

    def get_actionable_vulnerabilities(self) -> List[VulnerabilityMatch]:
        """Get CRITICAL and HIGH severity vulnerabilities."""
        return [
            v for v in self.vulnerabilities
            if v.cve.severity in ["CRITICAL", "HIGH"]
        ]

    def get_vulnerabilities_by_package(self) -> Dict[str, List[VulnerabilityMatch]]:
        """Group vulnerabilities by package name."""
        grouped: Dict[str, List[VulnerabilityMatch]] = defaultdict(list)
        for vuln in self.vulnerabilities:
            grouped[vuln.dependency.name].append(vuln)
        return dict(grouped)

    def get_recent_vulnerabilities(self, days: int = 30) -> List[VulnerabilityMatch]:
        """Get vulnerabilities published in the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        return [
            v for v in self.vulnerabilities
            if v.cve.published_date.replace(tzinfo=None) >= cutoff
        ]


class VulnerabilityAnalyzer:
    """Analyzes package dependencies for known vulnerabilities."""

    def __init__(
        self,
        nvd_client: NVDClient,
        severity_filter: Optional[List[str]] = None,
        include_dev_dependencies: bool = False
    ):
        """
        Initialize the vulnerability analyzer.

        Args:
            nvd_client: NVD API client instance
            severity_filter: List of severities to include (e.g., ["CRITICAL", "HIGH"])
                           If None, all severities are included
            include_dev_dependencies: Whether to analyze dev dependencies
        """
        self.nvd_client = nvd_client
        self.severity_filter = severity_filter or ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        self.include_dev_dependencies = include_dev_dependencies

    async def analyze_manifest(
        self,
        manifest: PackageManifest,
        days_back: Optional[int] = None
    ) -> AnalysisResult:
        """
        Analyze a package manifest for vulnerabilities.

        Args:
            manifest: PackageManifest to analyze
            days_back: Only consider CVEs published in the last N days (optional)

        Returns:
            AnalysisResult with found vulnerabilities
        """
        result = AnalysisResult(
            manifest=manifest,
            packages_analyzed=0
        )

        # Filter dependencies based on settings
        dependencies_to_check = manifest.dependencies
        if not self.include_dev_dependencies:
            dependencies_to_check = [
                dep for dep in dependencies_to_check
                if dep.type != "dev"
            ]

        result.packages_analyzed = len(dependencies_to_check)

        # Track which packages have vulnerabilities
        packages_with_vulns = set()

        # Analyze each dependency
        for dependency in dependencies_to_check:
            vulnerabilities = await self._check_dependency(dependency, days_back)

            if vulnerabilities:
                packages_with_vulns.add(dependency.name)

            for cve in vulnerabilities:
                # Apply severity filter
                if cve.severity not in self.severity_filter:
                    continue

                # Create vulnerability match
                match = VulnerabilityMatch(
                    dependency=dependency,
                    cve=cve,
                    confidence="medium"
                )
                result.vulnerabilities.append(match)

                # Update severity stats
                severity = cve.severity.upper()
                if severity == "CRITICAL":
                    result.severity_stats.critical += 1
                elif severity == "HIGH":
                    result.severity_stats.high += 1
                elif severity == "MEDIUM":
                    result.severity_stats.medium += 1
                elif severity == "LOW":
                    result.severity_stats.low += 1
                else:
                    result.severity_stats.unknown += 1

        result.packages_with_vulnerabilities = len(packages_with_vulns)

        return result

    async def _check_dependency(
        self,
        dependency: PackageDependency,
        days_back: Optional[int] = None
    ) -> List[CVEData]:
        """
        Check a single dependency for vulnerabilities.

        Args:
            dependency: Package dependency to check
            days_back: Only consider CVEs published in the last N days

        Returns:
            List of CVE data for this dependency
        """
        vendor = dependency.get_vendor()
        product = dependency.get_product()
        version = dependency.clean_version()

        # Set date range if specified
        published_start = None
        if days_back:
            published_start = datetime.now() - timedelta(days=days_back)

        try:
            # Search for CVEs matching this package
            cves = await self.nvd_client.search_cves(
                keyword=f"{vendor} {product}",
                published_start=published_start
            )

            # Filter CVEs that might be relevant to this version
            # Note: This is a basic filter. More sophisticated version matching
            # would require parsing CPE strings and version comparisons
            relevant_cves = []
            for cve in cves:
                # Check if the version appears in the description or CPE matches
                if version and version != "*":
                    if version in cve.description or any(
                        version in cpe for cpe in cve.cpe_matches
                    ):
                        relevant_cves.append(cve)
                else:
                    # If no specific version, include all CVEs for the product
                    relevant_cves.append(cve)

            return relevant_cves

        except Exception as e:
            # Log error but continue with other dependencies
            print(f"Error checking {dependency.name}: {e}")
            return []

    async def analyze_dependency_list(
        self,
        dependencies: List[PackageDependency],
        days_back: Optional[int] = None
    ) -> AnalysisResult:
        """
        Analyze a list of dependencies for vulnerabilities.

        Args:
            dependencies: List of PackageDependency objects
            days_back: Only consider CVEs published in the last N days

        Returns:
            AnalysisResult with found vulnerabilities
        """
        manifest = PackageManifest(dependencies=dependencies)
        return await self.analyze_manifest(manifest, days_back)
