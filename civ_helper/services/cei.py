"""
civ_helper/services/cei.py
"""
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from ..core.client import CivHTTPClient
from ..core.exceptions import CivOfflineError

URL_CEI = "https://electoris.cei.ci"

def check_voter_status(numero_cni: str, client: Optional[CivHTTPClient] = None) -> Dict[str, Any]:
    http = client or CivHTTPClient()
    
    res = http.post(f"{URL_CEI}/recherche", data={"cni": numero_cni})
    
    if res.status_code >= 400:
        raise CivOfflineError(f"Service de la CEI indisponible (Erreur {res.status_code}).")
        
    soup = BeautifulSoup(res.text, "html.parser")
    
    if "nginx" in soup.text.lower() or "not found" in soup.text.lower():
        raise CivOfflineError("Service électoral inactif.")

    if "bureau de vote" in soup.text.lower() or "inscrit" in soup.text.lower() or "trouvé" in soup.text.lower():
        result_box = soup.find("div", class_="result-box") or soup.find("table")
        msg = result_box.get_text(" ", strip=True) if result_box else soup.text[:500]
        return {"status": "success", "message": msg, "html_excerpt": str(result_box) if result_box else ""}

    return {"status": "unknown", "message": "Réponse inattendue du portail CEI.", "html_excerpt": res.text[:500]}
