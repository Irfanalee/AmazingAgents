# Security Auditor - Project Structure

Complete overview of the project file organization.

## Project Tree

```
Security-Auditor/
│
├── 📚 Documentation
│   ├── README.md                    # Main project documentation
│   ├── INDEX.md                     # Documentation index
│   ├── QUICKSTART.md                # 5-minute quick start guide
│   ├── INSTALL.md                   # Detailed installation instructions
│   ├── API_GUIDE.md                 # Python API reference
│   ├── MCP_INTEGRATION.md           # MCP protocol integration guide
│   └── PROJECT_SUMMARY.md           # High-level project overview
│
├── 🐍 Source Code
│   └── src/security_auditor/
│       ├── __init__.py              # Package initialization
│       ├── nvd_client.py            # NVD API client (372 lines)
│       ├── package_parser.py        # Package manifest parser (195 lines)
│       ├── analyzer.py              # Vulnerability analyzer (224 lines)
│       ├── report.py                # Report generator (329 lines)
│       ├── mcp_server.py            # MCP server implementation (262 lines)
│       └── cli.py                   # Command-line interface (190 lines)
│
├── 📦 Examples
│   ├── package.json                 # Sample Node.js dependencies
│   ├── requirements.txt             # Sample Python dependencies
│   └── run_example.py               # Interactive example script
│
├── 🧪 Tests
│   └── tests/
│       └── test_package_parser.py   # Package parser unit tests
│
├── ⚙️ Configuration
│   ├── pyproject.toml               # Project metadata & build config
│   ├── setup.py                     # Setup script for installation
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment variables template
│   └── .gitignore                   # Git ignore rules
│
└── 📋 Additional Files
    └── PROJECT_STRUCTURE.md         # This file
```

## File Descriptions

### Documentation (7 files)

| File | Lines | Purpose |
|------|-------|---------|
| README.md | ~600 | Complete project documentation with features, usage, examples |
| INDEX.md | ~350 | Documentation index and navigation guide |
| QUICKSTART.md | ~250 | Get started in 5 minutes with common examples |
| INSTALL.md | ~450 | Platform-specific installation instructions |
| API_GUIDE.md | ~600 | Comprehensive Python API reference with examples |
| MCP_INTEGRATION.md | ~400 | MCP protocol integration for AI assistants |
| PROJECT_SUMMARY.md | ~500 | Architecture overview and technical details |

### Source Code (7 files, ~1,572 lines)

| File | Lines | Classes/Functions | Purpose |
|------|-------|-------------------|---------|
| nvd_client.py | 372 | NVDClient, CVEData, CVSSMetrics | Async NVD API client with rate limiting |
| package_parser.py | 195 | PackageParser, PackageManifest | Parse npm & pip package files |
| analyzer.py | 224 | VulnerabilityAnalyzer, AnalysisResult | Match dependencies to CVEs |
| report.py | 329 | ExecutiveSummaryGenerator | Generate reports in text/markdown/JSON |
| mcp_server.py | 262 | SecurityAuditorMCP | MCP protocol server |
| cli.py | 190 | main(), audit_command(), search_command() | Command-line interface |
| __init__.py | 4 | - | Package initialization |

### Test Files (1 file, ~100 lines)

| File | Tests | Coverage |
|------|-------|----------|
| test_package_parser.py | 4 test functions | PackageParser module |

### Configuration Files (5 files)

| File | Format | Purpose |
|------|--------|---------|
| pyproject.toml | TOML | Project metadata, dependencies, build config |
| setup.py | Python | Installation script with entry points |
| requirements.txt | Text | Production dependencies |
| .env.example | Env | Environment variables template |
| .gitignore | Text | Git ignore patterns |

### Example Files (3 files)

| File | Type | Purpose |
|------|------|---------|
| examples/package.json | JSON | Sample Node.js project dependencies |
| examples/requirements.txt | Text | Sample Python project dependencies |
| run_example.py | Python | Interactive demonstration script |

## Module Dependencies

```
┌─────────────────────────────────────────────────────┐
│                   CLI / MCP Server                  │
│              (cli.py, mcp_server.py)                │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│              Report Generator                       │
│                 (report.py)                         │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│         Vulnerability Analyzer                      │
│              (analyzer.py)                          │
└──────────┬──────────────────────────┬───────────────┘
           │                          │
           ▼                          ▼
┌──────────────────────┐   ┌─────────────────────────┐
│   Package Parser     │   │     NVD Client          │
│  (package_parser.py) │   │   (nvd_client.py)       │
└──────────────────────┘   └─────────────────────────┘
```

## Code Statistics

### Total Lines of Code

```
Source Code:     ~1,572 lines
Tests:           ~100 lines
Documentation:   ~3,150 lines
Examples:        ~120 lines
Configuration:   ~150 lines
────────────────────────────
Total:           ~5,092 lines
```

### Language Breakdown

```
Python:          ~1,800 lines (35%)
Markdown:        ~3,150 lines (62%)
JSON/TOML:       ~100 lines (2%)
Text:            ~50 lines (1%)
```

## Key Features by File

### nvd_client.py
- ✅ Async HTTP client using httpx
- ✅ Automatic rate limiting
- ✅ CVSS v2 and v3 parsing
- ✅ Search by CVE ID, keyword, product
- ✅ Date range filtering
- ✅ Context manager support

### package_parser.py
- ✅ Auto-detect file format
- ✅ Parse package.json (npm)
- ✅ Parse requirements.txt (pip)
- ✅ Version normalization (^, ~, >=)
- ✅ Vendor/product extraction
- ✅ Dependency classification

