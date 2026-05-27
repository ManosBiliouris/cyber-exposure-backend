from groq import Groq
import json
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.services.shodan_client import ShodanClient
from src.services.zoomeye_client import ZoomEyeClient
from src.services.fofa_client import FOFAClient
from src.services.credential_manager import credential_manager

load_dotenv()

SYSTEM_PROMPT = """
You are a cybersecurity OSINT expert. Your job is to convert natural language queries 
(in Greek or English) into search queries for 3 platforms: Shodan, ZoomEye, and FOFA.

Always respond with ONLY a valid JSON object, no explanation, no markdown, like this:
{
  "shodan": "apache port:80 country:GR",
  "zoomeye": "app:apache port:80 country:GR",
  "fofa": "app=\"Apache\" && port=\"80\" && country=\"GR\""
}

Rules:
- Shodan syntax: uses keywords like port:, country:, org:, product:, os:
- ZoomEye syntax: uses app:, port:, country:, os:, service:
- FOFA syntax: uses app=, port=, country=, protocol=, connected with && or ||, values in quotes
- Always try to infer country, port, service from context
- If the user mentions Greece, use country:GR (Shodan/ZoomEye) and country="GR" (FOFA)
"""

def get_groq_client():
    return Groq(api_key=credential_manager.get_key("groq"))

class LLMAgent:
    def __init__(self):
        self.shodan = ShodanClient()
        self.zoomeye = ZoomEyeClient()
        self.fofa = FOFAClient()

    def translate_query(self, natural_language: str) -> dict:
        client = get_groq_client()
        
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": natural_language}
                ],
                temperature=0.1,
            )
        except Exception as e:
            # Rate limit — blacklist and retry with next key
            if "429" in str(e) or "rate" in str(e).lower():
                current_key = credential_manager.get_key("groq")
                credential_manager.blacklist_key("groq", current_key)
                client = get_groq_client()
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": natural_language}
                    ],
                    temperature=0.1,
                )
            else:
                raise e

        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        queries = json.loads(raw.strip())
        return queries

    def run_parallel(self, natural_language: str) -> dict:
        queries = self.translate_query(natural_language)

        results = {
            "original_query": natural_language,
            "translated_queries": queries,
            "shodan": None,
            "zoomeye": None,
            "fofa": None,
            "errors": {}
        }

        def run_shodan():
            return self.shodan.run_single_query(queries["shodan"])

        def run_zoomeye():
            return self.zoomeye.run_single_query(queries["zoomeye"])

        def run_fofa():
            return self.fofa.run_single_query(queries["fofa"])

        tasks = {
            "shodan": run_shodan,
            "zoomeye": run_zoomeye,
            "fofa": run_fofa,
        }

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(fn): name for name, fn in tasks.items()}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    results[name] = future.result()
                except Exception as e:
                    results["errors"][name] = str(e)
                    results[name] = {"total": 0, "results": []}

        return results