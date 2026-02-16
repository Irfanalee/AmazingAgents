# Organization-Wide Security Scanning

Guide for scanning multiple repositories across your GitHub organization.

## 🏢 Overview

This guide shows how to set up automated security scanning for all repositories in your organization.

## 🎯 Approaches

### 1. Centralized Scanner Bot
### 2. GitHub App Integration
### 3. Organization Workflow
### 4. Scheduled Lambda/Cloud Function

---

## Approach 1: Centralized Scanner Bot

### Python Script

Create `org_scanner.py`:

```python
#!/usr/bin/env python3
"""Organization-wide security scanner."""

import asyncio
import os
from datetime import datetime
from github import Github
from security_auditor.nvd_client import NVDClient
from security_auditor.package_parser import PackageParser
from security_auditor.analyzer import VulnerabilityAnalyzer
from security_auditor.report import ExecutiveSummaryGenerator


async def scan_repository(repo, nvd_client):
    """Scan a single repository for vulnerabilities."""
    print(f"Scanning {repo.full_name}...")

    results = {
        "repo": repo.full_name,
        "vulnerabilities": [],
        "scanned_files": []
    }

    # Check for package.json
    try:
        package_file = repo.get_contents("package.json")
        content = package_file.decoded_content

        # Save temporarily
        with open("/tmp/package.json", "wb") as f:
            f.write(content)

        # Analyze
        manifest = PackageParser.parse_package_json("/tmp/package.json")
        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=["CRITICAL", "HIGH"]
        )

        result = await analyzer.analyze_manifest(manifest)
        results["scanned_files"].append("package.json")

        if result.severity_stats.actionable > 0:
            results["vulnerabilities"].append({
                "file": "package.json",
                "critical": result.severity_stats.critical,
                "high": result.severity_stats.high,
                "total": result.severity_stats.total
            })

            # Create issue
            report = ExecutiveSummaryGenerator.generate_markdown_summary(result)
            repo.create_issue(
                title=f"🚨 {result.severity_stats.actionable} Security Vulnerabilities Found",
                body=report,
                labels=["security", "automated", "vulnerability"]
            )
            print(f"  ⚠️  Created issue for {repo.full_name}")

    except Exception as e:
        print(f"  ℹ️  No package.json or error: {e}")

    # Check for requirements.txt
    try:
        req_file = repo.get_contents("requirements.txt")
        content = req_file.decoded_content

        with open("/tmp/requirements.txt", "wb") as f:
            f.write(content)

        manifest = PackageParser.parse_requirements_txt("/tmp/requirements.txt")
        analyzer = VulnerabilityAnalyzer(
            nvd_client=nvd_client,
            severity_filter=["CRITICAL", "HIGH"]
        )

        result = await analyzer.analyze_manifest(manifest)
        results["scanned_files"].append("requirements.txt")

        if result.severity_stats.actionable > 0:
            results["vulnerabilities"].append({
                "file": "requirements.txt",
                "critical": result.severity_stats.critical,
                "high": result.severity_stats.high,
                "total": result.severity_stats.total
            })

            report = ExecutiveSummaryGenerator.generate_markdown_summary(result)
            repo.create_issue(
                title=f"🚨 {result.severity_stats.actionable} Python Security Vulnerabilities",
                body=report,
                labels=["security", "automated", "python"]
            )
            print(f"  ⚠️  Created Python issue for {repo.full_name}")

    except Exception as e:
        print(f"  ℹ️  No requirements.txt or error: {e}")

    return results


async def main():
    """Main scanner function."""
    print("=" * 80)
    print("Organization Security Scanner")
    print("=" * 80)
    print()

    # Initialize GitHub
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set")
        return

    g = Github(github_token)

    # Get organization
    org_name = os.getenv("GITHUB_ORG")
    if not org_name:
        print("Error: GITHUB_ORG environment variable not set")
        return

    org = g.get_organization(org_name)
    print(f"Organization: {org.name}")
    print()

    # Initialize NVD client
    async with NVDClient(api_key=os.getenv("NVD_API_KEY")) as nvd_client:
        print(f"NVD Client initialized")
        print()

        all_results = []
        repos = list(org.get_repos())

        print(f"Found {len(repos)} repositories")
        print()

        # Scan each repository
        for repo in repos:
            # Skip archived repos
            if repo.archived:
                print(f"Skipping archived repo: {repo.full_name}")
                continue

            try:
                result = await scan_repository(repo, nvd_client)
                all_results.append(result)
            except Exception as e:
                print(f"Error scanning {repo.full_name}: {e}")

        # Generate summary
        print()
        print("=" * 80)
        print("SCAN SUMMARY")
        print("=" * 80)

        total_repos = len(all_results)
        repos_with_vulns = len([r for r in all_results if r["vulnerabilities"]])

        print(f"Repositories scanned: {total_repos}")
        print(f"Repositories with vulnerabilities: {repos_with_vulns}")
        print()

        if repos_with_vulns > 0:
            print("Affected Repositories:")
            for result in all_results:
                if result["vulnerabilities"]:
                    print(f"  - {result['repo']}")
                    for vuln in result["vulnerabilities"]:
                        print(f"    {vuln['file']}: {vuln['critical']} CRITICAL, {vuln['high']} HIGH")


if __name__ == "__main__":
    asyncio.run(main())
```

