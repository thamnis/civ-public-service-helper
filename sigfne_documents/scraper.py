"""
sigfne_documents/scraper.py

Module d'interrogation et de téléchargement des documents scolaires SIGFNE / DESPS (Côte d'Ivoire)
(Reçus de préinscription, Fiches de cursus scolaire) depuis la plateforme officielle :
https://agfne.sigfne.net/vas/interface-edition-documents-sigfne/
"""

import os
import re
from typing import Dict, Any, Optional, Literal
from requests import Session, RequestException
import urllib3
from bs4 import BeautifulSoup
import pypdf

# Désactiver les avertissements SSL pour les plateformes gouvernementales
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://agfne.sigfne.net"
PAGE_URL = f"{BASE_URL}/vas/interface-edition-documents-sigfne/"
DEFAULT_DOWNLOAD_DIR = os.path.join("downloads", "sigfne")

DOCUMENT_TYPES = {
    "recu": "Reçu de préinscription",
    "cursus": "Fiche Cursus Scolaire",
    "cursusnew": "Fiche Cursus Scolaire (New)",
}

ACADEMIC_YEARS = {
    "1920": "2019 - 2020",
    "2021": "2020 - 2021",
    "2122": "2021 - 2022",
    "2223": "2022 - 2023",
    "2324": "2023 - 2024",
    "2425": "2024 - 2025",
    "2526": "2025 - 2026",
    "2627": "2026 - 2027",
}

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": PAGE_URL,
}


def clean_student_code(code: str) -> str:
    """
    Nettoie et formate le matricule de l'élève.
    """
    return str(code).strip().upper()


def normalize_annee(annee_str: str) -> str:
    """
    Normalise le code de l'année scolaire vers le format à 4 chiffres (ex: '2026-2027' -> '2627', '2627' -> '2627').
    """
    s = str(annee_str).strip()
    if s in ACADEMIC_YEARS:
        return s

    # Match format type 2026-2027 ou 2026/2027
    m = re.match(r"^20(\d{2})\s*[-/]\s*20(\d{2})$", s)
    if m:
        code = f"{m.group(1)}{m.group(2)}"
        if code in ACADEMIC_YEARS:
            return code

    return "2627"


def download_sigfne_document(
    matricule: str,
    doc_type: Literal["recu", "cursus", "cursusnew"] = "recu",
    annee: str = "2627",
    output_dir: str = DEFAULT_DOWNLOAD_DIR,
    filename: Optional[str] = None,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Télécharge un document officiel SIGFNE / DESPS (Reçu de préinscription ou Fiche cursus).

    Args:
        matricule (str): Matricule de l'élève (ex: "12345678A").
        doc_type (Literal["recu", "cursus", "cursusnew"]): Type de document.
        annee (str): Année scolaire (ex: "2627" pour 2026-2027).
        output_dir (str): Dossier de destination du PDF.
        filename (str, optional): Nom personnalisé du fichier PDF.
        session (Session, optional): Session HTTP.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Résultat avec statut, chemin du fichier PDF et métadonnées.
    """
    code = clean_student_code(matricule)
    if not code:
        return {"status": "error", "message": "Le matricule de l'élève est requis."}

    if doc_type not in DOCUMENT_TYPES:
        return {
            "status": "error",
            "message": f"Type de document invalide: '{doc_type}'. Valeurs autorisées: {list(DOCUMENT_TYPES.keys())}",
        }

    year_code = normalize_annee(annee)
    http = session or Session()

    payload = {
        "matricule": code,
        "typedoc": doc_type,
        "annee": year_code,
    }

    try:
        res = http.post(
            PAGE_URL,
            data=payload,
            headers=DEFAULT_HEADERS,
            verify=False,
            timeout=timeout,
        )
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion à SIGFNE : {e}"}

    content = res.content
    content_type = res.headers.get("Content-Type", "")

    # Si la réponse est un PDF valide
    if content.startswith(b"%PDF") or "application/pdf" in content_type:
        os.makedirs(output_dir, exist_ok=True)
        out_filename = filename or f"sigfne_{doc_type}_{code}_{year_code}.pdf"
        if not out_filename.lower().endswith(".pdf"):
            out_filename += ".pdf"
        file_path = os.path.join(output_dir, out_filename)

        with open(file_path, "wb") as f:
            f.write(content)

        return {
            "status": "success",
            "matricule": code,
            "doc_type": doc_type,
            "doc_label": DOCUMENT_TYPES[doc_type],
            "annee": year_code,
            "annee_label": ACADEMIC_YEARS.get(year_code, year_code),
            "file_path": os.path.abspath(file_path),
            "file_size": len(content),
            "filename": out_filename,
        }

    # Si la réponse est une page HTML (erreur ou document non disponible)
    soup = BeautifulSoup(res.text, "html.parser")
    error_span = soup.find("span", style=lambda s: s and "red" in s)
    error_msg = error_span.get_text(strip=True) if error_span else ""

    if not error_msg:
        for tag in soup.find_all(["div", "p", "span"]):
            txt = tag.get_text(strip=True)
            if any(k in txt.lower() for k in ["aucun", "erreur", "refuse", "introuvable", "non trouvé"]):
                error_msg = txt
                break

    if not error_msg:
        error_msg = "Document introuvable ou non disponible pour ce matricule et cette année."

    return {
        "status": "not_found",
        "matricule": code,
        "doc_type": doc_type,
        "doc_label": DOCUMENT_TYPES.get(doc_type, doc_type),
        "annee": year_code,
        "annee_label": ACADEMIC_YEARS.get(year_code, year_code),
        "message": error_msg,
    }


def extract_pdf_info(pdf_path: str) -> Dict[str, Any]:
    """
    Extrait le contenu textuel d'un document SIGFNE PDF.
    """
    if not os.path.exists(pdf_path):
        return {"status": "error", "message": f"Fichier non trouvé : {pdf_path}"}

    try:
        reader = pypdf.PdfReader(pdf_path)
        if len(reader.pages) == 0:
            return {"status": "error", "message": "Le document PDF est vide."}

        full_text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return {
            "status": "success",
            "page_count": len(reader.pages),
            "raw_text": full_text,
        }
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors de la lecture du PDF : {e}"}


def get_sigfne_document(
    matricule: str,
    doc_type: Literal["recu", "cursus", "cursusnew"] = "recu",
    annee: str = "2627",
    download_pdf: bool = True,
    output_dir: str = DEFAULT_DOWNLOAD_DIR,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Fonction unifiée pour interroger et télécharger un document SIGFNE.
    """
    return download_sigfne_document(
        matricule=matricule,
        doc_type=doc_type,
        annee=annee,
        output_dir=output_dir,
        session=session,
        timeout=timeout,
    )
