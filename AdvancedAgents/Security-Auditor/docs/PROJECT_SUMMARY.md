# Security Auditor - Project Summary

## Overview

Security Auditor is a comprehensive CVE intelligence tool built with Python that helps organizations triage and prioritize software vulnerabilities using the NIST National Vulnerability Database (NVD) API.

## Key Features

✅ **NVD API Integration** - Real-time access to official US government CVE data
✅ **Multi-Language Support** - Analyze package.json (Node.js) and requirements.txt (Python)
✅ **Intelligent Filtering** - Focus on CRITICAL and HIGH severity vulnerabilities
✅ **Executive Summaries** - Generate actionable reports for decision-makers
✅ **MCP Integration** - Model Context Protocol support for AI assistants
✅ **CLI Tool** - Command-line interface for manual audits and automation
✅ **Multiple Formats** - Text, Markdown, and JSON output formats
✅ **Rate Limiting** - Automatic rate limit handling (5 or 50 req/30s)

## Project Structure

```
Security-Auditor/
├── src/security_auditor/        # Main source code
│   ├── __init__.py              # Package initialization
│   ├── nvd_client.py            # NVD API client with rate limiting
│   ├── package_parser.py        # Parse package.json & requirements.txt
│   ├── analyzer.py              # Vulnerability analysis engine
│   ├── report.py                # Executive summary generation
│   ├── mcp_server.py            # MCP protocol implementation
│   └── cli.py                   # Command-line interface
│
├── examples/                    # Example package files
│   ├── package.json             # Sample Node.js dependencies
│   └── requirements.txt         # Sample Python dependencies
│
├── tests/                       # Unit tests
│   └── test_package_parser.py  # Parser tests
│
├── Documentation/
│   ├── README.md                # Main documentation
│   ├── QUICKSTART.md            # 5-minute quick start guide
│   ├── API_GUIDE.md             # Python API usage guide
│   ├── MCP_INTEGRATION.md       # MCP integration guide
│   └── PROJECT_SUMMARY.md       # This file
│
└── Configuration/
    ├── pyproject.toml           # Project metadata
    ├── setup.py                 # Installation script
    ├── requirements.txt         # Dependencies
    ├── .env.example             # Environment template
    └── .gitignore               # Git ignore rules
```

## Core Components

### 1. NVD Client (`nvd_client.py`)
- Async HTTP client for NVD API 2.0
- Rate limiting (5 without key, 50 with key)
- CVSS v2 and v3 metrics parsing
- Search by CVE ID, keyword, product, severity
- Date range filtering
- CPE (Common Platform Enumeration) support

### 2. Package Parser (`package_parser.py`)
- Auto-detects file format
- Supports package.json (npm)
- Supports requirements.txt (pip)
- Version string normalization (^, ~, >=, etc.)
- Vendor/product extraction
- Dependency type classification

### 3. Vulnerability Analyzer (`analyzer.py`)
- Matches dependencies to CVEs
- Severity filtering
- Statistical analysis
- Groups vulnerabilities by package
- Recent vulnerability detection
- Confidence scoring

### 4. Report Generator (`report.py`)
- Text format for terminals
- Markdown format for documentation
- JSON format for APIs
- Executive-focused summaries
- Risk level calculation
- Actionable recommendations

### 5. MCP Server (`mcp_server.py`)
- Model Context Protocol implementation
- Three exposed tools:
  - `audit_package_file` - Full security audit
  - `search_cve` - CVE database search
  - `get_vulnerability_stats` - Quick statistics
- Stdio-based communication
- Error handling

### 6. CLI Tool (`cli.py`)
- `audit` command - Audit package files
- `search` command - Search CVEs
- Multiple output formats
- CI/CD integration support
- Exit codes for automation

## Usage Examples

### CLI Usage

```bash
# Basic audit
python -m security_auditor.cli audit package.json

# With filtering
python -m security_auditor.cli audit package.json --severity CRITICAL HIGH

# Generate report
python -m security_auditor.cli audit package.json --format markdown -o report.md

# Recent vulnerabilities
python -m security_auditor.cli audit package.json --days 30

# Search CVEs
python -m security_auditor.cli search --keyword "nodejs" --severity CRITICAL
```

### Python API Usage

```python
import asyncio
from security_auditor.nvd_client import NVDClient
from security_auditor.package_parser import PackageParser
from security_auditor.analyzer import VulnerabilityAnalyzer
from security_auditor.report import ExecutiveSummaryGenerator

async def main():
    manifest = PackageParser.parse_package_json("package.json")

    async with NVDClient(api_key="your-key") as client:
        analyzer = VulnerabilityAnalyzer(
            nvd_client=client,
            severity_filter=["CRITICAL", "HIGH"]
        )

        result = await analyzer.analyze_manifest(manifest)
        report = ExecutiveSummaryGenerator.generate_text_summary(result)
        print(report)

asyncio.run(main())
```

