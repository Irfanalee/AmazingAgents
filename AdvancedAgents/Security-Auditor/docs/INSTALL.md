# Installation Guide

Complete installation instructions for Security Auditor on different platforms.

## System Requirements

- **Python**: 3.10 or higher
- **Operating System**: macOS, Linux, or Windows
- **Network**: Internet connection for NVD API access
- **Memory**: 256 MB minimum
- **Disk Space**: 50 MB

## Installation Methods

### Method 1: Basic Installation (Recommended)

```bash
# 1. Clone or download the repository
git clone <repository-url>
cd Security-Auditor

# 2. Create a virtual environment (recommended)
python -m venv venv

# 3. Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
cp .env.example .env
# Edit .env and add your NVD API key (see below)

# 6. Test the installation
python run_example.py
```

### Method 2: Development Installation

For contributors or those who want to modify the code:

```bash
# 1-3. Same as Method 1

# 4. Install with development dependencies
pip install -e ".[dev]"

# 5. Verify installation
pytest tests/ -v

# 6. Run example
python run_example.py
```

### Method 3: Using setup.py

```bash
# 1-3. Same as Method 1

# 4. Install the package
python setup.py install

# 5. Run using the installed command
security-auditor audit examples/package.json
```

## Getting an NVD API Key

An API key is **optional but highly recommended** for better performance.

### Why You Need an API Key

| Without API Key | With API Key |
|----------------|--------------|
| 5 requests per 30 seconds | 50 requests per 30 seconds |
| Slow for large projects | 10x faster |
| May timeout | Reliable performance |

### How to Get an API Key

1. Visit [https://nvd.nist.gov/developers/request-an-api-key](https://nvd.nist.gov/developers/request-an-api-key)

2. Fill out the request form:
   - Enter your email address
   - Agree to the terms of service
   - Complete the CAPTCHA

3. Check your email:
   - You'll receive an API key immediately
   - The key will be a long alphanumeric string

4. Add to your `.env` file:
   ```bash
   NVD_API_KEY=your-actual-api-key-here
   NVD_RATE_LIMIT=50
   ```

5. Verify it works:
   ```bash
   python run_example.py
   ```

## Platform-Specific Instructions

### macOS

```bash
# Install Python 3.10+ using Homebrew
brew install python@3.10

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make run_example.py executable
chmod +x run_example.py

# Run example
./run_example.py
```

### Linux (Ubuntu/Debian)

```bash
# Install Python 3.10+
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run example
python run_example.py
```

### Linux (RHEL/CentOS/Fedora)

```bash
# Install Python 3.10+
sudo dnf install python3.10

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run example
python run_example.py
```

### Windows

```powershell
# Download and install Python 3.10+ from python.org

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run example
python run_example.py
```

## Verifying Installation

### 1. Check Python Version

```bash
python --version
# Should output: Python 3.10.x or higher
```

### 2. Check Dependencies

```bash
pip list
# Should show: mcp, httpx, pydantic, python-dotenv
```

### 3. Run Tests

```bash
pytest tests/ -v
# Should pass all tests
```

### 4. Test CLI

```bash
python -m security_auditor.cli audit examples/package.json
# Should output security audit report
```

### 5. Test MCP Server

```bash
python -m security_auditor.mcp_server &
# Should start without errors (Ctrl+C to stop)
```

## Troubleshooting

### Python Version Issues

**Problem**: "Python 3.10 or higher is required"

**Solution**:
```bash
# Check your Python version
python --version

# Install Python 3.10+ from python.org or your package manager
# Then create a new virtual environment with the correct version
python3.10 -m venv venv
```

### Module Not Found Errors

**Problem**: "ModuleNotFoundError: No module named 'mcp'"

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Import Errors

**Problem**: "ImportError: cannot import name 'NVDClient'"

**Solution**:
```bash
# Make sure you're in the project root directory
pwd  # or cd on Windows

# Try running with module syntax
python -m security_auditor.cli audit examples/package.json
```

### Network Errors

**Problem**: "Connection timeout to nvd.nist.gov"

**Solution**:
1. Check your internet connection
2. Verify you can access https://nvd.nist.gov
3. Check if you're behind a proxy
4. Try increasing the timeout in `.env`:
   ```bash
   NVD_TIMEOUT=60
   ```

### Rate Limit Errors

**Problem**: "Rate limit exceeded"

**Solution**:
1. Get an NVD API key (free)
2. Add it to your `.env` file
3. Wait 30 seconds before retrying
4. Use severity filtering to reduce API calls

### Permission Errors

**Problem**: "Permission denied: .env"

**Solution**:
```bash
# Make sure the .env file has correct permissions
chmod 644 .env

# Make sure you own the file
ls -la .env
```

## Docker Installation (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV NVD_API_KEY=""
ENV NVD_RATE_LIMIT=5

CMD ["python", "-m", "security_auditor.mcp_server"]
```

Build and run:

```bash
# Build image
docker build -t security-auditor .

# Run container
docker run -it --rm \
  -e NVD_API_KEY=your-key \
  -v $(pwd)/package.json:/app/package.json \
  security-auditor \
  python -m security_auditor.cli audit /app/package.json
```

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Remove the project directory
cd ..
rm -rf Security-Auditor
```

## Updating

```bash
# Activate virtual environment
source venv/bin/activate

# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests
pytest tests/ -v
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| NVD_API_KEY | No | None | NVD API key for higher rate limits |
| NVD_RATE_LIMIT | No | 5 or 50 | Requests per 30 seconds |
| NVD_TIMEOUT | No | 30 | Request timeout in seconds |

## Next Steps

After successful installation:

1. ✅ Read [QUICKSTART.md](QUICKSTART.md) for usage examples
2. ✅ Run `python run_example.py` to see it in action
3. ✅ Try auditing your own projects
4. ✅ Explore the [API_GUIDE.md](API_GUIDE.md) for Python API
5. ✅ Set up [MCP Integration](MCP_INTEGRATION.md) for AI assistants

## Getting Help

- **Documentation**: Check the `docs/` folder
- **Examples**: See `examples/` directory
- **Issues**: Open an issue on GitHub
- **Tests**: Run `pytest tests/ -v` for diagnostics

## System Compatibility

### Tested Platforms

- ✅ macOS 12+ (Intel & Apple Silicon)
- ✅ Ubuntu 20.04+
- ✅ Debian 11+
- ✅ Windows 10/11
- ✅ CentOS 8+
- ✅ Fedora 35+

### Python Versions

- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12
- ❌ Python 3.9 (missing required features)
- ❌ Python 2.x (not supported)

## Support

For installation issues:
1. Check this guide first
2. Review the [README.md](../README.md)
3. Search existing GitHub issues
4. Open a new issue with:
   - Your OS and Python version
   - Complete error message
   - Steps to reproduce

---

**Installation complete? Run `python run_example.py` to get started! 🚀**
