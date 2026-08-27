"""
cei_services/scraper.py

Scraper pour vérifier l'inscription sur la liste électorale (CEI).
"""
from typing import Dict, Any, Optional
import urllib3
from requests import Session, RequestException
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL_CEI = "https://electoris.cei.ci"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}


def check_voter_status(numero_cni: str, session: Optional[Session] = None, timeout: int = 15) -> Dict[str, Any]:
    """
    Vérifie le statut d'inscription d'un électeur sur le portail de la CEI.
    """
    http = session or Session()
    try:
        # Souvent ces plateformes font un POST ou GET avec le numéro CNI ou récépissé
        res = http.post(f"{URL_CEI}/recherche", data={"cni": numero_cni}, headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
        
        if res.status_code >= 400:
            return {"status": "offline", "message": f"Service de la CEI indisponible (Erreur {res.status_code})."}
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        if "nginx" in soup.text.lower() or "not found" in soup.text.lower():
            return {"status": "offline", "message": "Service électoral inactif. Les serveurs sont souvent fermés en dehors des périodes d'élection."}

        if "bureau de vote" in soup.text.lower() or "inscrit" in soup.text.lower() or "trouvé" in soup.text.lower():
            result_box = soup.find("div", class_="result-box") or soup.find("table")
            msg = result_box.get_text(" ", strip=True) if result_box else soup.text[:500]
            return {"status": "success", "message": msg, "html_excerpt": str(result_box) if result_box else ""}

        return {"status": "unknown", "message": "Réponse inattendue du portail CEI.", "html_excerpt": res.text[:500]}
        
    except RequestException as e:
        return {"status": "offline", "message": f"Erreur de connexion (Serveur de la CEI hors ligne ou inaccessible) : {e}"}
