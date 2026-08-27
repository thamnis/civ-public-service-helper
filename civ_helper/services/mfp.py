"""
civ_helper/services/mfp.py
"""
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from ..core.client import CivHTTPClient
from ..core.exceptions import CivOfflineError

URL_MFP_BASE = "https://www.fonctionpublique.gouv.ci"

def get_concours_result(num_inscription: str, client: Optional[CivHTTPClient] = None) -> Dict[str, Any]:
    http = client or CivHTTPClient()
    
    res = http.get(f"{URL_MFP_BASE}/resultats?numero={num_inscription}")
    
    if res.status_code >= 400:
        raise CivOfflineError(f"Portail MFP indisponible (Erreur {res.status_code}).")
        
    soup = BeautifulSoup(res.text, "html.parser")
    
    if not res.text.strip():
        raise CivOfflineError("Le serveur du MFP a renvoyé une réponse vide.")

    if "admis" in soup.text.lower() or "échec" in soup.text.lower() or "candidat" in soup.text.lower():
        result_box = soup.find("div", class_="result-box") or soup.find("table")
        msg = result_box.get_text(" ", strip=True) if result_box else soup.text[:500]
        return {"status": "success", "message": msg, "html_excerpt": str(result_box) if result_box else ""}

    return {"status": "unknown", "message": "Réponse inattendue du portail MFP.", "html_excerpt": res.text[:500]}
