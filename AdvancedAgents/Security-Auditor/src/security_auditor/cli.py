"""Command-line interface for Security Auditor."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .analyzer import VulnerabilityAnalyzer
from .nvd_client import NVDClient
from .package_parser import PackageParser
from .report import ExecutiveSummaryGenerator


async def audit_command(args):
    """Execute the audit command."""
    # Load environment variables
    load_dotenv()

    # Initialize NVD client
    api_key = os.getenv("NVD_API_KEY")
    rate_limit = int(os.getenv("NVD_RATE_LIMIT", "50" if api_key else "5"))

    print(f"Initializing NVD client (rate limit: {rate_limit} requests/30s)...")

    async with NVDClient(api_key=api_key, rate_limit=rate_limit) as nvd_client:
        # Parse package file
        print(f"Parsing package file: {args.file}")
        try:
            manifest = PackageParser.auto_detect_and_parse(args.file)
            print(f"Found {manifest.total_count} dependencies")
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        # Initialize analyzer
        severity_filter = args.severity or ["CRITICAL", "HIGH"]
        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=severity_filter,
            include_dev_dependencies=args.include_dev
        )

        # Perform analysis
        print("\nAnalyzing dependencies for vulnerabilities...")
        print("This may take a while depending on the number of packages...\n")

        result = await analyzer.analyze_manifest(manifest, days_back=args.days)

        # Generate report
        if args.format == "json":
            summary = ExecutiveSummaryGenerator.generate_json_summary(result)
            import json
            output = json.dumps(summary, indent=2)
        elif args.format == "markdown":
            output = ExecutiveSummaryGenerator.generate_markdown_summary(result)
        else:
            output = ExecutiveSummaryGenerator.generate_text_summary(result)

        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output)
            print(f"\nReport saved to: {args.output}")
        else:
            print(output)

        # Return exit code based on findings
        if result.severity_stats.critical > 0:
            return 2  # Critical vulnerabilities found
        elif result.severity_stats.high > 0:
            return 1  # High vulnerabilities found
        else:
            return 0  # No critical/high vulnerabilities


async def search_command(args):
    """Execute the search command."""
    load_dotenv()

    api_key = os.getenv("NVD_API_KEY")
    rate_limit = int(os.getenv("NVD_RATE_LIMIT", "50" if api_key else "5"))

    async with NVDClient(api_key=api_key, rate_limit=rate_limit) as nvd_client:
        print("Searching NVD database...")

        cves = await nvd_client.search_cves(
            cve_id=args.cve_id,
            keyword=args.keyword,
            cvss_v3_severity=args.severity,
            results_per_page=args.limit
        )

        if not cves:
            print("No CVEs found matching the search criteria.")
            return 0

        print(f"\nFound {len(cves)} CVE(s):\n")

        for cve in cves:
            print("=" * 80)
            print(f"CVE ID: {cve.cve_id}")
            print(f"Severity: {cve.severity}")
            if cve.score:
                print(f"CVSS Score: {cve.score}")
            print(f"Published: {cve.published_date.strftime('%Y-%m-%d')}")
            print(f"\nDescription:")
            print(cve.description)

            if cve.references:
                print(f"\nReferences:")
                for ref in cve.references[:3]:
                    print(f"  - {ref}")
                if len(cve.references) > 3:
                    print(f"  ... and {len(cve.references) - 3} more")
            print()

        return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Security Auditor - CVE Intelligence Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Audit command
    audit_parser = subparsers.add_parser(
        "audit",
        help="Audit a package file for vulnerabilities"
    )
    audit_parser.add_argument(
        "file",
        help="Path to package manifest file (package.json, requirements.txt)"
    )
    audit_parser.add_argument(
        "--severity",
        nargs="+",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        help="Filter by severity levels (default: CRITICAL HIGH)"
    )
    audit_parser.add_argument(
        "--include-dev",
        action="store_true",
        help="Include development dependencies"
    )
    audit_parser.add_argument(
        "--days",
        type=int,
        help="Only consider CVEs published in last N days"
    )
    audit_parser.add_argument(
        "--format",
        choices=["text", "markdown", "json"],
        default="text",
        help="Output format (default: text)"
    )
    audit_parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)"
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search for CVE information"
    )
    search_parser.add_argument(
        "--cve-id",
        help="Specific CVE ID (e.g., CVE-2024-1234)"
    )
    search_parser.add_argument(
        "--keyword",
        help="Search keyword"
    )
    search_parser.add_argument(
        "--severity",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        help="Filter by severity"
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Run the appropriate command
    if args.command == "audit":
        return asyncio.run(audit_command(args))
    elif args.command == "search":
        return asyncio.run(search_command(args))


if __name__ == "__main__":
    sys.exit(main())
