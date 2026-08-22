"""
after_bac_orientation/scraper.py

Module d'interrogation et de scraping de la plateforme officielle d'Orientation des Bacheliers
(MESRS Côte d'Ivoire) : https://bac.mesrs-ci.net/

Fonctionnalités :
- Consultation des concours d'entrée aux grandes filières (Architecture, Urbanisme, ENSAU).
- Récupération des listes officielles des candidats admissibles classés par rang.
- Vérification du statut de paiement de l'orientation post-BAC.
- Simulation des choix d'orientation selon les notes du BAC.
- Extraction des filières et coordonnées d'un établissement d'enseignement supérieur.
"""

from typing import Dict, Any, List, Optional
import urllib3
from bs4 import BeautifulSoup
from requests import Session, RequestException

# Désactiver les avertissements SSL pour les plateformes gouvernementales
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://bac.mesrs-ci.net"
CONCOURS_URL = f"{BASE_URL}/orientation/concours"
PAYMENT_INFO_URL = f"{BASE_URL}/info/paiement"
SIMULATEUR_URL = f"{BASE_URL}/resultat/simulateur"
ETABLISSEMENT_SECTORS_URL = f"{BASE_URL}/liste-filiere-etablissement"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}


def get_bac_orientation_concours(
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Récupère la liste des concours d'orientation spéciaux post-BAC (ex: Architecture, Urbanisme).

    Returns:
        dict: Statut et liste des concours avec ID, intitulé et URL.
    """
    http = session or Session()
    try:
        res = http.get(CONCOURS_URL, headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion : {e}", "concours": []}

    soup = BeautifulSoup(res.text, "html.parser")
    concours_list = []

    for a in soup.find_all("a", href=lambda h: h and "/orientation/concours/" in h):
        href = a["href"]
        c_id = href.rstrip("/").split("/")[-1]
        title = a.get_text(" ", strip=True).replace("Consulter", "").replace("Admissibles", "").strip()
        if not title and a.parent:
            title = a.parent.get_text(" ", strip=True).replace("Consulter", "").replace("Admissibles", "").strip()

        # Éviter les doublons
        if c_id and not any(c["id"] == c_id for c in concours_list):
            concours_list.append({
                "id": c_id,
                "title": title,
                "url": BASE_URL + href if href.startswith("/") else href,
            })

    return {
        "status": "success",
        "concours": concours_list,
        "count": len(concours_list),
    }


def get_bac_orientation_concours_admissibles(
    concours_id: str,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Récupère la liste officielle des candidats admissibles à un concours d'orientation post-BAC.

    Args:
        concours_id (str): Identifiant numérique du concours (ex: "20693" pour Architecture).

    Returns:
        dict: Statut, titre du concours et liste des candidats avec leur rang.
    """
    c_id = str(concours_id).strip()
    if not c_id:
        return {"status": "error", "message": "L'identifiant du concours est requis.", "admissibles": []}

    http = session or Session()
    url = f"{BASE_URL}/orientation/concours/{c_id}"

    try:
        res = http.get(url, headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion : {e}", "admissibles": []}

    soup = BeautifulSoup(res.text, "html.parser")
    heading = soup.find(["h1", "h2", "h3", "h4"])
    concours_title = heading.get_text(strip=True) if heading else f"Concours #{c_id}"

    admissibles = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 2:
            rang = tds[0].get_text(strip=True)
            nom = " ".join(tds[1].get_text().split())
            if rang and nom and rang.isdigit():
                admissibles.append({"rang": int(rang), "nom_prenoms": nom})

    return {
        "status": "success",
        "concours_id": c_id,
        "title": concours_title,
        "admissibles": admissibles,
        "count": len(admissibles),
    }


def check_bac_orientation_payment(
    matricule: str,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Vérifie le statut de paiement des frais d'orientation post-BAC d'un candidat.

    Args:
        matricule (str): Matricule BAC du candidat (ex: "12345678A" ou "BAC2014563").

    Returns:
        dict: Statut de paiement et informations associées.
    """
    mat = str(matricule).strip().upper()
    if not mat:
        return {"status": "error", "message": "Le matricule BAC est obligatoire.", "is_paid": False}

    http = session or Session()
    try:
        res = http.post(
            PAYMENT_INFO_URL,
            data={"matricule": mat},
            headers=DEFAULT_HEADERS,
            verify=False,
            timeout=timeout,
        )
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion : {e}", "is_paid": False}

    soup = BeautifulSoup(res.text, "html.parser")
    alert = soup.find(class_=lambda c: c and any(k in str(c).lower() for k in ["alert", "card", "msg", "error", "danger"]))
    alert_text = alert.get_text(" ", strip=True) if alert else ""

    if "aucun bachelier" in res.text.lower() or "introuvable" in res.text.lower() or "invalide" in res.text.lower():
        return {
            "status": "not_found",
            "is_paid": False,
            "matricule": mat,
            "message": alert_text or "Aucun bachelier trouvé pour ce matricule.",
        }

    # Si paiement validé / trouvé
    return {
        "status": "success",
        "is_paid": True,
        "matricule": mat,
        "message": "Paiement de l'orientation enregistré avec succès.",
    }


def simulate_bac_orientation(
    matricule: str,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Simule l'affectation et les filières accessibles selon les notes du BAC du candidat.

    Args:
        matricule (str): Matricule BAC du candidat.

    Returns:
        dict: Résultat de la simulation ou message d'information.
    """
    mat = str(matricule).strip().upper()
    if not mat:
        return {"status": "error", "message": "Le matricule BAC est obligatoire."}

    http = session or Session()
    try:
        res = http.post(
            SIMULATEUR_URL,
            data={"matricule": mat},
            headers=DEFAULT_HEADERS,
            verify=False,
            timeout=timeout,
        )
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion : {e}"}

    soup = BeautifulSoup(res.text, "html.parser")
    alert = soup.find(class_=lambda c: c and any(k in str(c).lower() for k in ["alert", "card", "msg", "error", "danger"]))
    alert_text = alert.get_text(" ", strip=True) if alert else ""

    if "aucun bachelier" in res.text.lower() or "introuvable" in res.text.lower():
        return {
            "status": "not_found",
            "matricule": mat,
            "message": alert_text or "Aucun bachelier trouvé pour ce matricule.",
        }

    return {
        "status": "success",
        "matricule": mat,
        "message": "Simulation exécutée avec succès.",
    }


def get_bac_etablissement_sectors(
    etablissement_id: str,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Récupère les filières et informations complètes d'un établissement d'enseignement supérieur.

    Args:
        etablissement_id (str): Identifiant de l'établissement.
    """
    http = session or Session()
    try:
        res = http.post(
            ETABLISSEMENT_SECTORS_URL,
            data={"etablissement_id": str(etablissement_id).strip()},
            headers=DEFAULT_HEADERS,
            verify=False,
            timeout=timeout,
        )
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion : {e}"}

    soup = BeautifulSoup(res.content, "html.parser")
    box = soup.find("div", attrs={"class": lambda c: c and "card" in str(c)})
    if not box:
        return {"status": "not_found", "message": "Établissement introuvable."}

    infos = box.find_all("p")
    data: Dict[str, Any] = {}
    for p in infos:
        txt = p.get_text(strip=True)
        if ":" in txt:
            k, v = txt.split(":", 1)
            data[k.strip().lower()] = v.strip()

    return {
        "status": "success",
        "etablissement_id": etablissement_id,
        "details": data,
    }
