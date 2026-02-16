"""Executive summary and report generation."""

from datetime import datetime
from typing import Optional, List, Dict

from .analyzer import AnalysisResult, VulnerabilityMatch


class ExecutiveSummaryGenerator:
    """Generates executive summaries from vulnerability analysis results."""

    @staticmethod
    def generate_text_summary(
        result: AnalysisResult,
        include_details: bool = True
    ) -> str:
        """
        Generate a text-based executive summary.

        Args:
            result: Analysis result to summarize
            include_details: Whether to include detailed vulnerability listings

        Returns:
            Formatted text summary
        """
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("SECURITY AUDIT EXECUTIVE SUMMARY")
        lines.append("=" * 80)
        lines.append("")

        # Analysis metadata
        lines.append(f"Analysis Date: {result.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        if result.manifest.name:
            lines.append(f"Project: {result.manifest.name} v{result.manifest.version or 'unknown'}")
        lines.append("")

        # Overview
        lines.append("OVERVIEW")
        lines.append("-" * 80)
        lines.append(f"Packages Analyzed: {result.packages_analyzed}")
        lines.append(f"Packages with Vulnerabilities: {result.packages_with_vulnerabilities}")
        lines.append(f"Total Vulnerabilities Found: {result.severity_stats.total}")
        lines.append("")

        # Severity breakdown
        lines.append("SEVERITY BREAKDOWN")
        lines.append("-" * 80)
        lines.append(f"  CRITICAL: {result.severity_stats.critical}")
        lines.append(f"  HIGH:     {result.severity_stats.high}")
        lines.append(f"  MEDIUM:   {result.severity_stats.medium}")
        lines.append(f"  LOW:      {result.severity_stats.low}")
        if result.severity_stats.unknown > 0:
            lines.append(f"  UNKNOWN:  {result.severity_stats.unknown}")
        lines.append("")

        # Risk assessment
        lines.append("RISK ASSESSMENT")
        lines.append("-" * 80)

        actionable = result.severity_stats.actionable
        if actionable == 0:
            lines.append("✓ No critical or high severity vulnerabilities found.")
            lines.append("  Risk Level: LOW")
        elif actionable <= 5:
            lines.append("⚠ Limited critical/high severity vulnerabilities detected.")
            lines.append("  Risk Level: MEDIUM")
            lines.append(f"  Immediate Action Required: {actionable} vulnerabilities")
        else:
            lines.append("✗ SIGNIFICANT security vulnerabilities detected!")
            lines.append("  Risk Level: HIGH")
            lines.append(f"  Immediate Action Required: {actionable} vulnerabilities")

        lines.append("")

        # Recent vulnerabilities
        recent = result.get_recent_vulnerabilities(days=30)
        if recent:
            lines.append("RECENTLY DISCLOSED VULNERABILITIES (Last 30 Days)")
            lines.append("-" * 80)
            lines.append(f"  {len(recent)} vulnerabilities were published in the last 30 days")
            lines.append("")

        # Actionable items
        if include_details and actionable > 0:
            lines.append("ACTIONABLE VULNERABILITIES (CRITICAL & HIGH)")
            lines.append("-" * 80)
            lines.append("")

            actionable_vulns = result.get_actionable_vulnerabilities()

            # Group by package
            by_package = result.get_vulnerabilities_by_package()

            for pkg_name, vulns in sorted(by_package.items()):
                # Only show actionable vulnerabilities
                pkg_actionable = [
                    v for v in vulns
                    if v.cve.severity in ["CRITICAL", "HIGH"]
                ]

                if not pkg_actionable:
                    continue

                lines.append(f"Package: {pkg_name}")
                lines.append(f"  Vulnerabilities: {len(pkg_actionable)}")
                lines.append("")

                for vuln in pkg_actionable[:3]:  # Limit to top 3 per package
                    lines.append(f"  • {vuln.cve.cve_id} [{vuln.cve.severity}]")
                    if vuln.cve.score:
                        lines.append(f"    CVSS Score: {vuln.cve.score}")
                    lines.append(f"    Published: {vuln.cve.published_date.strftime('%Y-%m-%d')}")

                    # Truncate description
                    desc = vuln.cve.description
                    if len(desc) > 200:
                        desc = desc[:200] + "..."
                    lines.append(f"    {desc}")
                    lines.append("")

                if len(pkg_actionable) > 3:
                    lines.append(f"  ... and {len(pkg_actionable) - 3} more vulnerabilities")
                    lines.append("")

        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)

        if actionable > 0:
            lines.append("1. IMMEDIATE: Review and patch all CRITICAL and HIGH severity vulnerabilities")
            lines.append("2. Update affected packages to latest secure versions")
            lines.append("3. Implement automated dependency scanning in CI/CD pipeline")
            lines.append("4. Schedule regular security audits (weekly/monthly)")
        else:
            lines.append("1. Continue monitoring for new vulnerabilities")
            lines.append("2. Keep dependencies up to date")
            lines.append("3. Maintain automated security scanning")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    @staticmethod
    def generate_json_summary(result: AnalysisResult) -> dict:
        """
        Generate a JSON-serializable summary.

        Args:
            result: Analysis result to summarize

        Returns:
            Dictionary containing summary data
        """
        actionable_vulns = result.get_actionable_vulnerabilities()

        return {
            "analysis_date": result.analysis_date.isoformat(),
            "project": {
                "name": result.manifest.name,
                "version": result.manifest.version
            },
            "summary": {
                "packages_analyzed": result.packages_analyzed,
                "packages_with_vulnerabilities": result.packages_with_vulnerabilities,
                "total_vulnerabilities": result.severity_stats.total,
                "actionable_vulnerabilities": result.severity_stats.actionable
            },
            "severity_breakdown": {
                "critical": result.severity_stats.critical,
                "high": result.severity_stats.high,
                "medium": result.severity_stats.medium,
                "low": result.severity_stats.low,
                "unknown": result.severity_stats.unknown
            },
            "risk_level": ExecutiveSummaryGenerator._calculate_risk_level(result),
            "actionable_vulnerabilities": [
                {
                    "package": vuln.dependency.name,
                    "version": vuln.dependency.version,
                    "cve_id": vuln.cve.cve_id,
                    "severity": vuln.cve.severity,
                    "score": vuln.cve.score,
                    "published_date": vuln.cve.published_date.isoformat(),
                    "description": vuln.cve.description,
                    "references": vuln.cve.references
                }
                for vuln in actionable_vulns
            ],
            "recent_vulnerabilities_count": len(result.get_recent_vulnerabilities(30))
        }

    @staticmethod
    def generate_markdown_summary(result: AnalysisResult) -> str:
        """
        Generate a Markdown-formatted summary.

        Args:
            result: Analysis result to summarize

        Returns:
            Markdown-formatted summary
        """
        lines = []

        # Header
        lines.append("# Security Audit Executive Summary")
        lines.append("")
        lines.append(f"**Analysis Date:** {result.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        if result.manifest.name:
            lines.append(f"**Project:** {result.manifest.name} v{result.manifest.version or 'unknown'}")
        lines.append("")

        # Overview
        lines.append("## Overview")
        lines.append("")
        lines.append(f"- **Packages Analyzed:** {result.packages_analyzed}")
        lines.append(f"- **Packages with Vulnerabilities:** {result.packages_with_vulnerabilities}")
        lines.append(f"- **Total Vulnerabilities:** {result.severity_stats.total}")
        lines.append("")

        # Severity breakdown
        lines.append("## Severity Breakdown")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        lines.append(f"| CRITICAL | {result.severity_stats.critical} |")
        lines.append(f"| HIGH     | {result.severity_stats.high} |")
        lines.append(f"| MEDIUM   | {result.severity_stats.medium} |")
        lines.append(f"| LOW      | {result.severity_stats.low} |")
        lines.append("")

        # Risk assessment
        lines.append("## Risk Assessment")
        lines.append("")
        risk_level = ExecutiveSummaryGenerator._calculate_risk_level(result)
        actionable = result.severity_stats.actionable

        if risk_level == "LOW":
            lines.append("✓ **Risk Level: LOW**")
            lines.append("")
            lines.append("No critical or high severity vulnerabilities found.")
        elif risk_level == "MEDIUM":
            lines.append("⚠️ **Risk Level: MEDIUM**")
            lines.append("")
            lines.append(f"Limited critical/high severity vulnerabilities detected: {actionable}")
        else:
            lines.append("❌ **Risk Level: HIGH**")
            lines.append("")
            lines.append(f"SIGNIFICANT security vulnerabilities detected: {actionable}")

        lines.append("")

        # Actionable vulnerabilities
        if actionable > 0:
            lines.append("## Actionable Vulnerabilities (Critical & High)")
            lines.append("")

            by_package = result.get_vulnerabilities_by_package()

            for pkg_name, vulns in sorted(by_package.items()):
                pkg_actionable = [
                    v for v in vulns
                    if v.cve.severity in ["CRITICAL", "HIGH"]
                ]

                if not pkg_actionable:
                    continue

                lines.append(f"### {pkg_name}")
                lines.append("")

                for vuln in pkg_actionable[:5]:
                    lines.append(f"#### {vuln.cve.cve_id} [{vuln.cve.severity}]")
                    if vuln.cve.score:
                        lines.append(f"- **CVSS Score:** {vuln.cve.score}")
                    lines.append(f"- **Published:** {vuln.cve.published_date.strftime('%Y-%m-%d')}")
                    lines.append(f"- **Description:** {vuln.cve.description}")
                    lines.append("")

        # Recommendations
        lines.append("## Recommendations")
        lines.append("")

        if actionable > 0:
            lines.append("1. **IMMEDIATE:** Review and patch all CRITICAL and HIGH severity vulnerabilities")
            lines.append("2. Update affected packages to latest secure versions")
            lines.append("3. Implement automated dependency scanning in CI/CD pipeline")
            lines.append("4. Schedule regular security audits")
        else:
            lines.append("1. Continue monitoring for new vulnerabilities")
            lines.append("2. Keep dependencies up to date")
            lines.append("3. Maintain automated security scanning")

        return "\n".join(lines)

    @staticmethod
    def _calculate_risk_level(result: AnalysisResult) -> str:
        """Calculate overall risk level based on vulnerabilities found."""
        actionable = result.severity_stats.actionable

        if actionable == 0:
            return "LOW"
        elif actionable <= 5:
            return "MEDIUM"
        else:
            return "HIGH"