### GitHub Action for Org Scanner

`.github/workflows/org-scanner.yml`:

```yaml
name: Organization Security Scanner

on:
  schedule:
    - cron: '0 2 * * 1'  # Monday 2 AM
  workflow_dispatch:

jobs:
  scan-organization:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Security Auditor
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install PyGithub

      - name: Run Organization Scan
        env:
          GITHUB_TOKEN: ${{ secrets.ORG_ACCESS_TOKEN }}
          GITHUB_ORG: ${{ secrets.ORG_NAME }}
          NVD_API_KEY: ${{ secrets.NVD_API_KEY }}
        run: |
          python org_scanner.py

      - name: Upload scan results
        uses: actions/upload-artifact@v3
        with:
          name: org-scan-results
          path: scan-results-*.json
```

### Setup

1. Create a GitHub Personal Access Token:
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token
   - Scopes: `repo`, `read:org`

2. Add secrets to a central repository:
   - `ORG_ACCESS_TOKEN`: Your PAT
   - `ORG_NAME`: Your organization name
   - `NVD_API_KEY`: Your NVD API key

---

## Approach 2: Organization-Level Workflow

Use GitHub's organization-level workflows (Enterprise feature):

### `.github/workflows/security-audit.yml` (in `.github` repo)

```yaml
name: Organization Security Audit

on:
  schedule:
    - cron: '0 9 * * 1'
  workflow_dispatch:
    inputs:
      repositories:
        description: 'Comma-separated repo names (or "all")'
        required: false
        default: 'all'

jobs:
  get-repos:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}

    steps:
      - id: set-matrix
        run: |
          # Get all repos using GitHub API
          REPOS=$(gh api orgs/${{ github.repository_owner }}/repos \
            --paginate \
            --jq '[.[] | select(.archived == false) | .name]')

          echo "matrix=$REPOS" >> $GITHUB_OUTPUT
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  scan-repos:
    needs: get-repos
    runs-on: ubuntu-latest

    strategy:
      matrix:
        repo: ${{ fromJson(needs.get-repos.outputs.matrix) }}
      fail-fast: false

    steps:
      - name: Checkout target repository
        uses: actions/checkout@v4
        with:
          repository: ${{ github.repository_owner }}/${{ matrix.repo }}

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Security Auditor
        run: |
          pip install git+https://github.com/yourusername/Security-Auditor.git

      - name: Run Security Audit
        env:
          NVD_API_KEY: ${{ secrets.NVD_API_KEY }}
        run: |
          for file in package.json requirements.txt; do
            if [ -f "$file" ]; then
              python -m security_auditor.cli audit "$file" \
                --severity CRITICAL HIGH \
                --format markdown \
                --output "audit-$file.md"
            fi
          done

      - name: Create issue if vulnerabilities found
        if: hashFiles('audit-*.md') != ''
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.ORG_ACCESS_TOKEN }}
          script: |
            const fs = require('fs');
            const files = ['audit-package.json.md', 'audit-requirements.txt.md'];

            let body = '## 🚨 Security Vulnerabilities Detected\n\n';
            let hasVulns = false;

            for (const file of files) {
              if (fs.existsSync(file)) {
                const content = fs.readFileSync(file, 'utf8');
                if (content.includes('CRITICAL') || content.includes('HIGH')) {
                  body += content + '\n\n---\n\n';
                  hasVulns = true;
                }
              }
            }

            if (hasVulns) {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: '${{ matrix.repo }}',
                title: '🚨 Security Vulnerabilities Detected',
                body: body,
                labels: ['security', 'automated']
              });
            }
```

---

## Approach 3: Dashboard Integration

