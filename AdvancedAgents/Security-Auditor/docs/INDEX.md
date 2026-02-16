# Security Auditor - Documentation Index

Welcome to Security Auditor! This index will help you find the right documentation for your needs.

## 🚀 Getting Started

**New to Security Auditor? Start here:**

1. **[INSTALL.md](INSTALL.md)** - Complete installation guide for all platforms
2. **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
3. **[README.md](../README.md)** - Full project documentation and overview

## 📚 Documentation by Topic

### Installation & Setup

| Document | Description | When to Use |
|----------|-------------|-------------|
| [INSTALL.md](INSTALL.md) | Detailed installation instructions | First time setup, troubleshooting |
| [QUICKSTART.md](QUICKSTART.md) | Quick 5-minute setup guide | Want to try it quickly |
| [.env.example](.env.example) | Environment configuration template | Setting up API keys |

### Usage Guides

| Document | Description | When to Use |
|----------|-------------|-------------|
| [README.md](../README.md) | Complete feature documentation | Understanding all features |
| [API_GUIDE.md](API_GUIDE.md) | Python API reference | Building custom integrations |
| [MCP_INTEGRATION.md](MCP_INTEGRATION.md) | MCP protocol integration | Integrating with AI assistants |

### Reference

| Document | Description | When to Use |
|----------|-------------|-------------|
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | High-level project overview | Understanding architecture |
| [pyproject.toml](pyproject.toml) | Project metadata | Package management |
| [requirements.txt](requirements.txt) | Python dependencies | Installing dependencies |

### Examples

| File | Description | When to Use |
|------|-------------|-------------|
| [examples/package.json](examples/package.json) | Sample Node.js dependencies | Testing npm package scanning |
| [examples/requirements.txt](examples/requirements.txt) | Sample Python dependencies | Testing pip package scanning |
| [run_example.py](run_example.py) | Runnable example script | Seeing it in action |

## 🎯 Documentation by User Type

### For Developers

**Want to audit your project dependencies?**

