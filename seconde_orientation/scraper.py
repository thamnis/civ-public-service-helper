"""
seconde_orientation/scraper.py

Module d'interrogation et de téléchargement des fiches d'orientation en seconde (Côte d'Ivoire)
depuis la plateforme officielle de la Direction de l'Orientation et des Bourses (DOB) :
https://orientation.mendob.ci
"""

import os
import re
import json
from typing import Dict, Any, Optional
from requests import Session, RequestException
import urllib3
import pypdf

# Désactiver les avertissements InsecureRequestWarning pour les certificats SSL gouvernementaux
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://orientation.mendob.ci"
AJAX_URL = f"{BASE_URL}/templates/ajax_command_json.php"
DEFAULT_DOWNLOAD_DIR = os.path.join("downloads", "orientation")

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": f"{BASE_URL}/",
}


def clean_student_code(code: str) -> str:
    """
    Nettoie et formate le matricule de l'élève.
    """
    return str(code).strip().upper()


def get_student_info(
    student_code: str,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Récupère l'identité et les informations d'orientation de l'élève par son matricule.

    Args:
        student_code (str): Matricule de l'élève (ex: "12345678A").
        session (Session, optional): Session HTTP.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Informations de l'élève ou message d'erreur/statut.
    """
    code = clean_student_code(student_code)
    if not code:
        return {"status": "error", "message": "Le matricule est requis."}

    http = session or Session()
    payload = {
        "command": "get_student_by_code_only",
        "code": code,
    }

    try:
        res = http.post(
            AJAX_URL,
            json=payload,
            headers={**DEFAULT_HEADERS, "Content-Type": "application/json"},
            verify=False,
            timeout=timeout,
        )
        res.raise_for_status()
        data = res.json()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion : {e}"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Réponse JSON invalide du serveur."}

    if data.get("status") == "ok" and data.get("answer"):
        ans = data["answer"]
        return {
            "status": "success",
            "id": ans.get("id"),
            "student_code": ans.get("student_code", code),
            "first_name": ans.get("student_first_name", "").strip(),
            "last_name": ans.get("student_last_name", "").strip(),
            "full_name": f"{ans.get('student_last_name', '').strip()} {ans.get('student_first_name', '').strip()}".strip(),
            "birthday": ans.get("student_birthday", "").strip(),
            "age": ans.get("student_age"),
            "gender": ans.get("student_gender"),
            "nationality": ans.get("student_nationality"),
            "tgp": ans.get("student_tgp"),
            "msno": ans.get("student_msno"),
        }
    else:
        err_msg = data.get("error") or "Élève non trouvé ou non orienté en enseignement général."
        return {"status": "not_found", "message": err_msg}


def get_school_info(
    school_id: int,
    student_code: str,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Récupère les informations sur l'établissement d'accueil en seconde.

    Args:
        school_id (int): Identifiant de l'établissement.
        student_code (str): Matricule de l'élève.
        session (Session, optional): Session HTTP.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Détails sur l'établissement et la série d'orientation.
    """
    http = session or Session()
    payload = {
        "command": "get_school",
        "id": school_id,
        "student_code": clean_student_code(student_code),
    }

    try:
        res = http.post(
            AJAX_URL,
            json=payload,
            headers={**DEFAULT_HEADERS, "Content-Type": "application/json"},
            verify=False,
            timeout=timeout,
        )
        res.raise_for_status()
        data = res.json()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion : {e}"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Réponse JSON invalide du serveur."}

    if data.get("status") == "ok" and data.get("answer"):
        ans = data["answer"]
        return {
            "status": "success",
            "school_id": ans.get("id"),
            "school_name": ans.get("school_name", "").strip(),
            "serie": ans.get("school_serie", "").strip(),
            "quartier": ans.get("school_quartier", "").strip(),
            "school_type": ans.get("school_type", "").strip(),
            "school_cost": ans.get("school_cost", "").strip(),
            "capacity": ans.get("school_capacity"),
            "assigned_count": ans.get("school_assigned"),
            "free_place": ans.get("school_free_place"),
            "school_gender": ans.get("school_gender"),
            "comment": ans.get("school_comment", "").strip(),
        }
    else:
        return {"status": "not_found", "message": data.get("error") or "Établissement non trouvé."}


