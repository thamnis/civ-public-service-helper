"""
justice_services/scraper.py

Scraper pour vérifier le statut d'une demande sur le portail e-justice (Casier Judiciaire).
"""
from typing import Dict, Any, Optional
import urllib3
from requests import Session, RequestException
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL_JUSTICE = "https://www.e-justice.ci"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}


def check_demande_status(numero_demande: str, session_cookie: str = "", session: Optional[Session] = None, timeout: int = 15) -> Dict[str, Any]:
    """
    Vérifie le statut d'une demande de casier judiciaire sur e-justice.ci.
    
    Args:
        numero_demande (str): Le numéro de suivi de la demande.
        session_cookie (str): Cookie d'authentification si requis par le portail.
    """
    http = session or Session()
    try:
        headers = DEFAULT_HEADERS.copy()
        if session_cookie:
            headers["Cookie"] = session_cookie
            
        res = http.get(f"{URL_JUSTICE}/suivi?numero={numero_demande}", headers=headers, verify=False, timeout=timeout)
        
        if res.status_code == 401 or res.status_code == 403:
            return {"status": "error", "message": "Authentification requise. Veuillez fournir un cookie de session valide (--cookie)."}
            
        if res.status_code >= 400:
            return {"status": "offline", "message": f"Portail e-justice indisponible (Erreur {res.status_code})."}
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Vérification si on est redirigé vers une page de login
        if "connexion" in soup.text.lower() or "connectez-vous" in soup.text.lower() or "mot de passe" in soup.text.lower():
            return {"status": "error", "message": "Le portail requiert une connexion. Veuillez utiliser le flag --cookie avec une session valide."}

        # Analyse du statut
        if "en cours" in soup.text.lower() or "disponible" in soup.text.lower() or "rejeté" in soup.text.lower():
            result_box = soup.find("div", class_="status-box") or soup.find("table")
            msg = result_box.get_text(" ", strip=True) if result_box else soup.text[:500]
            return {"status": "success", "message": msg, "html_excerpt": str(result_box) if result_box else ""}

        return {"status": "unknown", "message": "Réponse inattendue du portail e-justice.", "html_excerpt": res.text[:500]}
        
    except RequestException as e:
        return {"status": "offline", "message": f"Erreur de connexion (Serveur e-justice hors ligne) : {e}"}
