"""
civ_helper/services/directory.py

Module de gestion et de recherche du répertoire national des services publics et institutions ivoiriennes.
Inclut le monitoring de disponibilité en direct.
"""

import json
import os
import time
import unicodedata
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse

from ..core.client import CivHTTPClient
from ..core.exceptions import CivOfflineError

_DIRECTORY_CACHE: Optional[List[Dict[str, Any]]] = None

def _get_data_path() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(current_dir), "data", "directory.json")

def load_directory() -> List[Dict[str, Any]]:
    """Charge en mémoire le répertoire des services publics."""
    global _DIRECTORY_CACHE
    if _DIRECTORY_CACHE is not None:
        return _DIRECTORY_CACHE
        
    data_path = _get_data_path()
    if not os.path.exists(data_path):
        return []
        
    with open(data_path, "r", encoding="utf-8") as f:
        _DIRECTORY_CACHE = json.load(f)
    return _DIRECTORY_CACHE

def _normalize_text(text: str) -> str:
    """Supprime les accents et convertit en minuscules pour la recherche insensible."""
    if not text:
        return ""
    normalized = unicodedata.normalize('NFD', text)
    return "".join(c for c in normalized if unicodedata.category(c) != 'Mn').lower()

def get_services(
    query: Optional[str] = None,
    category: Optional[str] = None,
    is_eservice: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Recherche et filtre les services publics ivoiriens.
    """
    services = load_directory()
    filtered = services
    
    if is_eservice is not None:
        filtered = [s for s in filtered if s.get("is_eservice") == is_eservice]
        
    if category:
        norm_cat = _normalize_text(category)
        filtered = [
            s for s in filtered 
            if any(norm_cat in _normalize_text(c) for c in s.get("categories", []))
        ]
        
    if query:
        norm_q = _normalize_text(query)
        words = norm_q.split()
        
        def matches(s: Dict[str, Any]) -> bool:
            search_corpus = _normalize_text(
                f"{s.get('name', '')} {s.get('description', '')} {s.get('interest', '')} "
                f"{s.get('url', '')} {' '.join(s.get('categories', []))}"
            )
            return all(w in search_corpus for w in words)
            
        filtered = [s for s in filtered if matches(s)]
        
    total = len(filtered)
    results = filtered[offset : offset + limit]
    
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "services": results
    }

def get_service_by_id(service_id: int) -> Optional[Dict[str, Any]]:
    """Récupère une institution par son identifiant unique."""
    services = load_directory()
    for s in services:
        if s.get("id") == service_id:
            return s
    return None

def get_categories() -> List[Dict[str, Any]]:
    """Retourne la liste des catégories avec le nombre de services associés."""
    services = load_directory()
    cat_counts: Dict[str, int] = {}
    
    for s in services:
        for cat in s.get("categories", []):
            cat_clean = cat.strip()
            if cat_clean:
                cat_counts[cat_clean] = cat_counts.get(cat_clean, 0) + 1
                
    sorted_cats = sorted(cat_counts.items(), key=lambda x: (-x[1], x[0]))
    return [{"category": c, "count": count} for c, count in sorted_cats]

def get_e_services(limit: int = 50) -> List[Dict[str, Any]]:
    """Retourne la liste des démarches et portails e-services dématérialisés."""
    res = get_services(is_eservice=True, limit=limit)
    return res["services"]

def check_service_health(
    url_or_id: Union[str, int],
    client: Optional[CivHTTPClient] = None,
    timeout: int = 5
) -> Dict[str, Any]:
    """
    Teste la disponibilité et le temps de réponse d'un portail public en direct.
    """
    url = ""
    name = "Portail Public"
    
    if isinstance(url_or_id, int) or (isinstance(url_or_id, str) and url_or_id.isdigit()):
        s = get_service_by_id(int(url_or_id))
        if not s:
            raise ValueError(f"Service ID {url_or_id} introuvable.")
        url = s["url"]
        name = s["name"]
    else:
        url = str(url_or_id)
        if not url.startswith("http"):
            url = f"https://{url}"
            
    http = client or CivHTTPClient(timeout=timeout)
    start_time = time.time()
    
    try:
        res = http.get(url)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        is_online = (res.status_code < 400 or res.status_code in [401, 403])
        
        return {
            "name": name,
            "url": url,
            "status": "online" if is_online else "warning",
            "status_code": res.status_code,
            "response_time_ms": elapsed_ms,
            "message": f"En ligne (Code HTTP {res.status_code})" if is_online else f"Réponse HTTP {res.status_code}"
        }
    except Exception as e:
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "name": name,
            "url": url,
            "status": "offline",
            "status_code": 0,
            "response_time_ms": elapsed_ms,
            "message": f"Inaccessible ou timeout ({str(e)})"
        }
