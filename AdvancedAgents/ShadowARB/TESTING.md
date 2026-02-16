# Shadow ARB - Testing Guide

## Quick Start Testing

### 1. Environment Setup

```bash
# Navigate to project
cd ShadowARB

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use any editor
```

**Required Environment Variables:**
```env
# GitHub Token (https://github.com/settings/tokens)
GITHUB_TOKEN=ghp_your_token_here

# LLM Provider (choose one)
OPENAI_API_KEY=sk-your_openai_key_here
# OR
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# Model Selection
LLM_MODEL=gpt-4o
```

### 3. Get GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ `public_repo` (for public repos)
   - ✅ `repo` (for private repos)
4. Generate and copy token
5. Add to `.env` file

### 4. Test Cases

#### Option A: Use a Public Test PR

```bash
# Test with a real public PR (read-only, won't post comment)
python main.py --pr_url https://github.com/facebook/react/pull/28647 --dry-run
```

#### Option B: Create Your Own Test PR

```bash
# 1. Fork a repository or use your own
# 2. Create a test branch with changes
# 3. Open a PR
# 4. Run Shadow ARB

python main.py --pr_url https://github.com/YOUR_USERNAME/YOUR_REPO/pull/1 --dry-run
```

#### Option C: Test Without Posting

```bash
# Use --dry-run flag to preview review without posting to GitHub
python main.py --pr_url <YOUR_PR_URL> --dry-run
```

### 5. Verify Output

Expected console output:

```
🔧 Validating configuration...
✅ Configuration valid
🔍 Fetching PR diff from: https://github.com/...
📄 Fetched diff (1234 characters)
🤖 Starting Shadow ARB review workflow...
   ├─ Security Agent (parallel)
   ├─ Scale Agent (parallel)
   ├─ Clean Code Agent (parallel)
   └─ Chairperson Agent (synthesis)

================================================================================
REVIEW COMPLETE
================================================================================
## 🤖 Shadow ARB Review

### Security Findings
[Security issues listed here]

### Scalability Findings
[Scalability issues listed here]

### Code Quality Findings
[Code quality issues listed here]

---

### Final Verdict: Approved with Comments

[Summary and recommendations]
================================================================================

🏃 Dry-run mode: Skipping GitHub comment posting

✨ Shadow ARB review completed successfully
```

### 6. Post Real Review (No --dry-run)

```bash
# This will post the review as a comment on GitHub
python main.py --pr_url https://github.com/YOUR_USERNAME/YOUR_REPO/pull/1
```

**Note:** Your GitHub token needs `write:discussion` scope to post comments.

---

## 🐛 Troubleshooting

### Error: "GITHUB_TOKEN environment variable is required"

**Solution:**
```bash
# Check if .env file exists
cat .env

# Verify python-dotenv is installed
pip list | grep dotenv

# Manually export for testing
export GITHUB_TOKEN=ghp_your_token_here
python main.py --pr_url <URL> --dry-run
```

### Error: "Invalid GitHub PR URL format"

**Solution:**
- URL must be: `https://github.com/owner/repo/pull/NUMBER`
- Don't use shortened URLs
- Include `/pull/` not `/pulls/`

### Error: "Bad credentials" (GitHub)

**Solution:**
- Regenerate GitHub token
- Ensure token has `public_repo` or `repo` scope
- Check token isn't expired

### Error: "OpenAI API key" or "Anthropic API key"

**Solution:**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" | head
```

### Error: Module not found

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 🧪 Test Scenarios

### Minimal Test (Fast)

Small PR with 1-2 file changes:

```bash
# Example: Documentation update PR
python main.py --pr_url <SMALL_PR_URL> --dry-run
```

**Expected:** < 30 seconds, minimal findings

### Comprehensive Test (Realistic)

Medium PR with 5-10 file changes:

```bash
# Example: Feature implementation PR
python main.py --pr_url <MEDIUM_PR_URL> --dry-run
```

**Expected:** 1-2 minutes, multiple findings

### Stress Test (Large)

Large PR with 20+ file changes:

```bash
# Example: Major refactoring PR
python main.py --pr_url <LARGE_PR_URL> --dry-run
```

**Expected:** 2-5 minutes, extensive findings

---

## 📊 Verify Each Component

### Test 1: GitHub Integration

```python
# Create test_github.py
from shadow_arb.github_client import GitHubClient

client = GitHubClient()
pr_url = "https://github.com/facebook/react/pull/28647"
diff = client.get_pr_diff(pr_url)
print(f"✅ Fetched {len(diff)} characters")
```

```bash
python test_github.py
```

### Test 2: LLM Integration

```python
# Create test_llm.py
from litellm import completion

response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Say hello"}]
)
print(f"✅ LLM responded: {response.choices[0].message.content}")
```

```bash
python test_llm.py
```

### Test 3: Workflow Execution

```python
# Create test_workflow.py
from shadow_arb.workflow import run_review

test_diff = """
diff --git a/auth.py b/auth.py
+password = "hardcoded123"
+cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
"""

verdict = run_review(test_diff)
print(verdict)
```

```bash
python test_workflow.py
```

---

## ✅ Success Criteria

You've successfully tested Shadow ARB when:

- [x] Environment setup completed without errors
- [x] Configuration validated successfully
- [x] PR diff fetched from GitHub
- [x] All three agents executed in parallel
- [x] Chairperson synthesized findings
- [x] Review posted to GitHub (or --dry-run worked)
- [x] No Python exceptions or tracebacks

---

## 🔄 Next Steps After Testing

1. **Test with your own repository**
   - Create a test PR with intentional issues
   - Verify findings are accurate

2. **Tune agent prompts**
   - Edit `shadow_arb/prompts.py`
   - Customize for your team's standards

3. **Set up CI/CD integration**
   - Add GitHub Actions workflow
   - Trigger on PR events

4. **Configure team settings**
   - Adjust severity thresholds
   - Add custom review criteria

---

## 📞 Need Help?

If you encounter issues:

1. Check the error message carefully
2. Verify all environment variables are set
3. Ensure dependencies are installed
4. Test individual components separately
5. Check GitHub token permissions

**Common fixes solve 90% of issues:**
- Re-activate virtual environment
- Regenerate API tokens
- Clear and reinstall dependencies
- Check network connectivity
