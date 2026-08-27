"""
mfp_services/scraper.py

Scraper pour vérifier les résultats des concours de la Fonction Publique (MFP).
"""
from typing import Dict, Any, Optional
import urllib3
from requests import Session, RequestException
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Les sous-domaines varient selon l'année, ex: concours2026.fonctionpublique.gouv.ci ou espacecandidat.
URL_MFP_BASE = "https://www.fonctionpublique.gouv.ci"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}


def get_concours_result(num_inscription: str, session: Optional[Session] = None, timeout: int = 15) -> Dict[str, Any]:
    """
    Vérifie le résultat d'un concours de la fonction publique.
    """
    http = session or Session()
    try:
        # Souvent ces plateformes utilisent une structure d'URL ou un paramètre GET
        res = http.get(f"{URL_MFP_BASE}/resultats?numero={num_inscription}", headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
        
        if res.status_code >= 400:
            return {"status": "offline", "message": f"Portail MFP indisponible (Erreur {res.status_code})."}
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        if not res.text.strip():
            return {"status": "offline", "message": "Le serveur du MFP a renvoyé une réponse vide. Les résultats ne sont probablement pas publiés ou le serveur est restreint."}

        # Analyse du succès
        if "admis" in soup.text.lower() or "échec" in soup.text.lower() or "candidat" in soup.text.lower():
            result_box = soup.find("div", class_="result-box") or soup.find("table")
            msg = result_box.get_text(" ", strip=True) if result_box else soup.text[:500]
            return {"status": "success", "message": msg, "html_excerpt": str(result_box) if result_box else ""}

        return {"status": "unknown", "message": "Réponse inattendue du portail MFP. Il est possible que le numéro d'inscription soit invalide.", "html_excerpt": res.text[:500]}
        
    except RequestException as e:
        return {"status": "offline", "message": f"Erreur de connexion (Serveur MFP hors ligne) : {e}"}
