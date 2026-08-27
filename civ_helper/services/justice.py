"""
civ_helper/services/justice.py
"""
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from ..core.client import CivHTTPClient
from ..core.exceptions import CivOfflineError, CivAuthError

URL_JUSTICE = "https://www.e-justice.ci"

def check_demande_status(numero_demande: str, session_cookie: str = "", client: Optional[CivHTTPClient] = None) -> Dict[str, Any]:
    http = client or CivHTTPClient()
    headers = {}
    if session_cookie:
        headers["Cookie"] = session_cookie
        
    res = http.get(f"{URL_JUSTICE}/suivi?numero={numero_demande}", headers=headers)
    
    if res.status_code in [401, 403]:
        raise CivAuthError("Authentification requise. Cookie manquant ou expiré.")
        
    if res.status_code >= 400:
        raise CivOfflineError(f"Portail e-justice indisponible (Erreur {res.status_code}).")
        
    soup = BeautifulSoup(res.text, "html.parser")
    
    if "connexion" in soup.text.lower() or "connectez-vous" in soup.text.lower() or "mot de passe" in soup.text.lower():
        raise CivAuthError("Le portail requiert une connexion.")

    if "en cours" in soup.text.lower() or "disponible" in soup.text.lower() or "rejeté" in soup.text.lower():
        result_box = soup.find("div", class_="status-box") or soup.find("table")
        msg = result_box.get_text(" ", strip=True) if result_box else soup.text[:500]
        return {"status": "success", "message": msg, "html_excerpt": str(result_box) if result_box else ""}

    return {"status": "unknown", "message": "Réponse inattendue du portail e-justice.", "html_excerpt": res.text[:500]}
