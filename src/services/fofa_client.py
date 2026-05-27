import requests
import base64
import os

class FOFAClient:
    def __init__(self):
        self.email = os.getenv("FOFA_EMAIL")
        self.api_key = os.getenv("FOFA_API_KEY")
        self.base_url = "https://fofa.info/api/v1"

    def run_single_query(self, query: str):
        endpoint = f"{self.base_url}/search/all"

        query_b64 = base64.b64encode(query.encode()).decode()

        params = {
            "email": self.email,
            "key": self.api_key,
            "qbase64": query_b64,
            "fields": "ip,port,org,protocol",
            "size": 20
        }

        response = requests.get(endpoint, params=params)
        data = response.json()

        # Print για debugging
        print(f"FOFA response: {data}")

        # Check για FOFA errors
        if not data.get("error", False) is False:
            print(f"FOFA error: {data.get('errmsg', 'Unknown error')}")
            return {"raw_query": query, "total": 0, "results": []}

        if data.get("errmsg"):
            print(f"FOFA errmsg: {data.get('errmsg')}")
            return {"raw_query": query, "total": 0, "results": []}

        results = []
        for item in data.get("results", []):
            results.append({
                "ip": item[0] if len(item) > 0 else None,
                "port": item[1] if len(item) > 1 else None,
                "org": item[2] if len(item) > 2 else None,
                "service": item[3] if len(item) > 3 else None,
            })

        return {
            "raw_query": query,
            "total": len(results),
            "results": results
        }