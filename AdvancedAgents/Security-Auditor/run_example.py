#!/usr/bin/env python
"""
Simple example script to demonstrate Security Auditor functionality.
Run this to test the installation and see the tool in action.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from src.security_auditor.nvd_client import NVDClient
from src.security_auditor.package_parser import PackageParser
from src.security_auditor.analyzer import VulnerabilityAnalyzer
from src.security_auditor.report import ExecutiveSummaryGenerator


async def main():
    """Run a simple security audit example."""
    print("=" * 80)
    print("Security Auditor - Example Run")
    print("=" * 80)
    print()

    # Load environment variables
    load_dotenv()
    api_key = os.getenv("NVD_API_KEY")

    if not api_key:
        print("⚠️  WARNING: No NVD_API_KEY found in .env file")
        print("   Running with limited rate limits (5 requests/30 seconds)")
        print("   Get a free API key from: https://nvd.nist.gov/developers/request-an-api-key")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting. Please add your API key to .env file.")
            return
        print()

    # Use example package.json
    example_file = Path("examples/package.json")

    if not example_file.exists():
        print(f"❌ Error: Example file not found: {example_file}")
        print("   Make sure you're running this from the project root directory.")
        return

    print(f"📦 Analyzing: {example_file}")
    print()

    # Parse the package file
    print("Step 1: Parsing package file...")
    manifest = PackageParser.parse_package_json(example_file)
    print(f"✓ Found {manifest.total_count} dependencies")
    print(f"  - Runtime: {len(manifest.runtime_dependencies)}")
    print(f"  - Dev: {len([d for d in manifest.dependencies if d.type == 'dev'])}")
    print()

    # Initialize NVD client
    print("Step 2: Initializing NVD client...")
    rate_limit = int(os.getenv("NVD_RATE_LIMIT", "50" if api_key else "5"))
    print(f"✓ Rate limit: {rate_limit} requests per 30 seconds")
    print()

    async with NVDClient(api_key=api_key, rate_limit=rate_limit) as nvd_client:
        # Create analyzer
        print("Step 3: Analyzing dependencies for vulnerabilities...")
        print("⏳ This may take a few minutes depending on the number of packages...")
        print()

        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=["CRITICAL", "HIGH"],
            include_dev_dependencies=False
        )

        # Perform analysis
        result = await analyzer.analyze_manifest(manifest)

        # Display quick stats
        print("✓ Analysis complete!")
        print()
        print("Quick Stats:")
        print(f"  - Packages analyzed: {result.packages_analyzed}")
        print(f"  - Packages with vulnerabilities: {result.packages_with_vulnerabilities}")
        print(f"  - Total vulnerabilities found: {result.severity_stats.total}")
        print(f"  - CRITICAL: {result.severity_stats.critical}")
        print(f"  - HIGH: {result.severity_stats.high}")
        print()

        # Generate report
        print("Step 4: Generating executive summary...")
        report = ExecutiveSummaryGenerator.generate_text_summary(
            result,
            include_details=True
        )

        print()
        print(report)

        # Save report
        output_file = Path("security-audit-example.txt")
        output_file.write_text(report)
        print()
        print(f"💾 Report saved to: {output_file}")

        # Also generate markdown version
        markdown_report = ExecutiveSummaryGenerator.generate_markdown_summary(result)
        markdown_file = Path("security-audit-example.md")
        markdown_file.write_text(markdown_report)
        print(f"💾 Markdown report saved to: {markdown_file}")

        print()
        print("=" * 80)
        print("Example completed successfully! 🎉")
        print()
        print("Next steps:")
        print("  1. Review the generated reports")
        print("  2. Try the CLI: python -m security_auditor.cli audit --help")
        print("  3. Read the QUICKSTART.md guide")
        print("  4. Check out API_GUIDE.md for Python API usage")
        print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("  1. Dependencies are installed: pip install -r requirements.txt")
        print("  2. You're in the project root directory")
        print("  3. The examples/package.json file exists")
