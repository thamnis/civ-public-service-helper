"""
infas_convocation/scraper.py

Module d'interrogation et de téléchargement des convocations du concours INFAS
(Institut National de Formation des Agents de Santé de Côte d'Ivoire) depuis :
https://infas.ciconcours.com/infaseditconvoc-2026
"""

import os
import re
import json
from typing import Dict, Any, Optional, List
from requests import Session, RequestException
import urllib3
from bs4 import BeautifulSoup
import pypdf

# Désactiver les avertissements SSL pour les plateformes gouvernementales
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://infas.ciconcours.com"
PAGE_URL = f"{BASE_URL}/infaseditconvoc-2026"
LIST_CONVOC_URL = f"{BASE_URL}/listConvocation"
DEFAULT_DOWNLOAD_DIR = os.path.join("downloads", "infas")

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": PAGE_URL,
}


def clean_candidate_code(code: str) -> str:
    """
    Nettoie et formate le numéro de candidature INFAS.
    """
    return str(code).strip().upper()


def get_csrf_token(session: Session, timeout: int = 15) -> Optional[str]:
    """
    Récupère le token CSRF nécessaire à la soumission du formulaire INFAS.
    """
    try:
        res = session.get(PAGE_URL, headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            token_input = soup.find("input", {"name": "_token"})
            if token_input and token_input.get("value"):
                return token_input["value"]
    except Exception:
        pass
    return None


def parse_convocation_view(view_html: str) -> Dict[str, Any]:
    """
    Parse le fragment HTML renvoyé par listConvocation et extrait les métadonnées.
    """
    soup = BeautifulSoup(view_html, "html.parser")

    # 1. Extraction de la photo
    photo_img = soup.find("img", {"id": "imgCandidat"}) or soup.find("img", class_=lambda c: c and "img-thumbnail" in c)
    photo_url = photo_img.get("src") if photo_img else None

    # 2. Extraction des listes de définition (dl > dt, dd)
    fields: Dict[str, str] = {}
    for dl in soup.find_all("dl"):
        dt = dl.find("dt")
        dd = dl.find("dd")
        if dt and dd:
            label = dt.get_text(strip=True).lower()
            val = dd.get_text(" ", strip=True).lstrip(":").strip()
            fields[label] = val

    candidate_id = None
    table_number = None
    full_name = None
    birth_raw = None
    birthdate = None
    birthplace = None
    id_card = None

    for label, val in fields.items():
        if "candidat" in label:
            candidate_id = val
        elif "table" in label:
            table_number = val
        elif "nom" in label:
            full_name = re.sub(r"^M\.\s*|^Mme\s*|^Mlle\s*", "", val, flags=re.IGNORECASE).strip()
        elif "naissance" in label:
            birth_raw = val
            if " à " in val:
                parts = val.split(" à ", 1)
                birthdate = parts[0].strip()
                birthplace = parts[1].strip()
            else:
                birthdate = val
        elif "identit" in label:
            id_card = val

    # 3. Extraction des épreuves / sessions dans le tableau
    sessions: List[Dict[str, str]] = []
    table = soup.find("table")
    if table:
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 4:
                concours_val = tds[0].get_text(" ", strip=True)
                centre_val = tds[1].get_text(" ", strip=True)
                salle_val = tds[2].get_text(" ", strip=True)
                date_val = tds[3].get_text(" ", strip=True) if len(tds) > 3 else ""
                heure_val = tds[4].get_text(" ", strip=True) if len(tds) > 4 else ""

                sessions.append({
                    "concours": concours_val,
                    "centre": centre_val,
                    "salle": salle_val,
                    "date": date_val,
                    "heure": heure_val,
                })

    # 4. Extraction du lien de téléchargement PDF
    convocation_url = None
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if "imprimerConvocation" in href or "convocation" in href.lower():
            convocation_url = href.strip()
            break

    return {
        "status": "success",
        "candidate_id": candidate_id,
        "table_number": table_number,
        "full_name": full_name,
        "birthdate": birthdate,
        "birthplace": birthplace,
        "birth_raw": birth_raw,
        "id_card": id_card,
        "photo_url": photo_url,
        "sessions": sessions,
        "convocation_url": convocation_url,
    }


def get_infas_convocation_info(
    candidate_code: str,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Interroge la plateforme INFAS et récupère les informations de convocation d'un candidat.

    Args:
        candidate_code (str): Numéro de candidature (ex: "CD00000000" ou "CA00000000").
        session (Session, optional): Session HTTP.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Informations de convocation structurées ou message d'erreur.
    """
    code = clean_candidate_code(candidate_code)
    if not code:
        return {"status": "error", "message": "Le numéro de candidature est requis."}

    http = session or Session()
    token = get_csrf_token(http, timeout=timeout)
    if not token:
        return {"status": "error", "message": "Impossible de récupérer le token CSRF sur la page INFAS."}

    payload = {
        "_token": token,
        "code": code,
    }

    try:
        res = http.post(
            LIST_CONVOC_URL,
            data=payload,
            headers=DEFAULT_HEADERS,
            verify=False,
            timeout=timeout,
        )
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion au serveur INFAS : {e}"}

    if res.status_code != 200:
        return {
            "status": "not_found",
            "message": "Candidat non trouvé ou aucune convocation disponible pour ce numéro.",
        }

    try:
        data = res.json()
    except json.JSONDecodeError:
        return {"status": "error", "message": "Réponse JSON inattendue de la plateforme INFAS."}

    view_html = data.get("view", "")
    if not view_html or "Information" in view_html and "non trouvé" in view_html:
        return {"status": "not_found", "message": "Aucune convocation trouvée pour ce numéro."}

    parsed = parse_convocation_view(view_html)
    if not parsed.get("candidate_id"):
        parsed["candidate_id"] = code

    return parsed


def download_infas_convocation(
    candidate_code: str,
    output_dir: str = DEFAULT_DOWNLOAD_DIR,
    filename: Optional[str] = None,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Télécharge le fichier PDF officiel de la convocation INFAS.

    Args:
        candidate_code (str): Numéro de candidature (ex: "CD00000000" ou "CA00000000").
        output_dir (str): Dossier de sauvegarde.
        filename (str, optional): Nom personnalisé du fichier PDF.
        session (Session, optional): Session HTTP.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Statut de téléchargement et chemin du fichier.
    """
    code = clean_candidate_code(candidate_code)
    http = session or Session()

    info = get_infas_convocation_info(code, session=http, timeout=timeout)
    if info.get("status") != "success":
        return info

    convocation_url = info.get("convocation_url")
    if not convocation_url:
        return {
            "status": "error",
            "message": "Lien de téléchargement de la convocation non trouvé dans les données du candidat.",
        }

    try:
        res = http.get(convocation_url, headers=DEFAULT_HEADERS, verify=False, timeout=timeout)
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur lors du téléchargement du PDF : {e}"}

    content = res.content
    content_type = res.headers.get("Content-Type", "")
    if not content.startswith(b"%PDF") and "application/pdf" not in content_type:
        return {"status": "error", "message": "Le fichier téléchargé n'est pas un document PDF valide."}

    os.makedirs(output_dir, exist_ok=True)
    table_num = info.get("table_number") or code
    out_filename = filename or f"convocation_infas_{code}_{table_num}.pdf"
    if not out_filename.lower().endswith(".pdf"):
        out_filename += ".pdf"
    file_path = os.path.join(output_dir, out_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "status": "success",
        "file_path": os.path.abspath(file_path),
        "file_size": len(content),
        "filename": out_filename,
        "candidate": info,
    }


def extract_infas_pdf_info(pdf_path: str) -> Dict[str, Any]:
    """
    Extrait les informations d'un fichier PDF de convocation INFAS déjà téléchargé.
    """
    if not os.path.exists(pdf_path):
        return {"status": "error", "message": f"Fichier non trouvé : {pdf_path}"}

    try:
        reader = pypdf.PdfReader(pdf_path)
        if len(reader.pages) == 0:
            return {"status": "error", "message": "Le document PDF est vide."}

        text = reader.pages[0].extract_text() or ""
        return {
            "status": "success",
            "raw_text": text,
            "page_count": len(reader.pages),
        }
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors de la lecture du PDF : {e}"}


def get_infas_convocation(
    candidate_code: str,
    download_pdf: bool = False,
    output_dir: str = DEFAULT_DOWNLOAD_DIR,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Pipeline complet : récupère les données de convocation et télécharge optionnellement le PDF.

    Args:
        candidate_code (str): Numéro de candidature INFAS.
        download_pdf (bool): Télécharger automatiquement le fichier PDF.
        output_dir (str): Dossier de sauvegarde du PDF.
        session (Session, optional): Session HTTP.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Dictionnaire complet avec candidat, session(s) et détails du PDF.
    """
    http = session or Session()
    info = get_infas_convocation_info(candidate_code, session=http, timeout=timeout)
    if info.get("status") != "success":
        return info

    pdf_data = None
    if download_pdf:
        pdf_data = download_infas_convocation(
            candidate_code,
            output_dir=output_dir,
            session=http,
            timeout=timeout,
        )

    return {
        "status": "success",
        "candidate_id": info.get("candidate_id"),
        "table_number": info.get("table_number"),
        "full_name": info.get("full_name"),
        "birthdate": info.get("birthdate"),
        "birthplace": info.get("birthplace"),
        "id_card": info.get("id_card"),
        "photo_url": info.get("photo_url"),
        "sessions": info.get("sessions", []),
        "convocation_url": info.get("convocation_url"),
        "pdf": pdf_data,
    }
