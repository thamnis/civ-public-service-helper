"""
civ_helper/services/oneci.py
"""
import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

from ..core.client import CivHTTPClient
from ..core.exceptions import CivOfflineError, CivCaptchaError

URL_ONECI = "https://statut.oneci.ci"

def extract_csrf(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    token_input = soup.find("input", {"name": "_token"})
    if token_input:
        return token_input.get("value", "")
    return ""

def check_cni_status(numero_demande: str, nom: str, date_naissance: str, titre: str = "CNI", recaptcha_token: str = "", client: Optional[CivHTTPClient] = None) -> Dict[str, Any]:
    http = client or CivHTTPClient()
    
    # 1. Get CSRF Token
    res_get = http.get(URL_ONECI)
    if res_get.status_code >= 400:
        raise CivOfflineError(f"ONECI indisponible ({res_get.status_code})")
        
    csrf = extract_csrf(res_get.text)
    
    # 2. Post Data
    payload = {
        "_token": csrf,
        "titre": titre,
        "numero_demande": numero_demande,
        "nom": nom,
        "date_naissance": date_naissance
    }
    
    if recaptcha_token:
        payload["g-recaptcha-response"] = recaptcha_token
        
    res_post = http.post(URL_ONECI, data=payload)
    
    if res_post.status_code == 403 or "recaptcha" in res_post.text.lower():
        raise CivCaptchaError("Le serveur ONECI a bloqué la requête. Un token recaptcha_token est requis.")
        
    soup = BeautifulSoup(res_post.text, "html.parser")
    alert = soup.find("div", class_=re.compile("alert-.*"))
    if alert:
        return {"status": "success", "message": alert.get_text(strip=True)}
        
    return {"status": "unknown", "message": "Statut introuvable.", "html": res_post.text[:200]}


def find_numero_demande(nom: str, prenoms: str, date_naissance: str, lieu_naissance: str, titre: str = "CNI", recaptcha_token: str = "", client: Optional[CivHTTPClient] = None) -> Dict[str, Any]:
    http = client or CivHTTPClient()
    
    res_get = http.get(f"{URL_ONECI}/rechercher-numero-demande")
    if res_get.status_code >= 400:
        raise CivOfflineError(f"ONECI indisponible ({res_get.status_code})")
        
    csrf = extract_csrf(res_get.text)
    
    payload = {
        "_token": csrf,
        "titre": titre,
        "nom": nom,
        "prenoms": prenoms,
        "date_naissance": date_naissance,
        "lieu_naissance": lieu_naissance
    }
    
    if recaptcha_token:
        payload["g-recaptcha-response"] = recaptcha_token
        
    res_post = http.post(f"{URL_ONECI}/rechercher-numero-demande", data=payload)
    
    if res_post.status_code == 403 or "recaptcha" in res_post.text.lower():
        raise CivCaptchaError("Le serveur ONECI a bloqué la requête. Un token recaptcha_token est requis.")
        
    soup = BeautifulSoup(res_post.text, "html.parser")
    alert = soup.find("div", class_=re.compile("alert-.*"))
    if alert:
        return {"status": "success", "message": alert.get_text(strip=True)}
        
    return {"status": "unknown", "message": "Statut introuvable.", "html": res_post.text[:200]}
