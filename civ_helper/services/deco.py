"""
civ_helper/services/deco.py
"""
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from ..core.client import CivHTTPClient
from ..core.exceptions import CivOfflineError, CivParseError

URL_BEPC = "https://agce.exam-deco.org"
URL_CEPE = "https://agcepe.exam-deco.org"

def _check_exam_result(url: str, matricule: str, client: Optional[CivHTTPClient] = None) -> Dict[str, Any]:
    http = client or CivHTTPClient()
    
    res = http.post(f"{url}/resultat", data={"matricule": matricule})
    
    if res.status_code >= 400:
        raise CivOfflineError(f"Service temporairement indisponible (Erreur {res.status_code}).")
        
    soup = BeautifulSoup(res.text, "html.parser")
    
    if "Welcome to nginx" in soup.text:
        raise CivOfflineError("Service temporairement indisponible (Nginx par défaut).")

    if "admis" in soup.text.lower() or "refusé" in soup.text.lower() or "échec" in soup.text.lower() or "ajourné" in soup.text.lower():
        result_box = soup.find("div", class_="result-box") or soup.find("table")
        msg = result_box.get_text(" ", strip=True) if result_box else soup.text[:500]
        return {"status": "success", "message": msg, "html_excerpt": str(result_box) if result_box else ""}

    return {"status": "unknown", "message": "Réponse inattendue. Impossible de parser le résultat.", "html_excerpt": res.text[:500]}


def get_bepc_result(matricule: str, client: Optional[CivHTTPClient] = None) -> Dict[str, Any]:
    return _check_exam_result(URL_BEPC, matricule, client)

def get_cepe_result(matricule: str, client: Optional[CivHTTPClient] = None) -> Dict[str, Any]:
    return _check_exam_result(URL_CEPE, matricule, client)
