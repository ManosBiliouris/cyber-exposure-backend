import requests
import os

class ShodanClient:
    def __init__(self):
        self.api_key = os.getenv("SHODAN_API_KEY")
        self.base_url = "https://api.shodan.io"

    def run_single_query(self, query: str):
        """
        Performs exactly ONE Shodan API request (1 credit).
        No loops, no retries, no pagination.
        """
        endpoint = f"{self.base_url}/shodan/host/search"

        params = {
            "key": self.api_key,
            "query": query
        }

        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("matches", []):
            results.append({
                "ip": item.get("ip_str"),
                "port": item.get("port"),
                "org": item.get("org"),
                "service": item.get("product"),
            })

        return {
            "raw_query": query,
            "total": len(results),
            "results": results
        }
