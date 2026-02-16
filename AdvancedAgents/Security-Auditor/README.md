# Security Auditor (CVE Intelligence)

A powerful security auditing tool that analyzes your software dependencies for known CVE vulnerabilities using the NIST National Vulnerability Database (NVD) API. Built with Python and MCP (Model Context Protocol) integration.

## Features

- **Comprehensive CVE Scanning**: Query the official NIST NVD API for real-time vulnerability data
- **Multi-Language Support**: Analyze package.json (Node.js) and requirements.txt (Python) files
- **Intelligent Filtering**: Focus on CRITICAL and HIGH severity vulnerabilities that matter
- **Executive Summaries**: Generate actionable reports for technical and non-technical audiences
- **MCP Integration**: Expose security auditing capabilities through the Model Context Protocol
- **CLI Tool**: Command-line interface for manual audits and CI/CD integration
- **Multiple Output Formats**: Text, Markdown, and JSON report formats

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Security-Auditor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your NVD API key
```

### Getting an NVD API Key

1. Visit [https://nvd.nist.gov/developers/request-an-api-key](https://nvd.nist.gov/developers/request-an-api-key)
2. Request an API key (free)
3. Add the key to your `.env` file

**Rate Limits:**
- Without API key: 5 requests per 30 seconds
- With API key: 50 requests per 30 seconds

## Usage

### CLI Tool

#### Audit a Package File

```bash
python -m security_auditor.cli audit examples/package.json
```

**Options:**
- `--severity CRITICAL HIGH MEDIUM LOW`: Filter by severity levels
- `--include-dev`: Include development dependencies
- `--days N`: Only consider CVEs published in the last N days
- `--format text|markdown|json`: Output format
- `--output FILE`: Save report to file

**Examples:**

```bash
# Audit with CRITICAL and HIGH vulnerabilities only
python -m security_auditor.cli audit examples/package.json --severity CRITICAL HIGH

# Include all severities
python -m security_auditor.cli audit examples/package.json --severity CRITICAL HIGH MEDIUM LOW

# Generate markdown report
python -m security_auditor.cli audit examples/package.json --format markdown -o report.md

# Check for recent vulnerabilities (last 30 days)
python -m security_auditor.cli audit examples/package.json --days 30

# Include dev dependencies
python -m security_auditor.cli audit examples/package.json --include-dev
```

#### Search for CVEs

```bash
# Search by CVE ID
python -m security_auditor.cli search --cve-id CVE-2024-1234

# Search by keyword
python -m security_auditor.cli search --keyword "nodejs" --severity CRITICAL --limit 5

# Search for specific product vulnerabilities
python -m security_auditor.cli search --keyword "express framework" --limit 10
```

### MCP Server

The Security Auditor can be run as an MCP server, exposing tools for AI assistants to use:

```bash
python -m security_auditor.mcp_server
```

#### Available MCP Tools

1. **audit_package_file**: Audit a package manifest for vulnerabilities
   - Parameters: file_path, severity_filter, include_dev_dependencies, days_back, format
   - Returns: Executive summary report

2. **search_cve**: Search for specific CVEs
   - Parameters: cve_id, keyword, product, severity, limit
   - Returns: Detailed CVE information

3. **get_vulnerability_stats**: Get vulnerability statistics
   - Parameters: file_path
   - Returns: Summary statistics in JSON format

### Python API

```python
import asyncio
from security_auditor.nvd_client import NVDClient
from security_auditor.package_parser import PackageParser
from security_auditor.analyzer import VulnerabilityAnalyzer
from security_auditor.report import ExecutiveSummaryGenerator

async def audit_project():
    # Parse package file
    manifest = PackageParser.parse_package_json("package.json")

    # Initialize NVD client
    async with NVDClient(api_key="your-api-key") as nvd_client:
        # Create analyzer
        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=["CRITICAL", "HIGH"]
        )

        # Analyze dependencies
        result = await analyzer.analyze_manifest(manifest)

        # Generate report
        report = ExecutiveSummaryGenerator.generate_text_summary(result)
        print(report)

