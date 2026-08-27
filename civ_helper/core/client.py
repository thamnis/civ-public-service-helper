"""
civ_helper/core/client.py

Client HTTP unifié pour tous les services de civ-public-service-helper.
"""

import urllib3
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional

from .exceptions import CivOfflineError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

class CivHTTPClient:
    """Client HTTP avec gestion automatique des retries et contournement SSL."""
    
    def __init__(self, timeout: int = 15, retries: int = 3):
        self.timeout = timeout
        self.session = Session()
        
        # Configuration des Retries (relance automatique si erreur 500, 502, 503, 504)
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            "User-Agent": DEFAULT_USER_AGENT
        })

    def get(self, url: str, **kwargs):
        kwargs.setdefault("verify", False)
        kwargs.setdefault("timeout", self.timeout)
        try:
            return self.session.get(url, **kwargs)
        except Exception as e:
            raise CivOfflineError(f"Erreur de connexion GET à {url} : {e}")

    def post(self, url: str, **kwargs):
        kwargs.setdefault("verify", False)
        kwargs.setdefault("timeout", self.timeout)
        try:
            return self.session.post(url, **kwargs)
        except Exception as e:
            raise CivOfflineError(f"Erreur de connexion POST à {url} : {e}")
