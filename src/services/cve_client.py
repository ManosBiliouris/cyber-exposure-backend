import requests
import os

class CVEClient:
    def __init__(self):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    def search_by_keyword(self, keyword: str, max_results: int = 5) -> list:
        """
        Search NVD for CVEs related to a keyword (e.g. 'Apache httpd', 'RDP')
        Free API, no key needed.
        """
        try:
            params = {
                "keywordSearch": keyword,
                "resultsPerPage": max_results,
            }
            headers = {"User-Agent": "CyberKill-Platform/1.0"}
            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            cves = []
            for item in data.get("vulnerabilities", []):
                cve = item.get("cve", {})
                cve_id = cve.get("id", "")
                descriptions = cve.get("descriptions", [])
                description = next(
                    (d["value"] for d in descriptions if d["lang"] == "en"),
                    "No description available"
                )
                metrics = cve.get("metrics", {})
                cvss_score = 0.0
                severity = "medium"

                # Try CVSSv3 first, then v2
                if "cvssMetricV31" in metrics:
                    cvss_data = metrics["cvssMetricV31"][0]["cvssData"]
                    cvss_score = cvss_data.get("baseScore", 0.0)
                    severity = cvss_data.get("baseSeverity", "MEDIUM").lower()
                elif "cvssMetricV30" in metrics:
                    cvss_data = metrics["cvssMetricV30"][0]["cvssData"]
                    cvss_score = cvss_data.get("baseScore", 0.0)
                    severity = cvss_data.get("baseSeverity", "MEDIUM").lower()
                elif "cvssMetricV2" in metrics:
                    cvss_data = metrics["cvssMetricV2"][0]["cvssData"]
                    cvss_score = cvss_data.get("baseScore", 0.0)
                    severity = "high" if cvss_score >= 7 else "medium" if cvss_score >= 4 else "low"

                cves.append({
                    "cve_id": cve_id,
                    "description": description[:300],
                    "cvss_score": cvss_score,
                    "severity": severity,
                })

            return cves

        except Exception as e:
            print(f"CVE search error: {e}")
            return []