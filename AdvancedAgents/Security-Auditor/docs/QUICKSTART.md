# Quick Start Guide

Get started with Security Auditor in 5 minutes!

## Step 1: Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure API Key (Optional but Recommended)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your NVD API key
# Get your free API key from: https://nvd.nist.gov/developers/request-an-api-key
```

Without an API key, you're limited to 5 requests per 30 seconds.
With an API key, you get 50 requests per 30 seconds.

## Step 3: Run Your First Audit

```bash
# Audit the example package.json file
python -m security_auditor.cli audit examples/package.json
```

You should see output like:

```
================================================================================
SECURITY AUDIT EXECUTIVE SUMMARY
================================================================================

Analysis Date: 2024-12-10 14:30:00
Project: example-app v1.0.0

OVERVIEW
--------------------------------------------------------------------------------
Packages Analyzed: 6
Packages with Vulnerabilities: 3
Total Vulnerabilities Found: 12

SEVERITY BREAKDOWN
--------------------------------------------------------------------------------
  CRITICAL: 2
  HIGH:     5
  MEDIUM:   3
  LOW:      2
...
```

## Step 4: Try Different Options

### Filter by Severity

```bash
# Only show CRITICAL vulnerabilities
python -m security_auditor.cli audit examples/package.json --severity CRITICAL
```

### Generate Markdown Report

```bash
# Create a markdown report
python -m security_auditor.cli audit examples/package.json --format markdown -o security-report.md
```

### Check Recent Vulnerabilities

```bash
# Only show CVEs published in the last 30 days
python -m security_auditor.cli audit examples/package.json --days 30
```

### Include Dev Dependencies

```bash
# Include development dependencies in the audit
python -m security_auditor.cli audit examples/package.json --include-dev
```

## Step 5: Audit Your Own Project

```bash
# Audit your package.json
python -m security_auditor.cli audit /path/to/your/package.json

# Or audit your requirements.txt
python -m security_auditor.cli audit /path/to/your/requirements.txt
```

## Using as MCP Server

To run as an MCP server for integration with AI assistants:

```bash
python -m security_auditor.mcp_server
```

The MCP server exposes three tools:
1. `audit_package_file` - Audit dependencies for vulnerabilities
2. `search_cve` - Search for specific CVE information
3. `get_vulnerability_stats` - Get vulnerability statistics

## Searching for Specific CVEs

```bash
# Search for a specific CVE
python -m security_auditor.cli search --cve-id CVE-2024-1234

# Search by keyword
python -m security_auditor.cli search --keyword "nodejs" --severity CRITICAL

# Limit results
python -m security_auditor.cli search --keyword "express" --limit 5
```

## Exit Codes

The CLI returns different exit codes based on findings:
- `0`: No critical or high vulnerabilities
- `1`: High severity vulnerabilities found
- `2`: Critical severity vulnerabilities found

This makes it easy to integrate into CI/CD pipelines:

```bash
# Exit with error if critical/high vulnerabilities are found
python -m security_auditor.cli audit package.json || echo "Security issues detected!"
```

## Next Steps

- Read the full [README.md](../README.md) for detailed documentation
- Integrate into your CI/CD pipeline
- Explore the Python API for custom integrations
- Set up automated weekly security scans

## Troubleshooting

### Rate Limit Errors

If you see rate limit errors:
1. Get an NVD API key (free)
2. Add it to your `.env` file
3. This increases your limit from 5 to 50 requests per 30 seconds

### File Not Found

Make sure you're providing the correct path to your package file:
```bash
# Use absolute path if needed
python -m security_auditor.cli audit /absolute/path/to/package.json
```

### Module Not Found

Make sure you've installed the dependencies:
```bash
pip install -r requirements.txt
```

### No Vulnerabilities Found

This could mean:
1. Your dependencies are secure (great!)
2. The versions don't match NVD records exactly
3. The keyword matching didn't find related CVEs

Try broadening your search or checking individual packages manually.

## Getting Help

- Check the [README.md](../README.md) for detailed documentation
- Review the example files in the `examples/` directory
- Open an issue on GitHub for bugs or questions
