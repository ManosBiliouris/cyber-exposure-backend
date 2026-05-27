import os
import requests
import random
from dotenv import load_dotenv

load_dotenv()

class ProxyManager:
    """
    Manages a pool of proxies for API requests.
    Supports HTTP/HTTPS/SOCKS5 proxies.
    Automatically rotates and blacklists failed proxies.
    """

    def __init__(self):
        self.proxies = self._load_proxies()
        self.blacklisted = set()
        self.current_index = 0

    def _load_proxies(self) -> list:
        """
        Loads proxies from env variables.
        Format: PROXY_1=http://user:pass@host:port
        """
        proxies = []
        i = 1
        while True:
            proxy = os.getenv(f"PROXY_{i}")
            if not proxy:
                break
            proxies.append(proxy)
            i += 1

        if proxies:
            print(f"[ProxyManager] Loaded {len(proxies)} proxies")
        else:
            print("[ProxyManager] No proxies configured — using direct connection")

        return proxies

    def get_proxy(self) -> dict | None:
        """
        Returns a random available proxy dict for requests library.
        Returns None if no proxies configured (direct connection).
        """
        available = [p for p in self.proxies if p not in self.blacklisted]

        if not available:
            if self.proxies:
                # All blacklisted — reset
                print("[ProxyManager] All proxies failed, resetting blacklist...")
                self.blacklisted.clear()
                available = self.proxies
            else:
                return None

        proxy = random.choice(available)
        return {
            "http": proxy,
            "https": proxy,
        }

    def blacklist_proxy(self, proxy_dict: dict):
        """
        Marks a proxy as failed.
        """
        if proxy_dict:
            proxy_url = proxy_dict.get("http") or proxy_dict.get("https")
            if proxy_url:
                print(f"[ProxyManager] Blacklisting proxy: {proxy_url[:20]}...")
                self.blacklisted.add(proxy_url)

    def get_stats(self) -> dict:
        return {
            "total": len(self.proxies),
            "blacklisted": len(self.blacklisted),
            "available": len(self.proxies) - len(self.blacklisted),
            "using_direct": len(self.proxies) == 0,
        }

# Singleton
proxy_manager = ProxyManager()