### MCP Integration

```bash
# Start MCP server
python -m security_auditor.mcp_server

# Or configure with Claude Desktop
# Add to claude_desktop_config.json
```

## Technical Details

### Dependencies

- **mcp** (>=1.0.0) - Model Context Protocol
- **httpx** (>=0.27.0) - Async HTTP client
- **pydantic** (>=2.0.0) - Data validation
- **python-dotenv** (>=1.0.0) - Environment management

### Python Requirements

- Python 3.10 or higher
- Async/await support
- Type hints throughout

### API Details

- **NVD API Version**: 2.0
- **Endpoint**: https://services.nvd.nist.gov/rest/json/cves/2.0
- **Authentication**: Optional API key
- **Rate Limits**: 5 req/30s (no key), 50 req/30s (with key)

## Security Considerations

1. **API Key Management** - Use environment variables
2. **Input Validation** - Pydantic models validate all data
3. **Rate Limiting** - Automatic throttling
4. **Error Handling** - Graceful failure handling
5. **No Data Storage** - No persistent storage of CVE data

## Testing

```bash
# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_package_parser.py -v

# With coverage
pytest tests/ --cov=security_auditor
```

## CI/CD Integration

### Exit Codes

- `0` - No critical/high vulnerabilities
- `1` - High severity found
- `2` - Critical severity found

### GitHub Actions Example

```yaml
- name: Security Audit
  run: |
    python -m security_auditor.cli audit package.json
  env:
    NVD_API_KEY: ${{ secrets.NVD_API_KEY }}
```

## Performance Characteristics

### Benchmarks (approximate)

- Small project (10 deps): ~30-60 seconds
- Medium project (50 deps): ~2-5 minutes
- Large project (200 deps): ~10-20 minutes

*With API key. Without key, multiply by ~10x due to rate limits.*

### Optimization Tips

1. Use API key (50x faster)
2. Filter by severity (fewer API calls)
3. Exclude dev dependencies
4. Use date range filtering
5. Cache results for repeated scans

## Limitations

### Current Limitations

1. **Version Matching** - Keyword-based, not CPE range matching
2. **False Positives** - May match unrelated CVEs
3. **False Negatives** - May miss some relevant CVEs
4. **Performance** - Large projects take time due to API limits
5. **Language Support** - Only npm and pip currently

### Future Enhancements

- Advanced CPE version range matching
- Support for more package managers
- Result caching layer
- GitHub Security Advisories integration
- Automated remediation suggestions
- Web dashboard interface
- Batch processing mode
- Custom vulnerability databases

## Use Cases

### 1. Development Teams
- Pre-commit security checks
- Pull request validation
- Regular security audits
- Dependency updates planning

### 2. Security Teams
- Enterprise-wide vulnerability scanning
- Risk assessment reports
- Compliance documentation
- Executive briefings

### 3. DevOps/SRE
- CI/CD pipeline integration
- Automated security gates
- Deployment blocking
- Security metrics tracking

### 4. AI Assistants
- MCP integration with Claude
- Automated security analysis
- Natural language queries
- Report generation

## Documentation

| Document | Purpose |
|----------|---------|
| [README.md](../README.md) | Complete project documentation |
| [QUICKSTART.md](QUICKSTART.md) | Get started in 5 minutes |
| [API_GUIDE.md](API_GUIDE.md) | Python API reference |
| [MCP_INTEGRATION.md](MCP_INTEGRATION.md) | MCP protocol integration |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | This overview document |

## Installation

```bash
# Clone repository
git clone <repository-url>
cd Security-Auditor

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your NVD API key

# Run
python -m security_auditor.cli audit examples/package.json
```

## Development Workflow

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Run example
python -m security_auditor.cli audit examples/package.json
```

## License

This project is provided as-is for educational and security assessment purposes.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Resources

- [NIST NVD API](https://nvd.nist.gov/developers/vulnerabilities)
- [CVSS Specification](https://www.first.org/cvss/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

## Support

- GitHub Issues: Report bugs and request features
- Documentation: Check the docs/ folder
- Examples: See examples/ for sample usage

## Acknowledgments

- NIST for providing the National Vulnerability Database
- The security research community
- Contributors to the open-source ecosystem

---

**Built with Python 🐍 | Powered by NIST NVD 🔒 | MCP-Ready 🤖**