1. [INSTALL.md](INSTALL.md) - Install Security Auditor
2. [QUICKSTART.md](QUICKSTART.md) - Run your first audit
3. [README.md](README.md#cli-tool) - Learn CLI commands
4. [API_GUIDE.md](API_GUIDE.md) - Integrate into your code

**Key Files:**
- CLI: [src/security_auditor/cli.py](src/security_auditor/cli.py)
- Examples: [examples/](examples/)

### For Security Teams

**Need to generate executive reports?**

1. [QUICKSTART.md](QUICKSTART.md) - Get started quickly
2. [README.md](README.md#executive-summaries) - Report formats
3. [API_GUIDE.md](API_GUIDE.md#report-generation) - Custom reports

**Key Files:**
- Report Generator: [src/security_auditor/report.py](src/security_auditor/report.py)
- Analyzer: [src/security_auditor/analyzer.py](src/security_auditor/analyzer.py)

### For DevOps Engineers

**Want to integrate into CI/CD?**

1. [README.md](README.md#cicd-integration) - CI/CD examples
2. [QUICKSTART.md](QUICKSTART.md#exit-codes) - Exit codes
3. [API_GUIDE.md](API_GUIDE.md#integration-with-cicd) - Automation

**Key Concepts:**
- Exit codes: 0 (safe), 1 (high), 2 (critical)
- JSON output for parsing
- Environment variable configuration

### For AI Assistant Developers

**Integrating with Claude or other AI systems?**

1. [MCP_INTEGRATION.md](MCP_INTEGRATION.md) - Full MCP guide
2. [API_GUIDE.md](API_GUIDE.md) - Python API reference
3. [README.md](README.md#mcp-server) - MCP overview

**Key Files:**
- MCP Server: [src/security_auditor/mcp_server.py](src/security_auditor/mcp_server.py)
- Tools: audit_package_file, search_cve, get_vulnerability_stats

### For Contributors

**Want to contribute to the project?**

1. [INSTALL.md](INSTALL.md#method-2-development-installation) - Dev setup
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Architecture overview
3. [tests/](tests/) - Test examples

**Key Files:**
- Setup: [setup.py](setup.py)
- Tests: [tests/test_package_parser.py](tests/test_package_parser.py)
- Source: [src/security_auditor/](src/security_auditor/)

## 📖 Documentation by Task

### "I want to..."

#### Audit my package.json file
→ [QUICKSTART.md](QUICKSTART.md#step-3-run-your-first-audit)

#### Get an NVD API key
→ [INSTALL.md](INSTALL.md#getting-an-nvd-api-key)

#### Generate a markdown report
→ [QUICKSTART.md](QUICKSTART.md#generate-markdown-report)

#### Search for specific CVEs
→ [QUICKSTART.md](QUICKSTART.md#searching-for-specific-cves)

#### Use it in my Python code
→ [API_GUIDE.md](API_GUIDE.md#basic-usage)

#### Set up with Claude Desktop
→ [MCP_INTEGRATION.md](MCP_INTEGRATION.md#claude-desktop-integration)

#### Integrate with GitHub Actions
→ [README.md](README.md#cicd-integration)

#### Filter by severity
→ [QUICKSTART.md](QUICKSTART.md#filter-by-severity)

#### Understand the architecture
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#core-components)

#### Run tests
→ [INSTALL.md](INSTALL.md#verifying-installation)

#### Troubleshoot issues
→ [INSTALL.md](INSTALL.md#troubleshooting)

#### Contribute code
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#contributing)

## 🔍 Source Code Reference

### Core Modules

| Module | Purpose | Documentation |
|--------|---------|---------------|
| [nvd_client.py](src/security_auditor/nvd_client.py) | NVD API client | [API_GUIDE.md#nvd-client](API_GUIDE.md#nvd-client) |
| [package_parser.py](src/security_auditor/package_parser.py) | Parse package files | [API_GUIDE.md#package-parser](API_GUIDE.md#package-parser) |
| [analyzer.py](src/security_auditor/analyzer.py) | Vulnerability analysis | [API_GUIDE.md#vulnerability-analyzer](API_GUIDE.md#vulnerability-analyzer) |
| [report.py](src/security_auditor/report.py) | Report generation | [API_GUIDE.md#report-generation](API_GUIDE.md#report-generation) |
| [mcp_server.py](src/security_auditor/mcp_server.py) | MCP server | [MCP_INTEGRATION.md](MCP_INTEGRATION.md) |
| [cli.py](src/security_auditor/cli.py) | CLI interface | [README.md#cli-tool](README.md#cli-tool) |

## 📋 Quick Reference

### Common Commands

```bash
# Basic audit
python -m security_auditor.cli audit package.json

# With severity filter
python -m security_auditor.cli audit package.json --severity CRITICAL HIGH

# Generate markdown report
python -m security_auditor.cli audit package.json --format markdown -o report.md

# Search CVEs
python -m security_auditor.cli search --keyword "nodejs" --severity CRITICAL

# Run MCP server
python -m security_auditor.mcp_server

# Run example
python run_example.py

# Run tests
pytest tests/ -v
```

### File Locations

```
Security-Auditor/
├── Documentation/
│   ├── README.md           # Main docs
│   ├── QUICKSTART.md       # Quick start
│   ├── INSTALL.md          # Installation
│   ├── API_GUIDE.md        # API reference
│   ├── MCP_INTEGRATION.md  # MCP guide
│   ├── PROJECT_SUMMARY.md  # Overview
│   └── INDEX.md            # This file
│
├── Source Code/
│   └── src/security_auditor/
│       ├── nvd_client.py
│       ├── package_parser.py
│       ├── analyzer.py
│       ├── report.py
│       ├── mcp_server.py
│       └── cli.py
│
├── Examples/
│   ├── package.json
│   ├── requirements.txt
│   └── run_example.py
│
├── Tests/
│   └── tests/
│
└── Configuration/
    ├── pyproject.toml
    ├── requirements.txt
    ├── setup.py
    └── .env.example
```

## 🆘 Getting Help

### Documentation Not Helpful?

1. **Check Examples**: See [examples/](examples/) directory
2. **Run Example**: Execute `python run_example.py`
3. **Search Issues**: Look for similar problems on GitHub
4. **Ask Questions**: Open a GitHub issue

### Common Questions

**Q: Do I need an API key?**
A: No, but it's recommended. See [INSTALL.md](INSTALL.md#getting-an-nvd-api-key)

**Q: Which Python version?**
A: Python 3.10 or higher. See [INSTALL.md](INSTALL.md#system-requirements)

**Q: How do I generate reports?**
A: See [QUICKSTART.md](QUICKSTART.md#generate-markdown-report)

**Q: Can I use it in CI/CD?**
A: Yes! See [README.md](README.md#cicd-integration)

**Q: How do I integrate with Claude?**
A: See [MCP_INTEGRATION.md](MCP_INTEGRATION.md#claude-desktop-integration)

## 📚 External Resources

- [NIST NVD API Documentation](https://nvd.nist.gov/developers/vulnerabilities)
- [CVSS Specification](https://www.first.org/cvss/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Python asyncio Guide](https://docs.python.org/3/library/asyncio.html)

## 🗺️ Learning Path

### Beginner Path

1. **Install** → [INSTALL.md](INSTALL.md)
2. **Quick Start** → [QUICKSTART.md](QUICKSTART.md)
3. **Run Example** → `python run_example.py`
4. **Try Your Project** → Audit your package.json

### Intermediate Path

1. Complete Beginner Path
2. **Learn CLI** → [README.md](README.md#cli-tool)
3. **Explore API** → [API_GUIDE.md](API_GUIDE.md)
4. **Custom Reports** → [API_GUIDE.md](API_GUIDE.md#custom-reporting)

### Advanced Path

1. Complete Intermediate Path
2. **MCP Integration** → [MCP_INTEGRATION.md](MCP_INTEGRATION.md)
3. **Source Code** → [src/security_auditor/](src/security_auditor/)
4. **Contribute** → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#contributing)

## 📝 Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| README.md | ✅ Complete | 2024-12-10 |
| INSTALL.md | ✅ Complete | 2024-12-10 |
| QUICKSTART.md | ✅ Complete | 2024-12-10 |
| API_GUIDE.md | ✅ Complete | 2024-12-10 |
| MCP_INTEGRATION.md | ✅ Complete | 2024-12-10 |
| PROJECT_SUMMARY.md | ✅ Complete | 2024-12-10 |
| INDEX.md | ✅ Complete | 2024-12-10 |

---

**Can't find what you're looking for? Open an issue on GitHub!**

**Ready to start? → [INSTALL.md](INSTALL.md) or [QUICKSTART.md](QUICKSTART.md)**
