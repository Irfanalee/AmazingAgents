"""NVD API Client for querying CVE data."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, List, Optional
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field


class CVSSMetrics(BaseModel):
    """CVSS metrics for a vulnerability."""

    base_score: Optional[float] = None
    base_severity: Optional[str] = None
    exploitability_score: Optional[float] = None
    impact_score: Optional[float] = None
    vector_string: Optional[str] = None


class CVEData(BaseModel):
    """CVE vulnerability data."""

    cve_id: str
    description: str
    published_date: datetime
    last_modified_date: datetime
    cvss_v3: Optional[CVSSMetrics] = None
    cvss_v2: Optional[CVSSMetrics] = None
    references: List[str] = Field(default_factory=list)
    cpe_matches: List[str] = Field(default_factory=list)

    @property
    def severity(self) -> str:
        """Get the severity level (prefers CVSS v3 over v2)."""
        if self.cvss_v3 and self.cvss_v3.base_severity:
            return self.cvss_v3.base_severity
        if self.cvss_v2 and self.cvss_v2.base_severity:
            return self.cvss_v2.base_severity
        return "UNKNOWN"

    @property
    def score(self) -> Optional[float]:
        """Get the CVSS score (prefers v3 over v2)."""
        if self.cvss_v3 and self.cvss_v3.base_score:
            return self.cvss_v3.base_score
        if self.cvss_v2 and self.cvss_v2.base_score:
            return self.cvss_v2.base_score
        return None


class NVDClient:
    """Client for interacting with the NIST NVD API."""

    BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit: int = 5,
        timeout: int = 30
    ):
        """
        Initialize the NVD API client.

        Args:
            api_key: NVD API key (optional but recommended for higher rate limits)
            rate_limit: Requests per 30 seconds (5 without key, 50 with key)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.timeout = timeout
        self._last_request_time: Optional[datetime] = None
        self._request_count = 0

        headers = {"Accept": "application/json"}
        if api_key:
            headers["apiKey"] = api_key

        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
            follow_redirects=True
        )

    async def _rate_limit_wait(self):
        """Implement rate limiting to comply with NVD API requirements."""
        now = datetime.now()

        if self._last_request_time is None:
            self._last_request_time = now
            self._request_count = 1
            return

        time_since_first = (now - self._last_request_time).total_seconds()

        if time_since_first >= 30:
            self._last_request_time = now
            self._request_count = 1
            return

        if self._request_count >= self.rate_limit:
            wait_time = 30 - time_since_first
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self._last_request_time = datetime.now()
            self._request_count = 1
        else:
            self._request_count += 1

    def _parse_cvss_metrics(self, metrics_data: dict) -> Optional[CVSSMetrics]:
        """Parse CVSS metrics from NVD response."""
        if not metrics_data:
            return None

        cvss_data = metrics_data.get("cvssData", {})
        return CVSSMetrics(
            base_score=cvss_data.get("baseScore"),
            base_severity=cvss_data.get("baseSeverity"),
            exploitability_score=metrics_data.get("exploitabilityScore"),
            impact_score=metrics_data.get("impactScore"),
            vector_string=cvss_data.get("vectorString")
        )

    def _parse_cve(self, cve_item: dict) -> CVEData:
        """Parse a CVE item from the NVD API response."""
        cve = cve_item.get("cve", {})
        cve_id = cve.get("id", "UNKNOWN")

        # Extract description
        descriptions = cve.get("descriptions", [])
        description = next(
            (d.get("value", "") for d in descriptions if d.get("lang") == "en"),
            "No description available"
        )

        # Extract dates
        published = cve.get("published", datetime.now().isoformat())
        last_modified = cve.get("lastModified", published)

        # Extract CVSS metrics
        metrics = cve.get("metrics", {})
        cvss_v3 = None
        cvss_v2 = None

        if "cvssMetricV31" in metrics and metrics["cvssMetricV31"]:
            cvss_v3 = self._parse_cvss_metrics(metrics["cvssMetricV31"][0])
        elif "cvssMetricV30" in metrics and metrics["cvssMetricV30"]:
            cvss_v3 = self._parse_cvss_metrics(metrics["cvssMetricV30"][0])

        if "cvssMetricV2" in metrics and metrics["cvssMetricV2"]:
            cvss_v2 = self._parse_cvss_metrics(metrics["cvssMetricV2"][0])

        # Extract references
        references = [
            ref.get("url", "")
            for ref in cve.get("references", [])
        ]

        # Extract CPE matches (affected products)
        cpe_matches = []
        for config in cve.get("configurations", []):
            for node in config.get("nodes", []):
                for match in node.get("cpeMatch", []):
                    if match.get("vulnerable", False):
                        cpe_matches.append(match.get("criteria", ""))

        return CVEData(
            cve_id=cve_id,
            description=description,
            published_date=datetime.fromisoformat(published.replace("Z", "+00:00")),
            last_modified_date=datetime.fromisoformat(last_modified.replace("Z", "+00:00")),
            cvss_v3=cvss_v3,
            cvss_v2=cvss_v2,
            references=references,
            cpe_matches=cpe_matches
        )

    async def search_cves(
        self,
        keyword: Optional[str] = None,
        cpe_name: Optional[str] = None,
        cve_id: Optional[str] = None,
        published_start: Optional[datetime] = None,
        published_end: Optional[datetime] = None,
        cvss_v3_severity: Optional[str] = None,
        results_per_page: int = 2000,
        start_index: int = 0
    ) -> List[CVEData]:
        """
        Search for CVEs using various filters.

        Args:
            keyword: Search keyword in CVE descriptions
            cpe_name: CPE name to search for (e.g., "cpe:2.3:a:vendor:product:version")
            cve_id: Specific CVE ID to retrieve
            published_start: Start date for published date range
            published_end: End date for published date range
            cvss_v3_severity: Filter by CVSS v3 severity (LOW, MEDIUM, HIGH, CRITICAL)
            results_per_page: Number of results per page (max 2000)
            start_index: Starting index for pagination

        Returns:
            List of CVEData objects
        """
        await self._rate_limit_wait()

        params = {
            "resultsPerPage": min(results_per_page, 2000),
            "startIndex": start_index
        }

        if keyword:
            params["keywordSearch"] = keyword
        if cpe_name:
            params["cpeName"] = cpe_name
        if cve_id:
            params["cveId"] = cve_id
        if published_start:
            params["pubStartDate"] = published_start.isoformat()
        if published_end:
            params["pubEndDate"] = published_end.isoformat()
        if cvss_v3_severity:
            params["cvssV3Severity"] = cvss_v3_severity

        try:
            response = await self.client.get(
                self.BASE_URL,
                params=params
            )
            response.raise_for_status()
            data = response.json()

            vulnerabilities = data.get("vulnerabilities", [])
            return [self._parse_cve(item) for item in vulnerabilities]

        except httpx.HTTPError as e:
            raise Exception(f"NVD API request failed: {e}")

    async def get_cve_by_id(self, cve_id: str) -> Optional[CVEData]:
        """
        Get a specific CVE by its ID.

        Args:
            cve_id: CVE identifier (e.g., "CVE-2024-1234")

        Returns:
            CVEData object or None if not found
        """
        results = await self.search_cves(cve_id=cve_id)
        return results[0] if results else None

    async def search_by_product(
        self,
        vendor: str,
        product: str,
        version: Optional[str] = None,
        severity_filter: Optional[List[str]] = None
    ) -> List[CVEData]:
        """
        Search for CVEs affecting a specific product.

        Args:
            vendor: Vendor name (e.g., "nodejs")
            product: Product name (e.g., "node.js")
            version: Specific version (optional)
            severity_filter: List of severities to include (e.g., ["HIGH", "CRITICAL"])

        Returns:
            List of CVEData objects
        """
        # Construct CPE name pattern
        if version:
            keyword = f"{vendor} {product} {version}"
        else:
            keyword = f"{vendor} {product}"

        all_cves = []

        if severity_filter:
            for severity in severity_filter:
                cves = await self.search_cves(
                    keyword=keyword,
                    cvss_v3_severity=severity
                )
                all_cves.extend(cves)
        else:
            all_cves = await self.search_cves(keyword=keyword)

        return all_cves

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