def get_student_school_id(
    student_code: str,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Optional[int]:
    """
    Récupère le schoolid attribué à un élève orienté en seconde.
    """
    http = session or Session()
    payload = {
        "command": "get_student_schoolid_by_code_only",
        "code": clean_student_code(student_code),
    }

    try:
        res = http.post(
            AJAX_URL,
            json=payload,
            headers={**DEFAULT_HEADERS, "Content-Type": "application/json"},
            verify=False,
            timeout=timeout,
        )
        res.raise_for_status()
        data = res.json()
        if data.get("status") == "ok" and data.get("answer"):
            school_id = data["answer"].get("schoolid")
            if school_id:
                return int(school_id)
    except Exception:
        pass
    return None


def download_orientation_document(
    student_code: str,
    output_dir: str = DEFAULT_DOWNLOAD_DIR,
    filename: Optional[str] = None,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Télécharge la fiche officielle d'orientation en seconde (format PDF).

    Args:
        student_code (str): Matricule de l'élève.
        output_dir (str): Répertoire de sauvegarde.
        filename (str, optional): Nom personnalisé du fichier PDF.
        session (Session, optional): Session HTTP.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Statut, chemin absolu du fichier téléchargé et taille.
    """
    code = clean_student_code(student_code)
    if not code:
        return {"status": "error", "message": "Le matricule est requis."}

    http = session or Session()

    try:
        res = http.post(
            f"{BASE_URL}/",
            data={"code": code},
            headers=DEFAULT_HEADERS,
            verify=False,
            timeout=timeout,
        )
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur lors du téléchargement : {e}"}

    content = res.content
    content_type = res.headers.get("Content-Type", "")
    if not content.startswith(b"%PDF") and "application/pdf" not in content_type:
        return {
            "status": "error",
            "message": "Le document renvoyé n'est pas un fichier PDF valide. L'élève n'est peut-être pas orienté.",
        }

    os.makedirs(output_dir, exist_ok=True)
    out_filename = filename or f"orientation_seconde_{code}.pdf"
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
    }


def extract_pdf_info(pdf_path: str) -> Dict[str, Any]:
    """
    Extrait les informations utiles depuis une fiche PDF d'orientation en seconde.
    """
    if not os.path.exists(pdf_path):
        return {"status": "error", "message": f"Fichier non trouvé : {pdf_path}"}

    try:
        reader = pypdf.PdfReader(pdf_path)
        if len(reader.pages) == 0:
            return {"status": "error", "message": "Le fichier PDF est vide."}

        text = reader.pages[0].extract_text() or ""
        return {
            "status": "success",
            "raw_text": text,
            "page_count": len(reader.pages),
        }
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors de la lecture du PDF : {e}"}


def get_seconde_orientation(
    student_code: str,
    download_pdf: bool = False,
    output_dir: str = DEFAULT_DOWNLOAD_DIR,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Récupère le résultat complet d'orientation en 2nde pour un élève, avec téléchargement optionnel du PDF.

    Args:
        student_code (str): Matricule de l'élève (ex: "12345678A").
        download_pdf (bool): Télécharger automatiquement la fiche PDF.
        output_dir (str): Dossier de destination pour le PDF.
        session (Session, optional): Session HTTP.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Résultat complet de l'orientation (élève, établissement, série, PDF).
    """
    code = clean_student_code(student_code)
    http = session or Session()

    # 1. Identité de l'élève
    student_res = get_student_info(code, session=http, timeout=timeout)
    if student_res.get("status") != "success":
        return student_res

    # 2. Établissement d'orientation
    school_id = get_student_school_id(code, session=http, timeout=timeout)
    school_data: Optional[Dict[str, Any]] = None
    is_oriented = False

    if school_id and school_id > 0:
        is_oriented = True
        school_info_res = get_school_info(school_id, code, session=http, timeout=timeout)
        if school_info_res.get("status") == "success":
            school_data = school_info_res

    pdf_res = None
    if download_pdf and is_oriented:
        pdf_res = download_orientation_document(code, output_dir=output_dir, session=http, timeout=timeout)

    return {
        "status": "success",
        "is_oriented": is_oriented,
        "student_code": code,
        "student": student_res,
        "school": school_data,
        "pdf": pdf_res,
        "message": "Élève orienté(e) en seconde" if is_oriented else "L'élève n'est pas encore orienté(e)",
    }