asyncio.run(audit_project())
```

## Project Structure

```
Security-Auditor/
├── src/
│   └── security_auditor/
│       ├── __init__.py
│       ├── nvd_client.py         # NVD API client
│       ├── package_parser.py     # Package manifest parser
│       ├── analyzer.py           # Vulnerability analyzer
│       ├── report.py             # Report generation
│       ├── mcp_server.py         # MCP server implementation
│       └── cli.py                # Command-line interface
├── examples/
│   ├── package.json              # Example Node.js dependencies
│   └── requirements.txt          # Example Python dependencies
├── pyproject.toml                # Project configuration
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

## Architecture

### Components

1. **NVD Client** ([nvd_client.py](src/security_auditor/nvd_client.py))
   - Handles communication with NIST NVD API
   - Implements rate limiting
   - Parses CVE data and CVSS metrics

2. **Package Parser** ([package_parser.py](src/security_auditor/package_parser.py))
   - Supports package.json and requirements.txt
   - Normalizes version strings
   - Extracts vendor and product information

3. **Vulnerability Analyzer** ([analyzer.py](src/security_auditor/analyzer.py))
   - Matches dependencies to CVEs
   - Filters by severity
   - Generates statistics

4. **Report Generator** ([report.py](src/security_auditor/report.py))
   - Creates executive summaries
   - Supports multiple output formats
   - Focuses on actionable insights

5. **MCP Server** ([mcp_server.py](src/security_auditor/mcp_server.py))
   - Exposes security auditing via MCP protocol
   - Provides tools for AI assistants
   - Handles async operations

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# NVD API Configuration
NVD_API_KEY=your_api_key_here

# Rate limiting (requests per 30 seconds)
NVD_RATE_LIMIT=50
```

### Severity Levels

- **CRITICAL**: Immediate action required
- **HIGH**: Should be addressed soon
- **MEDIUM**: Address in regular maintenance
- **LOW**: Informational

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Security Audit

on: [push, pull_request]

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install Security Auditor
        run: |
          pip install -r requirements.txt

      - name: Run Security Audit
        env:
          NVD_API_KEY: ${{ secrets.NVD_API_KEY }}
        run: |
          python -m security_auditor.cli audit package.json --format json -o audit.json

      - name: Upload Audit Report
        uses: actions/upload-artifact@v2
        with:
          name: security-audit
          path: audit.json
```

## Exit Codes

When running the CLI audit command:

- `0`: No critical or high severity vulnerabilities found
- `1`: High severity vulnerabilities found
- `2`: Critical severity vulnerabilities found

## Limitations

- **Version Matching**: The tool uses keyword matching to associate CVEs with packages. More sophisticated CPE (Common Platform Enumeration) matching would improve accuracy.
- **Rate Limiting**: NVD API has rate limits. Large projects may take time to audit.
- **False Positives**: Some CVEs may be matched incorrectly due to keyword matching.
- **Coverage**: Only scans known CVEs in the NVD database.

## Future Enhancements

- [ ] Advanced CPE version range matching
- [ ] Support for more package managers (Gemfile, Cargo.toml, go.mod)
- [ ] Caching layer for faster repeated scans
- [ ] Integration with GitHub Security Advisories
- [ ] Automated fix suggestions
- [ ] Vulnerability trending and analytics
- [ ] Web dashboard interface

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is for educational and security assessment purposes.

## Resources

- [NIST NVD API Documentation](https://nvd.nist.gov/developers/vulnerabilities)
- [CVSS Scoring Guide](https://nvd.nist.gov/vuln-metrics/cvss)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

## Acknowledgments

- NIST National Vulnerability Database for providing the CVE data API
- The open-source security community for vulnerability research and disclosure
