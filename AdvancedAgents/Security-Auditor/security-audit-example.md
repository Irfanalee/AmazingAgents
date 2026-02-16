# Security Audit Executive Summary

**Analysis Date:** 2025-12-11 20:48:04
**Project:** example-app v1.0.0

## Overview

- **Packages Analyzed:** 6
- **Packages with Vulnerabilities:** 3
- **Total Vulnerabilities:** 2

## Severity Breakdown

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH     | 2 |
| MEDIUM   | 0 |
| LOW      | 0 |

## Risk Assessment

⚠️ **Risk Level: MEDIUM**

Limited critical/high severity vulnerabilities detected: 2

## Actionable Vulnerabilities (Critical & High)

### lodash

#### CVE-2020-8203 [HIGH]
- **CVSS Score:** 7.4
- **Published:** 2020-07-15
- **Description:** Prototype pollution attack when using _.zipObjectDeep in lodash before 4.17.20.

### moment

#### CVE-2022-24785 [HIGH]
- **CVSS Score:** 7.5
- **Published:** 2022-04-04
- **Description:** Moment.js is a JavaScript date library for parsing, validating, manipulating, and formatting dates. A path traversal vulnerability impacts npm (server) users of Moment.js between versions 1.0.1 and 2.29.1, especially if a user-provided locale string is directly used to switch moment locale. This problem is patched in 2.29.2, and the patch can be applied to all affected versions. As a workaround, sanitize the user-provided locale name before passing it to Moment.js.

## Recommendations

1. **IMMEDIATE:** Review and patch all CRITICAL and HIGH severity vulnerabilities
2. Update affected packages to latest secure versions
3. Implement automated dependency scanning in CI/CD pipeline
4. Schedule regular security audits