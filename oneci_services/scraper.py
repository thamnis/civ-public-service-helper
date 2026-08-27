"""
oneci_services/scraper.py

Scraper pour les services de l'ONECI (Office National de l'État Civil et de l'Identification).
- Suivi du statut de production d'une CNI/CRC.
- Récupération d'un numéro de demande perdu.

⚠️ Ces plateformes sont sécurisées par reCAPTCHA v3. Si le token n'est pas fourni, le serveur peut bloquer la requête.
"""

from typing import Dict, Any, Optional
import urllib3
from bs4 import BeautifulSoup
from requests import Session, RequestException

# Désactiver les avertissements SSL pour les plateformes gouvernementales
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://statut.oneci.ci"
STATUT_URL = f"{BASE_URL}/statut-cni"
NUMERO_DEMANDE_URL = f"{BASE_URL}/numero-de-demande"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}


def _get_csrf_token(session: Session, url: str, timeout: int = 15) -> str:
    """Récupère le token CSRF caché dans le formulaire d'une page donnée."""
    res = session.get(url, headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    token_input = soup.find("input", attrs={"name": "csrf_token"})
    if token_input:
        return token_input.get("value", "")
    return ""


def check_cni_status(
    numero_demande: str,
    nom: str,
    date_naissance: str,
    titre: str = "CNI",
    recaptcha_token: str = "",
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Vérifie le statut de production d'une CNI ou CRC.

    Args:
        numero_demande (str): Le numéro de demande (10 à 14 caractères).
        nom (str): Nom de famille.
        date_naissance (str): Date de naissance au format YYYY-MM-DD.
        titre (str): "CNI" ou "CRC".
        recaptcha_token (str): Jeton reCAPTCHA optionnel pour contourner les protections.

    Returns:
        dict: Résultat contenant le statut extrait ou les messages d'erreur de la page.
    """
    http = session or Session()
    try:
        # 1. Fetch CSRF token
        csrf_token = _get_csrf_token(http, BASE_URL, timeout)

        # 2. Prepare Form Data
        data = {
            "titre": titre,
            "dnum": numero_demande.upper(),
            "nom": nom.upper(),
            "dnaiss": date_naissance,
            "csrf_token": csrf_token,
            "recaptcha_token": recaptcha_token,
        }

        # 3. Submit Form
        res = http.post(STATUT_URL, data=data, headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
        if res.status_code == 403:
            return {"status": "error", "message": "Accès refusé. Un recaptcha_token valide est probablement requis."}
            
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion : {e}"}

    soup = BeautifulSoup(res.text, "html.parser")
    
    # Analyze errors
    alerts = []
    for el in soup.find_all(['div', 'span', 'p'], class_=lambda c: c and any(k in str(c).lower() for k in ["danger", "error", "alert"])):
        c_str = str(el.get('class', '')).lower()
        if "success" in c_str or "info" in c_str:
            continue
        txt = el.get_text(" ", strip=True)
        if txt and txt not in alerts and txt != "*":
            alerts.append(txt)

    if alerts:
        return {
            "status": "error",
            "message": " | ".join(alerts)
        }

    # Analyze success status
    # ONECI returns the status in a specific div/alert structure on success
    success_div = soup.find("div", class_="alert-success")
    if success_div:
        return {
            "status": "success",
            "message": success_div.get_text(" ", strip=True)
        }

    # Check for general info/warning messages
    info_div = soup.find("div", class_=lambda c: c and "alert-info" in str(c))
    if info_div:
         return {
            "status": "success",
            "message": info_div.get_text(" ", strip=True)
        }

    # Fallback si le DOM n'est pas clair
    return {
        "status": "unknown",
        "message": "La requête a abouti mais le statut n'a pas pu être extrait de la page.",
        "html_excerpt": res.text[:500]
    }


def find_numero_demande(
    nom: str,
    prenoms: str,
    date_naissance: str,
    lieu_naissance: str,
    titre: str = "CNI",
    recaptcha_token: str = "",
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Recherche un numéro de demande perdu.

    Args:
        nom (str): Nom de famille.
        prenoms (str): Prénoms.
        date_naissance (str): Date de naissance au format YYYY-MM-DD.
        lieu_naissance (str): Lieu de naissance (doit correspondre exactement aux options ONECI).
        titre (str): "CNI" ou "CRC".
        recaptcha_token (str): Jeton reCAPTCHA.

    Returns:
        dict: Résultat de la recherche.
    """
    http = session or Session()
    try:
        csrf_token = _get_csrf_token(http, NUMERO_DEMANDE_URL, timeout)

        data = {
            "titre": titre,
            "nom": nom.upper(),
            "prenoms": prenoms.upper(),
            "dnaiss": date_naissance,
            "lnaiss": lieu_naissance.upper(),
            "csrf_token": csrf_token,
            "recaptcha_token": recaptcha_token,
        }

        res = http.post(NUMERO_DEMANDE_URL, data=data, headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
        if res.status_code == 403:
            return {"status": "error", "message": "Accès refusé. Un recaptcha_token valide est probablement requis."}
            
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion : {e}"}

    soup = BeautifulSoup(res.text, "html.parser")
    
    alerts = []
    for el in soup.find_all(['div', 'span', 'p'], class_=lambda c: c and any(k in str(c).lower() for k in ["danger", "error", "alert"])):
        c_str = str(el.get('class', '')).lower()
        if "success" in c_str or "info" in c_str:
            continue
        txt = el.get_text(" ", strip=True)
        if txt and txt not in alerts and txt != "*":
            alerts.append(txt)

    if alerts:
        return {
            "status": "error",
            "message": " | ".join(alerts)
        }

    success_div = soup.find("div", class_="alert-success")
    if success_div:
        return {
            "status": "success",
            "message": success_div.get_text(" ", strip=True)
        }

    return {
        "status": "unknown",
        "message": "La requête a abouti mais le numéro n'a pas pu être extrait de la page."
    }