### analyzer.py
- ✅ Match dependencies to CVEs
- ✅ Severity filtering
- ✅ Statistical analysis
- ✅ Group by package
- ✅ Recent vulnerability detection
- ✅ Confidence scoring

### report.py
- ✅ Text format (terminal-friendly)
- ✅ Markdown format (documentation)
- ✅ JSON format (API integration)
- ✅ Executive summaries
- ✅ Risk assessment
- ✅ Actionable recommendations

### mcp_server.py
- ✅ MCP protocol implementation
- ✅ Three tools exposed
- ✅ Stdio communication
- ✅ Error handling
- ✅ Tool schema validation

### cli.py
- ✅ Audit command
- ✅ Search command
- ✅ Multiple output formats
- ✅ Severity filtering
- ✅ Exit codes for CI/CD

## Import Graph

```python
# External Dependencies
import asyncio          # Async/await support
import httpx           # HTTP client
from pydantic import BaseModel  # Data validation
from dotenv import load_dotenv  # Environment variables
from mcp.server import Server   # MCP protocol

# Internal Dependencies
from nvd_client import NVDClient
from package_parser import PackageParser
from analyzer import VulnerabilityAnalyzer
from report import ExecutiveSummaryGenerator
```

## Data Flow

```
1. Input (package.json/requirements.txt)
   │
   ▼
2. PackageParser → PackageManifest
   │
   ▼
3. VulnerabilityAnalyzer + NVDClient
   │
   ├─→ Query NVD API for each dependency
   ├─→ Match CVEs to dependencies
   └─→ Filter by severity
   │
   ▼
4. AnalysisResult
   │
   ├─→ Severity statistics
   ├─→ Vulnerability matches
   └─→ Package grouping
   │
   ▼
5. ExecutiveSummaryGenerator
   │
   ├─→ Text report
   ├─→ Markdown report
   └─→ JSON report
   │
   ▼
6. Output (stdout, file, or MCP response)
```

## API Endpoints Used

```
NVD API v2.0:
https://services.nvd.nist.gov/rest/json/cves/2.0

Query Parameters:
- cveId              # Specific CVE identifier
- keywordSearch      # Search in descriptions
- cpeName            # CPE name filter
- pubStartDate       # Publication date range start
- pubEndDate         # Publication date range end
- cvssV3Severity     # Severity filter
- resultsPerPage     # Pagination (max 2000)
- startIndex         # Pagination offset
```

## Environment Variables

```bash
# Required for optimal performance
NVD_API_KEY=your_api_key_here

# Optional (with defaults)
NVD_RATE_LIMIT=50        # 5 without key, 50 with key
NVD_TIMEOUT=30           # Request timeout in seconds
```

## Testing Coverage

```
✅ Package Parser
   - Parse package.json
   - Parse requirements.txt
   - Version cleaning
   - Vendor/product extraction

⏳ Planned Tests
   - NVD Client
   - Vulnerability Analyzer
   - Report Generator
   - CLI Commands
   - MCP Server
```

## Performance Metrics

### Rate Limits
- Without API key: 5 requests / 30 seconds
- With API key: 50 requests / 30 seconds

### Typical Scan Times
- 10 packages: ~30-60 seconds
- 50 packages: ~2-5 minutes
- 200 packages: ~10-20 minutes

*Times with API key. 10x slower without.*

## Future Enhancements

### Planned Features
- [ ] Advanced CPE version matching
- [ ] Support for more package managers
- [ ] Result caching
- [ ] GitHub Security Advisories
- [ ] Automated fixes
- [ ] Web dashboard
- [ ] Batch processing
- [ ] Custom databases

### Code Improvements
- [ ] Increase test coverage to 80%+
- [ ] Add integration tests
- [ ] Performance benchmarks
- [ ] Type stub files
- [ ] Async optimization

## Directory Purpose

| Directory | Purpose | Files |
|-----------|---------|-------|
| `/` | Root documentation & config | 14 |
| `/src/security_auditor/` | Main source code | 7 |
| `/examples/` | Sample files for testing | 3 |
| `/tests/` | Unit tests | 1 |

## File Naming Conventions

- **Python files**: `snake_case.py`
- **Documentation**: `UPPERCASE.md`
- **Config files**: Standard names (pyproject.toml, setup.py)
- **Examples**: Descriptive names (package.json, requirements.txt)

## Quick Access

### Most Important Files

1. **[README.md](../README.md)** - Start here
2. **[QUICKSTART.md](QUICKSTART.md)** - Get started fast
3. **[src/security_auditor/cli.py](src/security_auditor/cli.py)** - CLI entry point
4. **[run_example.py](run_example.py)** - Try it out

### Developer Files

1. **[src/security_auditor/nvd_client.py](src/security_auditor/nvd_client.py)** - API client
2. **[src/security_auditor/analyzer.py](src/security_auditor/analyzer.py)** - Core logic
3. **[tests/test_package_parser.py](tests/test_package_parser.py)** - Test examples
4. **[setup.py](setup.py)** - Installation

### Documentation Files

1. **[INDEX.md](INDEX.md)** - Navigation guide
2. **[API_GUIDE.md](API_GUIDE.md)** - API reference
3. **[MCP_INTEGRATION.md](MCP_INTEGRATION.md)** - MCP guide
4. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Overview

## Build & Distribution

```bash
# Install locally
pip install -e .

# Build distribution
python setup.py sdist bdist_wheel

# Install from distribution
pip install dist/security-auditor-0.1.0.tar.gz
```

## Version Control

```
Current Version: 0.1.0
Status: Beta
Python: 3.10+
License: As-is for educational purposes
```

---

**Need help navigating? See [INDEX.md](INDEX.md)**

**Want to contribute? All files are well-documented with docstrings!**
