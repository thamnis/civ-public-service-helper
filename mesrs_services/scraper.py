"""
mesrs_services/scraper.py

Module d'interrogation du portail officiel du MESRS (Ministère de l'Enseignement Supérieur
et de la Recherche Scientifique de Côte d'Ivoire) : https://inscription.mesrs-ci.net/
Permet de :
- Vérifier la validité des paiements d'inscription / réinscription étudiante.
- Consulter le catalogue des demandes d'actes d'examen DEXCO (authentifications, relevés, diplômes).
- Récupérer les actualités et annonces flash officielles (tickers).
"""

from typing import Dict, Any, List, Optional
import os
import urllib3
from bs4 import BeautifulSoup
from requests import Session, RequestException

# Désactiver les avertissements SSL pour les plateformes gouvernementales
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://inscription.mesrs-ci.net"
PAYMENT_VERIFY_URL = f"{BASE_URL}/verifier/paiement"
DEXCO_URL = f"{BASE_URL}/dexco"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}

DEXCO_DEMANDE_TYPES = {
    "dexco_dmd_auth_diplome": "Demande d'Authentification de diplôme",
    "dexco_dmd_diplome": "Demande de Diplôme définitif (BTS)",
    "dexco_dmd_edition_releve_bts": "Demande d'Édition de relevé de notes BTS",
    "dexco_dmd_attest_usage_admin": "Demande d'Attestation à usage administratif",
    "dexco_dmd_attest_usage_admissibilite": "Demande d'Attestation d'admissibilité",
}


def verify_mesrs_payment(
    matricule_mesrs: str,
    code_paiement: str,
    numero_paiement: str,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Vérifie un paiement d'inscription ou de réinscription universitaire auprès du MESRS.

    Args:
        matricule_mesrs (str): Matricule MESRS de l'étudiant (ex: "AAAB19920001").
        code_paiement (str): Référence ou code de la transaction de paiement (ex: "1502168548958751").
        numero_paiement (str): Numéro de téléphone ou identifiant de paiement (ex: "0102030405").
        session (Session, optional): Session HTTP.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Résultat de la vérification (statut, validité, détails ou message d'erreur).
    """
    mat = str(matricule_mesrs).strip().upper()
    code = str(code_paiement).strip()
    num = str(numero_paiement).strip()

    if not mat:
        return {"status": "error", "message": "Le matricule MESRS est obligatoire.", "is_valid": False}
    if not code:
        return {"status": "error", "message": "Le code de paiement est obligatoire.", "is_valid": False}
    if not num:
        return {"status": "error", "message": "Le numéro de paiement est obligatoire.", "is_valid": False}

    http = session or Session()
    payload = {
        "matricule_mesrs": mat,
        "code_paiement": code,
        "numero_paiement": num,
    }

    try:
        res = http.post(
            PAYMENT_VERIFY_URL,
            data=payload,
            headers=DEFAULT_HEADERS,
            verify=False,
            timeout=timeout,
        )
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion au serveur MESRS : {e}", "is_valid": False}

    soup = BeautifulSoup(res.text, "html.parser")
    alert_box = soup.find(class_=lambda c: c and any(k in str(c).lower() for k in ["alert-danger", "alert-warning", "error"]))
    alert_text = alert_box.get_text(" ", strip=True) if alert_box else ""

    if "n'existe pas" in res.text.lower() or "invalide" in res.text.lower() or "introuvable" in res.text.lower():
        msg = alert_text or "La référence de paiement n'existe pas ou est invalide."
        return {
            "status": "not_found",
            "is_valid": False,
            "matricule_mesrs": mat,
            "code_paiement": code,
            "message": msg,
        }

    # Si paiement trouvé et validé
    details: Dict[str, Any] = {
        "status": "success",
        "is_valid": True,
        "matricule_mesrs": mat,
        "code_paiement": code,
        "numero_paiement": num,
        "message": "Paiement validé avec succès.",
    }

    # Extraction d'éventuelles informations dans les tableaux / champs
    for tr in soup.find_all("tr"):
        tds = tr.find_all(["th", "td"])
        if len(tds) >= 2:
            k = tds[0].get_text(strip=True).rstrip(":")
            v = tds[1].get_text(strip=True)
            if k and v:
                details[k.lower().replace(" ", "_")] = v

    return details


def get_mesrs_dexco_services(
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Récupère le catalogue officiel des actes d'examens disponibles via DEXCO
    (authentifications, diplômes, relevés de notes).

    Returns:
        dict: Liste des actes et formulaires disponibles avec leurs libellés et codes de demande.
    """
    http = session or Session()

    try:
        res = http.get(DEXCO_URL, headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion DEXCO : {e}", "services": []}

    soup = BeautifulSoup(res.text, "html.parser")
    csrf_input = soup.find("input", attrs={"name": "csrf_token"})
    csrf_token = csrf_input["value"] if csrf_input and "value" in csrf_input.attrs else ""

    services = []
    for form in soup.find_all("form"):
        action = form.get("action", "")
        type_inp = form.find("input", attrs={"name": "type_demande"})
        if type_inp and type_inp.get("value"):
            code_type = type_inp["value"]
            label = DEXCO_DEMANDE_TYPES.get(code_type, code_type)
            services.append({
                "code": code_type,
                "label": label,
                "action": action,
            })

    return {
        "status": "success",
        "csrf_token": csrf_token,
        "services": services,
        "count": len(services),
    }


def get_mesrs_announcements(
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Récupère les actualités officielles et annonces flash (tickers) diffusées sur le portail MESRS.

    Returns:
        dict: Liste des annonces officielles actives.
    """
    http = session or Session()

    try:
        res = http.get(BASE_URL, headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion au portail MESRS : {e}", "announcements": []}

    soup = BeautifulSoup(res.text, "html.parser")
    announcements = set()

    for ticker in soup.find_all(class_=lambda c: c and "ticker" in str(c).lower()):
        txt = ticker.get_text(" ", strip=True)
        # Nettoyage des séparateurs
        cleaned = txt.replace("◆", "\n").replace("•", "\n")
        for line in cleaned.split("\n"):
            line = line.strip()
            if line and len(line) > 10 and not any(skip in line.lower() for skip in ["chargement", "navigation"]):
                announcements.add(line)

    return {
        "status": "success",
        "announcements": list(announcements),
        "count": len(announcements),
    }
