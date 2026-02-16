# CI/CD Integration Guide

Complete guide for integrating Security Auditor into your CI/CD pipelines.

## 📋 Table of Contents

1. [GitHub Actions](#github-actions)
2. [GitLab CI](#gitlab-ci)
3. [Jenkins](#jenkins)
4. [CircleCI](#circleci)
5. [Azure Pipelines](#azure-pipelines)
6. [Configuration](#configuration)
7. [Best Practices](#best-practices)

---

## GitHub Actions

### Quick Start

Three pre-configured workflows are included in this repository:

```
.github/workflows/
├── security-audit-weekly.yml    # Scheduled weekly scans
├── security-audit-pr.yml        # Pull request checks
└── security-audit-manual.yml    # Manual trigger with options
```

### Setup Steps

#### 1. Add GitHub Secret

Go to repository **Settings → Secrets and variables → Actions → New repository secret**

```
Name: NVD_API_KEY
Value: your_nvd_api_key_here
```

Get your free API key: https://nvd.nist.gov/developers/request-an-api-key

#### 2. Enable Workflows

The workflows are ready to use! They will:

- **Weekly Audit**: Run every Monday at 9 AM UTC
- **PR Audit**: Run on pull requests that modify dependency files
- **Manual Audit**: Trigger from Actions tab with custom options

#### 3. Customize (Optional)

Edit `.github/workflows/security-audit-weekly.yml` to change schedule:

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Monday 9 AM
    # Change to:
    # - cron: '0 0 * * 0'  # Sunday midnight
    # - cron: '0 12 * * 1,4'  # Monday & Thursday noon
```

### Exit Codes

The CLI returns different exit codes based on findings:

- **0**: No critical or high vulnerabilities ✅
- **1**: High severity vulnerabilities found ⚠️
- **2**: Critical severity vulnerabilities found ❌

Use these in your workflows:

```yaml
- name: Security Audit
  run: |
    python -m security_auditor.cli audit package.json || EXIT_CODE=$?
    if [ $EXIT_CODE -eq 2 ]; then
      echo "Critical vulnerabilities found!"
      exit 1
    fi
```

### Notifications

#### Slack Integration

```yaml
- name: Slack Notification
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "🚨 Security vulnerabilities found in ${{ github.repository }}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Security Alert*\nVulnerabilities detected in the latest security scan.\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Details>"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

#### Email Notification

```yaml
- name: Send Email
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: Security Alert - ${{ github.repository }}
    to: security-team@company.com
    from: github-actions@company.com
    body: file://security-report.md
```

#### Microsoft Teams

```yaml
- name: Teams Notification
  if: failure()
  uses: aliencube/microsoft-teams-actions@v0.8.0
  with:
    webhook_uri: ${{ secrets.TEAMS_WEBHOOK_URL }}
    title: Security Vulnerabilities Detected
    summary: Security audit found vulnerabilities
    text: Check the workflow run for details
```

---

## GitLab CI

### `.gitlab-ci.yml`

```yaml
stages:
  - security

variables:
  PYTHON_VERSION: "3.10"

security_audit:
  stage: security
  image: python:${PYTHON_VERSION}

  before_script:
    - pip install -r requirements.txt

  script:
    - |
      EXIT_CODE=0

      if [ -f package.json ]; then
        python -m security_auditor.cli audit package.json \
          --severity CRITICAL HIGH \
          --format markdown \
          --output security-report-npm.md || EXIT_CODE=$?
      fi

      if [ -f requirements.txt ]; then
        python -m security_auditor.cli audit requirements.txt \
          --severity CRITICAL HIGH \
          --format markdown \
          --output security-report-python.md || EXIT_CODE=$?
      fi

      if [ $EXIT_CODE -eq 2 ]; then
        echo "Critical vulnerabilities found!"
        exit 1
      fi

  artifacts:
    paths:
      - security-report-*.md
    expire_in: 30 days
    when: always

  only:
    - schedules
    - merge_requests
    - main

# Scheduled scan (configure in GitLab UI: CI/CD > Schedules)
weekly_security_audit:
  extends: security_audit
  only:
    - schedules
```

### Setup

1. Add CI/CD variable: `Settings → CI/CD → Variables`
   - Key: `NVD_API_KEY`
   - Value: Your API key
   - Protected: Yes
   - Masked: Yes

2. Create schedule: `CI/CD → Schedules → New schedule`
   - Description: Weekly Security Audit
   - Interval Pattern: `0 9 * * 1` (Every Monday 9 AM)
   - Target Branch: main

---

## Jenkins

### Jenkinsfile

```groovy
pipeline {
    agent any

    environment {
        NVD_API_KEY = credentials('nvd-api-key')
    }

    triggers {
        // Weekly on Monday at 9 AM
        cron('0 9 * * 1')
    }

    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Security Audit - npm') {
            when {
                expression { fileExists('package.json') }
            }
            steps {
                script {
                    def exitCode = sh(
                        script: '''
                            python -m security_auditor.cli audit package.json \
                                --severity CRITICAL HIGH \
                                --format markdown \
                                --output security-report-npm.md
                        ''',
                        returnStatus: true
                    )

                    if (exitCode == 2) {
                        currentBuild.result = 'FAILURE'
                        error('Critical vulnerabilities found!')
                    }
                }
            }
        }

        stage('Security Audit - Python') {
            when {
                expression { fileExists('requirements.txt') }
            }
            steps {
                script {
                    def exitCode = sh(
                        script: '''
                            python -m security_auditor.cli audit requirements.txt \
                                --severity CRITICAL HIGH \
                                --format markdown \
                                --output security-report-python.md
                        ''',
                        returnStatus: true
                    )

                    if (exitCode == 2) {
                        currentBuild.result = 'FAILURE'
                        error('Critical vulnerabilities found!')
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'security-report-*.md', allowEmptyArchive: true
        }
        failure {
            emailext (
                subject: "Security Alert: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: '''${FILE,path="security-report-npm.md"}
                         ${FILE,path="security-report-python.md"}''',
                to: 'security-team@company.com'
            )
        }
    }
}
```

### Setup

1. Install plugins:
   - Pipeline
   - Email Extension
   - Credentials Binding

2. Add credentials:
   - Manage Jenkins → Credentials → Add Credentials
   - Kind: Secret text
   - ID: `nvd-api-key`
   - Secret: Your NVD API key

---

## CircleCI

### `.circleci/config.yml`

```yaml
version: 2.1

orbs:
  python: circleci/python@2.1.1

jobs:
  security-audit:
    docker:
      - image: cimg/python:3.10

    steps:
      - checkout

      - python/install-packages:
          pkg-manager: pip

      - run:
          name: Install Security Auditor
          command: pip install -r requirements.txt

      - run:
          name: Audit package.json
          command: |
            if [ -f package.json ]; then
              python -m security_auditor.cli audit package.json \
                --severity CRITICAL HIGH \
                --format json \
                --output security-report-npm.json
            fi

      - run:
          name: Audit requirements.txt
          command: |
            if [ -f requirements.txt ]; then
              python -m security_auditor.cli audit requirements.txt \
                --severity CRITICAL HIGH \
                --format json \
                --output security-report-python.json
            fi

      - store_artifacts:
          path: security-report-npm.json
          destination: npm-security-report

      - store_artifacts:
          path: security-report-python.json
          destination: python-security-report

workflows:
  weekly-security-audit:
    triggers:
      - schedule:
          cron: "0 9 * * 1"
          filters:
            branches:
              only: main
    jobs:
      - security-audit

  pr-security-check:
    jobs:
      - security-audit:
          filters:
            branches:
              ignore: main
```

### Setup

1. Add environment variable in CircleCI:
   - Project Settings → Environment Variables
   - Name: `NVD_API_KEY`
   - Value: Your API key

---

## Azure Pipelines

### `azure-pipelines.yml`

```yaml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - package.json
      - requirements.txt

schedules:
  - cron: "0 9 * * 1"
    displayName: Weekly Security Audit
    branches:
      include:
        - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.10'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '$(pythonVersion)'
    displayName: 'Use Python $(pythonVersion)'

  - script: |
      pip install -r requirements.txt
    displayName: 'Install dependencies'

  - script: |
      if [ -f package.json ]; then
        python -m security_auditor.cli audit package.json \
          --severity CRITICAL HIGH \
          --format markdown \
          --output $(Build.ArtifactStagingDirectory)/security-report-npm.md
      fi
    env:
      NVD_API_KEY: $(NVD_API_KEY)
    displayName: 'Audit package.json'
    continueOnError: true

  - script: |
      if [ -f requirements.txt ]; then
        python -m security_auditor.cli audit requirements.txt \
          --severity CRITICAL HIGH \
          --format markdown \
          --output $(Build.ArtifactStagingDirectory)/security-report-python.md
      fi
    env:
      NVD_API_KEY: $(NVD_API_KEY)
    displayName: 'Audit requirements.txt'
    continueOnError: true

  - task: PublishBuildArtifacts@1
    inputs:
      pathToPublish: '$(Build.ArtifactStagingDirectory)'
      artifactName: 'security-reports'
    displayName: 'Publish security reports'
```

### Setup

1. Add secret variable:
   - Pipelines → Edit → Variables → New variable
   - Name: `NVD_API_KEY`
   - Value: Your API key
   - Keep this value secret: ✓

---

## Configuration

### Environment Variables

```bash
# Required for optimal performance
NVD_API_KEY=your_api_key_here

# Optional
NVD_RATE_LIMIT=50        # Requests per 30 seconds
NVD_TIMEOUT=30           # Request timeout in seconds
```

### Common Options

```bash
# Severity filtering
--severity CRITICAL HIGH MEDIUM LOW

# Include development dependencies
--include-dev

# Time-based filtering
--days 30  # Only CVEs from last 30 days

# Output formats
--format text      # Terminal-friendly
--format markdown  # Documentation
--format json      # Machine-readable

# Save to file
--output report.md
```

---

## Best Practices

### 1. Schedule Regular Scans

```yaml
# Run weekly (Monday 9 AM)
cron: '0 9 * * 1'

# Run daily
cron: '0 9 * * *'

# Run twice weekly (Monday & Thursday)
cron: '0 9 * * 1,4'
```

### 2. Fail Fast on Critical

```bash
EXIT_CODE=0
python -m security_auditor.cli audit package.json || EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  echo "❌ Critical vulnerabilities - blocking deployment"
  exit 1
fi
```

### 3. Save Reports

```yaml
- uses: actions/upload-artifact@v3
  with:
    name: security-reports
    path: security-report-*.md
    retention-days: 90  # Keep for compliance
```

### 4. Progressive Severity

```yaml
# Development branches: All severities
--severity CRITICAL HIGH MEDIUM LOW

# Staging: Medium and above
--severity CRITICAL HIGH MEDIUM

# Production: Only critical
--severity CRITICAL
```

### 5. Rate Limiting

```bash
# Use API key for faster scans
NVD_API_KEY=your_key  # 50 req/30s

# Without key (slow)
# 5 req/30s - suitable for small projects only
```

### 6. Caching

```yaml
- name: Cache audit results
  uses: actions/cache@v3
  with:
    path: |
      ~/.cache/security-auditor
    key: security-audit-${{ hashFiles('**/package.json', '**/requirements.txt') }}
```

### 7. Branch Protection

Configure branch rules to require security checks:

```
Settings → Branches → Branch protection rules
☑ Require status checks to pass before merging
  ☑ security-audit
```

---

## Troubleshooting

### Rate Limit Errors

**Problem:** "Rate limit exceeded"

**Solution:**
1. Get an NVD API key (free)
2. Add to CI/CD secrets
3. Reduces scan time by 10x

### Timeout Errors

**Problem:** Scan times out

**Solution:**
```yaml
- name: Security Audit
  timeout-minutes: 30  # Increase timeout
  run: |
    python -m security_auditor.cli audit package.json
```

### Large Projects

**Problem:** Too many dependencies

**Solution:**
```bash
# Filter by severity
--severity CRITICAL HIGH

# Exclude dev dependencies
# (don't use --include-dev)

# Check recent CVEs only
--days 90
```

---

## Examples

### Block Merge on Critical

```yaml
- name: Security Check
  run: |
    python -m security_auditor.cli audit package.json
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 2 ]; then
      echo "::error::Critical vulnerabilities found"
      exit 1
    fi
```

### Create GitHub Issue

```yaml
- name: Create Issue
  if: failure()
  uses: actions/github-script@v6
  with:
    script: |
      const report = require('fs').readFileSync('security-report.json', 'utf8');
      const data = JSON.parse(report);

      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: `🚨 ${data.summary.actionable_vulnerabilities} Security Issues`,
        body: JSON.stringify(data, null, 2),
        labels: ['security', 'automated']
      });
```

### Multi-Repository Scan

```yaml
strategy:
  matrix:
    repo: [repo1, repo2, repo3]

steps:
  - uses: actions/checkout@v4
    with:
      repository: org/${{ matrix.repo }}

  - name: Audit
    run: python -m security_auditor.cli audit package.json
```

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [NVD API Key Request](https://nvd.nist.gov/developers/request-an-api-key)
- [Security Auditor CLI Guide](API_GUIDE.md)
- [Exit Codes Reference](../README.md#exit-codes)

---

**Need help?** Check [INDEX.md](INDEX.md) or open an issue on GitHub.
