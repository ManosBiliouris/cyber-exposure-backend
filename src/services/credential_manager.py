import os
from itertools import cycle
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class CredentialManager:
    """
    Manages multiple API keys per service with round-robin rotation.
    When a key hits rate limit, automatically switches to the next one.
    """

    def __init__(self):
        self.credentials = {
            "shodan": self._load_keys("SHODAN_API_KEY"),
            "zoomeye": self._load_keys("ZOOMEYE_API_KEY"),
            "fofa_key": self._load_keys("FOFA_API_KEY"),
            "fofa_email": self._load_keys("FOFA_EMAIL"),
            "groq": self._load_keys("GROQ_API_KEY"),
        }

        # Create cycling iterators for round-robin
        self.cycles = {
            service: cycle(keys)
            for service, keys in self.credentials.items()
            if keys
        }

        # Track blacklisted keys (rate limited)
        self.blacklisted: dict = {service: set() for service in self.credentials}

    def _load_keys(self, env_prefix: str) -> List[str]:
        """
        Loads multiple keys from env variables.
        Supports KEY, KEY_2, KEY_3, etc.
        """
        keys = []
        # Load primary key
        primary = os.getenv(env_prefix)
        if primary:
            keys.append(primary)

        # Load additional keys (KEY_2, KEY_3, ...)
        i = 2
        while True:
            extra = os.getenv(f"{env_prefix}_{i}")
            if not extra:
                break
            keys.append(extra)
            i += 1

        return keys

    def get_key(self, service: str) -> Optional[str]:
        """
        Returns the next available key for a service.
        Skips blacklisted keys.
        """
        if service not in self.cycles:
            return None

        keys = self.credentials[service]
        if not keys:
            return None

        # Try each key once
        for _ in range(len(keys)):
            key = next(self.cycles[service])
            if key not in self.blacklisted[service]:
                return key

        # All keys blacklisted — clear blacklist and retry
        print(f"[CredentialManager] All {service} keys rate-limited, resetting...")
        self.blacklisted[service].clear()
        return next(self.cycles[service])

    def blacklist_key(self, service: str, key: str):
        """
        Marks a key as rate-limited temporarily.
        """
        print(f"[CredentialManager] Blacklisting {service} key: {key[:8]}...")
        self.blacklisted[service].add(key)

    def get_stats(self) -> dict:
        """
        Returns stats about available keys per service.
        """
        return {
            service: {
                "total": len(keys),
                "blacklisted": len(self.blacklisted.get(service, set())),
                "available": len(keys) - len(self.blacklisted.get(service, set())),
            }
            for service, keys in self.credentials.items()
        }

# Singleton instance
credential_manager = CredentialManager()