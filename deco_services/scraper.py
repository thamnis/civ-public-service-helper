"""
deco_services/scraper.py

Scraper pour récupérer les résultats d'examens (BEPC, CEPE) depuis les plateformes AGCE de la DECO.
"""
from typing import Dict, Any, Optional
import urllib3
from requests import Session, RequestException
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL_BEPC = "https://agce.exam-deco.org"
URL_CEPE = "https://agcepe.exam-deco.org"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}


def _check_exam_result(url: str, matricule: str, session: Optional[Session] = None, timeout: int = 15) -> Dict[str, Any]:
    """
    Vérifie le résultat d'un examen sur une plateforme AGCE (DECO).
    """
    http = session or Session()
    try:
        # Souvent ces plateformes font un POST simple avec 'matricule'
        res = http.post(f"{url}/resultat", data={"matricule": matricule}, headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
        
        # En dehors des périodes d'examen, le serveur peut retourner 404, 502, ou renvoyer la page Nginx
        if res.status_code >= 400:
            return {"status": "offline", "message": f"Service temporairement indisponible (Erreur {res.status_code}). Les résultats ne sont probablement pas en ligne."}
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Si on tombe sur la page par défaut de Nginx
        if "Welcome to nginx" in soup.text:
            return {"status": "offline", "message": "Service temporairement indisponible. Les serveurs de la DECO sont fermés en dehors des périodes d'examen."}

        # Analyse basique de succès (généralement un tableau ou un message de félicitations/échec)
        if "admis" in soup.text.lower() or "refusé" in soup.text.lower() or "échec" in soup.text.lower() or "ajourné" in soup.text.lower():
            # Extraction d'un éventuel bloc de résultat
            result_box = soup.find("div", class_="result-box") or soup.find("table")
            msg = result_box.get_text(" ", strip=True) if result_box else soup.text[:500]
            return {"status": "success", "message": msg, "html_excerpt": str(result_box) if result_box else ""}

        return {"status": "unknown", "message": "Réponse inattendue. Impossible de parser le résultat.", "html_excerpt": res.text[:500]}
        
    except RequestException as e:
        return {"status": "offline", "message": f"Erreur de connexion (serveur injoignable ou hors ligne) : {e}"}


def get_bepc_result(matricule: str, session: Optional[Session] = None, timeout: int = 15) -> Dict[str, Any]:
    """Récupère le résultat du BEPC via AGCE DECO."""
    return _check_exam_result(URL_BEPC, matricule, session, timeout)


def get_cepe_result(matricule: str, session: Optional[Session] = None, timeout: int = 15) -> Dict[str, Any]:
    """Récupère le résultat du CEPE via AGCEPE DECO."""
    return _check_exam_result(URL_CEPE, matricule, session, timeout)
