
I want to build this tool as given by the prompt below. 
Prompt:
The "Security Auditor" (CVE Intelligence)
The Corporate Story: Triage a massive list of software vulnerabilities to decide which ones matter to your specific stack.

The Public Proxy: NIST National Vulnerability Database (NVD) API.

Why: This is the official US government source for CVEs. It allows real-time JSON access to security data.

MCP Role: The MCP server ingests a dummy package.json you create. It then queries the NVD API for those specific versions and summarizes the severity specifically for an executive summary (ignoring low-priority noise).

Data Link: NIST NVD API (https://nvd.nist.gov/developers/vulnerabilities)

i want build this with Python as the main programming language
Show less