### Centralized Dashboard

Create a dashboard that aggregates results:

```python
# dashboard.py
from flask import Flask, render_template
import json
from pathlib import Path

app = Flask(__name__)

@app.route('/')
def index():
    """Display security dashboard."""
    results_dir = Path("scan-results")
    all_results = []

    for result_file in results_dir.glob("*.json"):
        with open(result_file) as f:
            data = json.load(f)
            all_results.append(data)

    # Sort by severity
    all_results.sort(
        key=lambda x: (
            x.get('severity_breakdown', {}).get('critical', 0),
            x.get('severity_breakdown', {}).get('high', 0)
        ),
        reverse=True
    )

    return render_template('dashboard.html', results=all_results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Dashboard Template

```html
<!-- templates/dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Security Dashboard</title>
    <style>
        .critical { background: #ff4444; color: white; }
        .high { background: #ff9933; color: white; }
        .medium { background: #ffcc00; }
        .low { background: #66cc66; }
    </style>
</head>
<body>
    <h1>Organization Security Dashboard</h1>

    <div class="summary">
        <p>Total Repositories: {{ results|length }}</p>
        <p>With Critical: {{ results|selectattr('severity_breakdown.critical', '>', 0)|list|length }}</p>
        <p>With High: {{ results|selectattr('severity_breakdown.high', '>', 0)|list|length }}</p>
    </div>

    <table>
        <thead>
            <tr>
                <th>Repository</th>
                <th>Critical</th>
                <th>High</th>
                <th>Medium</th>
                <th>Low</th>
                <th>Last Scan</th>
            </tr>
        </thead>
        <tbody>
        {% for result in results %}
            <tr>
                <td>{{ result.project.name }}</td>
                <td class="critical">{{ result.severity_breakdown.critical }}</td>
                <td class="high">{{ result.severity_breakdown.high }}</td>
                <td class="medium">{{ result.severity_breakdown.medium }}</td>
                <td class="low">{{ result.severity_breakdown.low }}</td>
                <td>{{ result.analysis_date }}</td>
            </tr>
        {% endfor %}
        </tbody>
    </table>
</body>
</html>
```

---

## Best Practices

### 1. Rate Limiting

Scan repos in batches to avoid API limits:

```python
# Scan 10 repos at a time
import asyncio

async def scan_batch(repos, nvd_client):
    tasks = [scan_repository(repo, nvd_client) for repo in repos]
    return await asyncio.gather(*tasks)

# Process in batches
batch_size = 10
for i in range(0, len(repos), batch_size):
    batch = repos[i:i + batch_size]
    await scan_batch(batch, nvd_client)
    await asyncio.sleep(60)  # Wait between batches
```

### 2. Filtering

Skip certain repositories:

```python
# Skip forks, archived, or specific repos
exclude_repos = ['docs-repo', 'archived-project']

for repo in org.get_repos():
    if repo.fork or repo.archived or repo.name in exclude_repos:
        continue

    await scan_repository(repo, nvd_client)
```

### 3. Reporting

Generate organization-wide report:

```python
# Generate weekly report
report = {
    "date": datetime.now().isoformat(),
    "total_repos": len(all_results),
    "repos_with_vulns": repos_with_vulns,
    "total_critical": sum(r.get('critical', 0) for r in all_results),
    "total_high": sum(r.get('high', 0) for r in all_results),
    "details": all_results
}

with open(f"org-report-{datetime.now().date()}.json", "w") as f:
    json.dump(report, f, indent=2)
```

---

## Troubleshooting

### GitHub API Rate Limits

Use authenticated requests and check limits:

```python
g = Github(token)
rate_limit = g.get_rate_limit()
print(f"Remaining: {rate_limit.core.remaining}/{rate_limit.core.limit}")
```

### Large Organizations

For 100+ repos, use pagination and caching:

```python
# Cache results
import pickle

cache_file = "scan-cache.pkl"

if os.path.exists(cache_file):
    with open(cache_file, "rb") as f:
        cached_results = pickle.load(f)
else:
    cached_results = {}

# Update cache after scan
with open(cache_file, "wb") as f:
    pickle.dump(all_results, f)
```

---

## Resources

- [PyGithub Documentation](https://pygithub.readthedocs.io/)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Organization Workflows](https://docs.github.com/en/actions/using-workflows/creating-starter-workflows-for-your-organization)

---

**Next:** [CICD_INTEGRATION.md](CICD_INTEGRATION.md) for single-repo setup
