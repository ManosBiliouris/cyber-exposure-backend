import requests
import os
from dotenv import load_dotenv
from src.services.credential_manager import credential_manager
from src.services.proxy_manager import proxy_manager

load_dotenv()

class ShodanClient:
    def __init__(self):
        self.base_url = "https://api.shodan.io"

    def run_single_query(self, query: str):
        endpoint = f"{self.base_url}/shodan/host/search"
        api_key = credential_manager.get_key("shodan")
        proxy = proxy_manager.get_proxy()

        params = {
            "key": api_key,
            "query": query
        }

        try:
            response = requests.get(endpoint, params=params, proxies=proxy, timeout=15)

            if response.status_code == 429:
                credential_manager.blacklist_key("shodan", api_key)
                proxy_manager.blacklist_proxy(proxy)
                api_key = credential_manager.get_key("shodan")
                proxy = proxy_manager.get_proxy()
                params["key"] = api_key
                response = requests.get(endpoint, params=params, proxies=proxy, timeout=15)

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

        except Exception as e:
            proxy_manager.blacklist_proxy(proxy)
            print(f"[Shodan] Error: {e}")
            return {"raw_query": query, "total": 0, "results": []}