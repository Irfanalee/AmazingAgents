# Shadow ARB - AI-Powered Architecture Review Board

An automated code review system that uses three specialized AI agents to review GitHub Pull Requests in parallel, synthesize their findings, and post a consolidated review comment.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         START                               │
│                    (PR Diff Input)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌────────┐   ┌──────────┐   ┌──────────┐
    │Security│   │  Scale   │   │  Clean   │  ◄── PARALLEL
    │ Agent  │   │  Agent   │   │Code Agent│      EXECUTION
    └────┬───┘   └─────┬────┘   └─────┬────┘
         │             │              │
         └─────────────┼──────────────┘
                       ▼
                ┌─────────────┐
                │Chairperson  │  ◄── SYNTHESIS
                │   Agent     │
                └──────┬──────┘
                       ▼
                ┌─────────────┐
                │   GitHub    │
                │  Comment    │
                └─────────────┘
```

## 🎯 Features

- **Parallel Agent Execution**: Three specialized agents run concurrently using LangGraph
- **Structured Output**: All findings use Pydantic models (no free-form text)
- **Unified LLM Interface**: LiteLLM supports OpenAI and Anthropic models
- **Type-Safe**: Full type hints and MyPy compatibility
- **Production-Ready**: Error handling, logging, and configuration management

## 📦 Tech Stack

- **LangGraph**: Stateful workflow orchestration
- **PyGithub**: GitHub API integration
- **Pydantic**: Data validation and structured output
- **LiteLLM**: Unified LLM interface (OpenAI/Anthropic)
- **Python 3.11+**: Modern Python with type hints

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
cd ShadowARB

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
GITHUB_TOKEN=ghp_your_github_token_here
OPENAI_API_KEY=sk-your_openai_key_here
# OR
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

LLM_MODEL=gpt-4o
```

### 3. Usage

Review a Pull Request:

```bash
python main.py --pr_url https://github.com/owner/repo/pull/123
```

Dry-run (review without posting):

```bash
python main.py --pr_url https://github.com/owner/repo/pull/123 --dry-run
```

## 📁 Project Structure

```
ShadowARB/
├── shadow_arb/
│   ├── __init__.py          # Package initialization
│   ├── state.py             # AgentState TypedDict definition
│   ├── agents.py            # Three specialized agents + chairperson
│   ├── workflow.py          # LangGraph workflow orchestration
│   ├── config.py            # Configuration and environment management
│   ├── prompts.py           # System prompts for each agent
│   └── github_client.py     # GitHub API integration
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🤖 Agent Responsibilities

### Security Agent
- SQL Injection, XSS, CSRF vulnerabilities
- Hardcoded credentials and secrets
- Insecure authentication/authorization
- Input validation and sanitization
- Cryptographic best practices

### Scale Agent
- N+1 query problems
- Missing pagination
- Memory leaks and resource consumption
- Algorithm efficiency
- Caching strategies
- Concurrency issues

### Clean Code Agent
- SOLID principle violations
- Code duplication (DRY)
- Naming conventions
- Function complexity
- Error handling
- Test coverage
- Documentation quality

### Chairperson Agent
- Synthesizes all findings
- Organizes by severity
- Provides final verdict
- Generates markdown review

## 🔧 Development

### Type Checking

```bash
mypy shadow_arb/
```

### Running Tests

```bash
# Add your test framework (pytest recommended)
pytest tests/
```

## 🔐 Security Notes

- Never commit `.env` file or API keys
- Use GitHub Personal Access Tokens with minimal required scopes
- Rotate tokens regularly
- Review LiteLLM's data handling policies

## 📝 GitHub Token Scopes

Required scopes for the GitHub token:
- `repo` (for private repositories) or `public_repo` (for public repositories)
- `write:discussion` (to post comments)

## 🎛️ Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | Required |
| `OPENAI_API_KEY` | OpenAI API key | Optional* |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional* |
| `LLM_MODEL` | Model to use | `gpt-4o` |
| `LITELLM_LOG` | LiteLLM log level | `INFO` |

*At least one LLM API key is required

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Troubleshooting

### "GITHUB_TOKEN environment variable is required"
- Ensure `.env` file exists and contains `GITHUB_TOKEN`
- Check that `python-dotenv` is installed

### "Invalid GitHub PR URL format"
- URL must be: `https://github.com/owner/repo/pull/number`
- Ensure the PR number is correct

### LiteLLM API Errors
- Verify API keys are valid
- Check model name matches your provider
- Ensure sufficient API credits

## 🗺️ Roadmap

- [ ] Add support for GitLab and Bitbucket
- [ ] Implement caching for repeated reviews
- [ ] Add custom agent configuration
- [ ] Support for incremental reviews (only new commits)
- [ ] Web dashboard for review history
- [ ] Slack/Teams integration for notifications

---

**Built with ❤️ for better code quality**
