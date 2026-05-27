import requests
import os

class ZoomEyeClient:
    def __init__(self):
        self.api_key = os.getenv("ZOOMEYE_API_KEY")
        self.base_url = "https://api.zoomeye.org"

    def run_single_query(self, query: str):
        """
        Performs ONE ZoomEye search request.
        """
        endpoint = f"{self.base_url}/host/search"

        headers = {
            "API-KEY": self.api_key
        }

        params = {
            "query": query,
            "page": 1
        }

        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("matches", []):
            portinfo = item.get("portinfo", {})
            results.append({
                "ip": item.get("ip"),
                "port": portinfo.get("port"),
                "org": item.get("whois", {}).get("organization"),
                "service": portinfo.get("service"),
            })

        return {
            "raw_query": query,
            "total": len(results),
            "results": results
        }