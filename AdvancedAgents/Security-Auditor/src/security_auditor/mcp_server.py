"""MCP Server implementation for Security Auditor."""

import json
import os
from pathlib import Path
from typing import Any, Optional, List, Dict

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl

from .analyzer import VulnerabilityAnalyzer
from .nvd_client import NVDClient
from .package_parser import PackageParser
from .report import ExecutiveSummaryGenerator

# Load environment variables
load_dotenv()


class SecurityAuditorMCP:
    """MCP Server for Security Auditor."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("security-auditor")
        self.nvd_client: Optional[NVDClient] = None

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="audit_package_file",
                    description=(
                        "Audit a package manifest file (package.json, requirements.txt) "
                        "for known CVE vulnerabilities. Returns an executive summary "
                        "focused on CRITICAL and HIGH severity issues."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the package manifest file"
                            },
                            "severity_filter": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
                                },
                                "description": "Severities to include (default: CRITICAL, HIGH)",
                                "default": ["CRITICAL", "HIGH"]
                            },
                            "include_dev_dependencies": {
                                "type": "boolean",
                                "description": "Include development dependencies",
                                "default": False
                            },
                            "days_back": {
                                "type": "integer",
                                "description": "Only consider CVEs published in last N days (optional)",
                            },
                            "format": {
                                "type": "string",
                                "enum": ["text", "markdown", "json"],
                                "description": "Output format for the summary",
                                "default": "text"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="search_cve",
                    description=(
                        "Search for specific CVE vulnerabilities by ID, keyword, or product. "
                        "Returns detailed CVE information from the NVD database."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cve_id": {
                                "type": "string",
                                "description": "Specific CVE ID (e.g., CVE-2024-1234)"
                            },
                            "keyword": {
                                "type": "string",
                                "description": "Search keyword in CVE descriptions"
                            },
                            "product": {
                                "type": "string",
                                "description": "Product name to search for"
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                                "description": "Filter by CVSS v3 severity"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10
                            }
                        }
                    }
                ),
                Tool(
                    name="get_vulnerability_stats",
                    description=(
                        "Get statistics about vulnerabilities for a package file. "
                        "Returns counts by severity without detailed listings."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the package manifest file"
                            }
                        },
                        "required": ["file_path"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "audit_package_file":
                    return await self._audit_package_file(arguments)
                elif name == "search_cve":
                    return await self._search_cve(arguments)
                elif name == "get_vulnerability_stats":
                    return await self._get_vulnerability_stats(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def _get_nvd_client(self) -> NVDClient:
        """Get or create NVD client instance."""
        if self.nvd_client is None:
            api_key = os.getenv("NVD_API_KEY")
            rate_limit = int(os.getenv("NVD_RATE_LIMIT", "50" if api_key else "5"))

            self.nvd_client = NVDClient(
                api_key=api_key,
                rate_limit=rate_limit
            )

        return self.nvd_client

    async def _audit_package_file(self, arguments: dict) -> List[TextContent]:
        """Audit a package file for vulnerabilities."""
        file_path = arguments["file_path"]
        severity_filter = arguments.get("severity_filter", ["CRITICAL", "HIGH"])
        include_dev = arguments.get("include_dev_dependencies", False)
        days_back = arguments.get("days_back")
        output_format = arguments.get("format", "text")

        # Parse the package file
        try:
            manifest = PackageParser.auto_detect_and_parse(file_path)
        except FileNotFoundError:
            return [TextContent(
                type="text",
                text=f"File not found: {file_path}"
            )]
        except ValueError as e:
            return [TextContent(
                type="text",
                text=f"Error parsing file: {e}"
            )]

        # Initialize NVD client and analyzer
        nvd_client = await self._get_nvd_client()
        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=severity_filter,
            include_dev_dependencies=include_dev
        )

        # Perform analysis
        result = await analyzer.analyze_manifest(manifest, days_back=days_back)

        # Generate summary in requested format
        if output_format == "json":
            summary = ExecutiveSummaryGenerator.generate_json_summary(result)
            text = json.dumps(summary, indent=2)
        elif output_format == "markdown":
            text = ExecutiveSummaryGenerator.generate_markdown_summary(result)
        else:
            text = ExecutiveSummaryGenerator.generate_text_summary(result)

        return [TextContent(type="text", text=text)]

    async def _search_cve(self, arguments: dict) -> List[TextContent]:
        """Search for CVE information."""
        cve_id = arguments.get("cve_id")
        keyword = arguments.get("keyword")
        product = arguments.get("product")
        severity = arguments.get("severity")
        limit = arguments.get("limit", 10)

        nvd_client = await self._get_nvd_client()

        # Perform search
        cves = await nvd_client.search_cves(
            cve_id=cve_id,
            keyword=keyword or product,
            cvss_v3_severity=severity,
            results_per_page=limit
        )

        if not cves:
            return [TextContent(
                type="text",
                text="No CVEs found matching the search criteria."
            )]

        # Format results
        lines = [f"Found {len(cves)} CVE(s):\n"]

        for cve in cves:
            lines.append(f"\n{'='*80}")
            lines.append(f"CVE ID: {cve.cve_id}")
            lines.append(f"Severity: {cve.severity}")
            if cve.score:
                lines.append(f"CVSS Score: {cve.score}")
            lines.append(f"Published: {cve.published_date.strftime('%Y-%m-%d')}")
            lines.append(f"\nDescription:")
            lines.append(cve.description)

            if cve.references:
                lines.append(f"\nReferences:")
                for ref in cve.references[:3]:
                    lines.append(f"  - {ref}")
                if len(cve.references) > 3:
                    lines.append(f"  ... and {len(cve.references) - 3} more")

        return [TextContent(type="text", text="\n".join(lines))]

    async def _get_vulnerability_stats(self, arguments: dict) -> List[TextContent]:
        """Get vulnerability statistics for a package file."""
        file_path = arguments["file_path"]

        # Parse the package file
        try:
            manifest = PackageParser.auto_detect_and_parse(file_path)
        except FileNotFoundError:
            return [TextContent(
                type="text",
                text=f"File not found: {file_path}"
            )]
        except ValueError as e:
            return [TextContent(
                type="text",
                text=f"Error parsing file: {e}"
            )]

        # Initialize analyzer
        nvd_client = await self._get_nvd_client()
        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        )

        # Perform analysis
        result = await analyzer.analyze_manifest(manifest)

        # Generate stats summary
        stats = {
            "packages_analyzed": result.packages_analyzed,
            "packages_with_vulnerabilities": result.packages_with_vulnerabilities,
            "total_vulnerabilities": result.severity_stats.total,
            "severity_breakdown": {
                "critical": result.severity_stats.critical,
                "high": result.severity_stats.high,
                "medium": result.severity_stats.medium,
                "low": result.severity_stats.low
            }
        }

        return [TextContent(
            type="text",
            text=json.dumps(stats, indent=2)
        )]

    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

    async def cleanup(self):
        """Cleanup resources."""
        if self.nvd_client:
            await self.nvd_client.close()


async def main():
    """Main entry point for the MCP server."""
    server = SecurityAuditorMCP()
    try:
        await server.run()
    finally:
        await server.cleanup()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
