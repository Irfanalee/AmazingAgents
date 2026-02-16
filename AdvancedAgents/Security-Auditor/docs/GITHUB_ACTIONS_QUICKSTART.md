# GitHub Actions Quick Start

Get automated security scanning running in 5 minutes!

## 🚀 Instant Setup

### Step 1: Get Your NVD API Key (2 minutes)

1. Visit: https://nvd.nist.gov/developers/request-an-api-key
2. Enter your email
3. Check your email for the API key
4. Copy the key

### Step 2: Add Secret to GitHub (1 minute)

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `NVD_API_KEY`
5. Value: Paste your API key
6. Click **Add secret**

### Step 3: Workflows Are Ready! (Already Done)

The workflows are already in `.github/workflows/`:

✅ `security-audit-weekly.yml` - Runs every Monday at 9 AM
✅ `security-audit-pr.yml` - Runs on pull requests
✅ `security-audit-manual.yml` - Manual trigger with options

### Step 4: Test It (2 minutes)

**Option A: Manual Run**

1. Go to **Actions** tab in your repo
2. Click **Manual Security Audit**
3. Click **Run workflow**
4. Select options and click **Run workflow**

**Option B: Create a PR**

1. Make any change to `package.json` or `requirements.txt`
2. Create a pull request
3. Watch the security check run automatically!

That's it! 🎉

---

## 📋 What Each Workflow Does

### Weekly Scan (`security-audit-weekly.yml`)

**Runs:** Every Monday at 9 AM UTC
**Scans:** package.json, requirements.txt
**Creates:** GitHub Issue if critical vulnerabilities found
**Uploads:** Reports as artifacts (90 days retention)

### PR Check (`security-audit-pr.yml`)

**Runs:** On pull requests
**Scans:** Changed dependency files
**Posts:** Comment on PR with results
**Blocks:** Merge if critical vulnerabilities found

### Manual Run (`security-audit-manual.yml`)

**Runs:** When you trigger it
**Options:**
- Severity levels
- Include dev dependencies
- Recent CVEs only
- Output format

---

## ⚙️ Customization

### Change Schedule

Edit `.github/workflows/security-audit-weekly.yml`:

```yaml
on:
  schedule:
    # Every Monday at 9 AM
    - cron: '0 9 * * 1'

    # Change to your preference:
    # Daily at midnight:    '0 0 * * *'
    # Every Friday 5 PM:    '0 17 * * 5'
    # 1st of month:         '0 0 1 * *'
```

### Change Severity Filter

```yaml
--severity CRITICAL HIGH    # Default (recommended)
--severity CRITICAL         # Only critical
--severity CRITICAL HIGH MEDIUM LOW  # All severities
```

### Add Slack Notifications

Add to any workflow:

```yaml
- name: Slack Notification
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "🚨 Security alert in ${{ github.repository }}"
      }
```

---

## 🎯 Usage Examples

### View Results

**Weekly Scan Results:**
1. Go to **Actions** tab
2. Click **Weekly Security Audit**
3. Click latest run
4. Download artifacts

**PR Comments:**
- Automatically posted on PRs
- Shows summary of vulnerabilities found

### Download Reports

```bash
# Using GitHub CLI
gh run download <run-id>

# Or download from Actions UI
Actions → Workflow run → Artifacts → Download
```

### Manual Scan Options

Trigger manual scan with custom settings:

1. **Severity:** CRITICAL only
2. **Include dev:** Yes
3. **Days back:** 30 (recent CVEs)
4. **Format:** json

---

## 📊 Understanding Results

### Exit Codes

- **0** = No critical/high vulnerabilities ✅
- **1** = High severity found ⚠️
- **2** = Critical severity found ❌

### Report Sections

```markdown
## Overview
Packages Analyzed: 50
Vulnerabilities Found: 12

## Severity Breakdown
CRITICAL: 2
HIGH: 5
MEDIUM: 3
LOW: 2

## Risk Assessment
Risk Level: HIGH
Immediate Action: 7 vulnerabilities
```

---

## 🔧 Troubleshooting

### "NVD_API_KEY not found"

**Fix:** Add the secret in Settings → Secrets → Actions

### "Rate limit exceeded"

**Fix:**
1. Make sure NVD_API_KEY is set
2. Without key: 5 req/30s (very slow)
3. With key: 50 req/30s (much faster)

### Workflow not running

**Check:**
1. Workflow files are in `.github/workflows/`
2. Branch name matches (main vs master)
3. Repository has Actions enabled

### Large projects timeout

**Fix:** Increase timeout in workflow:

```yaml
steps:
  - name: Security Audit
    timeout-minutes: 30  # Default is 360
```

---

## 💡 Pro Tips

### 1. Branch Protection

Require security check before merge:

```
Settings → Branches → Branch protection rules
☑ Require status checks: security-audit
```

### 2. Scheduled Reports

Get weekly email summary:

```yaml
- name: Email Report
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    to: security@company.com
    subject: Weekly Security Report
    body: file://security-report.md
```

### 3. Monitor Trends

Keep historical data:

```yaml
- uses: actions/upload-artifact@v3
  with:
    retention-days: 90  # Keep for 3 months
```

---

## 📚 Next Steps

- **Customize workflows:** Edit YAML files
- **Add notifications:** Slack, email, Teams
- **Organization-wide:** [ORGANIZATION_SCANNING.md](ORGANIZATION_SCANNING.md)
- **Full CI/CD guide:** [CICD_INTEGRATION.md](CICD_INTEGRATION.md)

---

## 🆘 Need Help?

- [Full Documentation](../README.md)
- [CI/CD Integration Guide](CICD_INTEGRATION.md)
- [Troubleshooting](INSTALL.md#troubleshooting)
- [GitHub Issues](https://github.com/yourusername/Security-Auditor/issues)

---

**Setup complete! Your repo is now automatically monitored for security vulnerabilities! 🔒**
