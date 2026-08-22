"""
bts_result/scraper.py

Module de scraping des résultats du BTS (Côte d'Ivoire) depuis le site officiel du MESRS.
Permet d'interroger le portail des résultats avec un matricule (permanent ou BTS) et une date de naissance,
puis d'extraire les informations structurées du candidat.
"""

from typing import Dict, Any, Optional
import re
from datetime import datetime
from bs4 import BeautifulSoup
from requests import Session, RequestException

TARGET_URL = "https://bts.mesrs-ci.net/resultat/candidat"
BASE_URL = "https://bts.mesrs-ci.net/resultats/bts"


def normalize_birthdate(date_str: str) -> str:
    """
    Normalise une chaîne de date de naissance vers le format attendu par le serveur (YYYY-MM-DD).

    Formats supportés :
        - YYYY-MM-DD (ex: 2007-01-16)
        - DD/MM/YYYY (ex: 16/01/2007)
        - DD-MM-YYYY (ex: 16-01-2007)
        - YYYY/MM/DD (ex: 2007/01/16)
        - DD.MM.YYYY (ex: 16.01.2007)
        - YY-MM-DD / DD-MM-YY (tentative d'inférence si 2 chiffres pour l'année)
    """
    date_str = str(date_str).strip()
    if not date_str:
        raise ValueError("La date de naissance ne peut pas être vide.")

    # Match YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return date_str

    # Formats avec séparateurs variés
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y", "%Y.%m.%d"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Essai avec année à 2 chiffres (ex: 04-11-02 ou 02-11-04)
    # Dans le format matricule CI, les 6 chiffres sont souvent JJMMYY ou YYMMJJ
    for fmt in ("%d-%m-%y", "%y-%m-%d", "%d/%m/%y", "%y/%m/%d"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return date_str


def parse_bts_html(html_content: str) -> Dict[str, Any]:
    """
    Parse le contenu HTML renvoyé par le site du BTS MESRS-CI.

    Returns:
        dict: Dictionnaire contenant le statut et les données du candidat ou le message d'erreur.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Vérifier si un message d'alerte / erreur est présent
    alert_box = soup.find("div", class_=lambda c: c and "alert" in c)
    alert_text = alert_box.get_text(" ", strip=True) if alert_box else None

    # 2. Chercher la carte de résultat principale
    card = soup.find("div", class_=lambda c: c and "text-center" in c and "shadow-lg" in c)
    if not card:
        # Recherche alternative de conteneur de résultat
        card = soup.find("div", class_=lambda c: c and ("resultat" in c or "candidat" in c))

    if not card:
        return {
            "status": "not_found",
            "is_admitted": False,
            "message": alert_text or "Aucun résultat trouvé pour ces identifiants.",
            "data": None,
        }

    # Extraction des identifiants (BTS ID / Matricule)
    bts_id = None
    student_id = None
    id_container = card.find("div", class_=lambda c: c and "text-muted" in c)
    if id_container:
        spans = id_container.find_all("span", class_=lambda c: c and "fw-bold" in c)
        if len(spans) >= 2:
            bts_id = spans[0].get_text(strip=True)
            student_id = spans[1].get_text(strip=True)
        elif len(spans) == 1:
            val = spans[0].get_text(strip=True)
            if val.startswith("BTS"):
                bts_id = val
            else:
                student_id = val

    # Extraction du nom complet (Nom / Prénoms)
    full_name = None
    last_name = None
    first_name = None
    name_tag = card.find(["h4", "h3"], class_=lambda c: c and ("fw-bold" in c or "text-dark" in c))
    if name_tag:
        lines = [re.sub(r"\s+", " ", line.strip()) for line in name_tag.get_text().split("\n") if line.strip()]
        if len(lines) >= 2:
            last_name = lines[0]
            first_name = " ".join(lines[1:])
            full_name = f"{last_name} {first_name}"
        elif len(lines) == 1:
            full_name = lines[0]
            parts = full_name.split()
            last_name = parts[0] if parts else ""
            first_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    # Extraction de la date et lieu de naissance
    birthdate = None
    birthplace = None
    birth_p = card.find("p", class_=lambda c: c and "text-secondary" in c)
    if birth_p:
        date_span = birth_p.find("span")
        if date_span:
            birthdate = date_span.get_text(strip=True)
        b_tags = birth_p.find_all("b")
        if len(b_tags) >= 2:
            birthplace = b_tags[1].get_text(strip=True)
        elif " à " in birth_p.get_text():
            parts = birth_p.get_text().split(" à ")
            if len(parts) > 1:
                birthplace = parts[1].strip()

    # Extraction de la filière / secteur
    sector = None
    sector_p = card.find("p", class_=lambda c: c and ("fs-5" in c or "text-muted" in c))
    if sector_p:
        sector = re.sub(r"\s+", " ", sector_p.get_text(strip=True))

    # Extraction de la décision d'admission et du message
    heading = card.find(["h2", "h3"])
    heading_text = heading.get_text(" ", strip=True) if heading else ""

    decision_p = card.find("p", class_=lambda c: c and ("admissible" in c or "message" in c))
    if not decision_p:
        # Trouver tout paragraphe contenant admissible ou admis
        decision_p = card.find(lambda tag: tag.name == "p" and any(k in tag.get_text().lower() for k in ["admiss", "refus", "ajourn"]))

    decision_text = decision_p.get_text(" ", strip=True) if decision_p else ""
    cleaned_decision_text = re.sub(r"\s+", " ", decision_text)

    # Détermination du statut d'admission
    text_corpus = f"{heading_text} {cleaned_decision_text}".lower()
    is_admitted = False
    decision = "inconnu"

    if "admissible" in text_corpus or "admis" in text_corpus or "félicitations" in text_corpus:
        if not ("non admissible" in text_corpus or "refus" in text_corpus or "ajourné" in text_corpus):
            is_admitted = True
            decision = "admissible"
    elif "refus" in text_corpus or "ajourné" in text_corpus or "non admissible" in text_corpus:
        is_admitted = False
        decision = "refusé"

    # Extraction de la session
    session = None
    session_match = re.search(r"session\s*(\d{4})", cleaned_decision_text, re.IGNORECASE)
    if session_match:
        session = session_match.group(1)
    else:
        session_match_all = re.search(r"session\s*(\d{4})", html_content, re.IGNORECASE)
        if session_match_all:
            session = session_match_all.group(1)

    # Extraction de la photo en base64 (si présente)
    photo_src = None
    img_tag = card.find("img", src=lambda s: s and s.startswith("data:image"))
    if img_tag:
        photo_src = img_tag.get("src")

    return {
        "status": "success",
        "is_admitted": is_admitted,
        "decision": decision,
        "bts_id": bts_id,
        "student_id": student_id,
        "full_name": full_name,
        "last_name": last_name,
        "first_name": first_name,
        "birthdate": birthdate,
        "birthplace": birthplace,
        "sector": sector,
        "session": session,
        "message": cleaned_decision_text or heading_text,
        "photo": photo_src,
    }


def get_bts_result(
    matricule: str,
    birthdate: str,
    session: Optional[Session] = None,
    timeout: int = 15,
    include_photo: bool = False,
    max_retries: int = 2,
) -> Dict[str, Any]:
    """
    Récupère le résultat d'un candidat au BTS ivoirien.

    Args:
        matricule (str): Matricule permanent ou identifiant BTS (ex: "12345678A" ou "BTS2026000000").
        birthdate (str): Date de naissance du candidat (ex: "2000-01-01", "01/01/2000").
        session (Session, optional): Session requests réutilisable.
        timeout (int): Délai d'attente maximum en secondes.
        include_photo (bool): Inclure la chaîne base64 de la photo dans le résultat.
        max_retries (int): Nombre de tentatives en cas d'erreur de connexion transitoire.

    Returns:
        dict: Résultat structuré du candidat.
    """
    if not matricule:
        return {"status": "error", "message": "Le matricule est obligatoire.", "is_admitted": False}
    if not birthdate:
        return {"status": "error", "message": "La date de naissance est obligatoire.", "is_admitted": False}

    formatted_birthdate = normalize_birthdate(birthdate)
    http = session or Session()

    response = None
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = http.post(
                TARGET_URL,
                data={"matricule": matricule.strip(), "datenaiss": formatted_birthdate},
                timeout=timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Referer": BASE_URL,
                },
            )
            response.raise_for_status()
            break
        except RequestException as e:
            last_error = e

    if response is None:
        return {
            "status": "error",
            "message": f"Erreur de connexion au serveur MESRS : {last_error}",
            "is_admitted": False,
        }

    parsed = parse_bts_html(response.text)
    if not include_photo and parsed.get("photo"):
        del parsed["photo"]

    return parsed


def get_bts_calendar(
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Récupère le calendrier officiel de la session BTS (étapes et dates clés).

    Returns:
        dict: Statut et liste des étapes du calendrier avec périodes associées.
    """
    http = session or Session()
    cal_url = "https://bts.mesrs-ci.net/examen/calendrier"

    try:
        res = http.get(
            cal_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            },
            timeout=timeout,
        )
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion : {e}", "events": []}

    soup = BeautifulSoup(res.text, "html.parser")
    events = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 2:
            etape = tds[0].get_text(" ", strip=True)
            periode = tds[1].get_text(" ", strip=True)
            if etape and periode:
                events.append({"etape": etape, "periode": periode})

    return {
        "status": "success",
        "events": events,
        "count": len(events),
    }


def get_bts_statistics(
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Récupère les statistiques nationales de la dernière session du BTS.

    Returns:
        dict: Chiffres clés (candidats inscrits, centres, filières, taux de réussite).
    """
    http = session or Session()
    stat_url = "https://bts.mesrs-ci.net/resultats/statistiques"

    try:
        res = http.get(
            stat_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            },
            timeout=timeout,
        )
        res.raise_for_status()
    except RequestException as e:
        return {"status": "error", "message": f"Erreur de connexion : {e}"}

    soup = BeautifulSoup(res.text, "html.parser")
    stats: Dict[str, str] = {}

    for stat_div in soup.find_all(class_=lambda c: c and "bts-stat" in c):
        val_div = stat_div.find(class_=lambda c: c and "value" in c)
        lbl_div = stat_div.find(class_=lambda c: c and "label" in c)
        if val_div and lbl_div:
            val = val_div.get_text(strip=True)
            lbl = lbl_div.get_text(strip=True).lower()
            if "inscrit" in lbl or "candidat" in lbl:
                stats["candidats_inscrits"] = val
            elif "centre" in lbl:
                stats["centres_examen"] = val
            elif "fili" in lbl:
                stats["filieres_count"] = val
            elif "taux" in lbl or "reussite" in lbl or "réussite" in lbl:
                stats["taux_reussite"] = val

    return {
        "status": "success",
        "statistics": stats,
    }


def get_bts_filieres(
    category: Optional[str] = "all",
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Récupère la liste officielle des filières et spécialités du BTS (Industrielles & Tertiaires).

    Args:
        category (str): 'all', 'industrielles' (ou '1'), ou 'tertiaires' (ou '2').

    Returns:
        dict: Dictionnaire regroupant les filières par catégorie.
    """
    http = session or Session()
    categories_to_fetch = []

    cat_clean = str(category).lower()
    if cat_clean in ["all", "tout"]:
        categories_to_fetch = [("1", "industrielles"), ("2", "tertiaires")]
    elif cat_clean in ["1", "industrielle", "industrielles", "indus"]:
        categories_to_fetch = [("1", "industrielles")]
    elif cat_clean in ["2", "tertiaire", "tertiaires", "tert"]:
        categories_to_fetch = [("2", "tertiaires")]
    else:
        categories_to_fetch = [("1", "industrielles"), ("2", "tertiaires")]

    result_data: Dict[str, list] = {"industrielles": [], "tertiaires": []}

    for cat_id, cat_name in categories_to_fetch:
        url = f"https://bts.mesrs-ci.net/filieres/cat/{cat_id}"
        try:
            res = http.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                },
                timeout=timeout,
            )
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            items = []
            for card in soup.find_all(class_=lambda c: c and any(k in str(c) for k in ["card", "item", "list-group-item"])):
                txt = card.get_text(" ", strip=True)
                if txt and not any(skip in txt.lower() for skip in ["résultats", "examen", "inscriptions", "actualités"]):
                    parts = txt.split(maxsplit=1)
                    sigle = parts[0] if parts else ""
                    libelle = parts[1] if len(parts) > 1 else ""
                    items.append({"sigle": sigle, "libelle": libelle})
            result_data[cat_name] = items
        except Exception:
            pass

    return {
        "status": "success",
        "industrielles": result_data["industrielles"],
        "tertiaires": result_data["tertiaires"],
        "total_count": len(result_data["industrielles"]) + len(result_data["tertiaires"]),
    }


def download_bts_convocation(
    matricule: str,
    output_dir: str = "downloads/bts-convoc",
    filename: Optional[str] = None,
    session: Optional[Session] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Télécharge la convocation officielle au BTS depuis le portail MESRS.
    """
    mat = str(matricule).strip()
    if not mat:
        return {"status": "error", "message": "Le matricule est requis."}

    http = session or Session()
    root_url = "https://bts.mesrs-ci.net"
    deep_page = f"{root_url}/convocation/candidat"

    try:
        res_cand = http.post(deep_page, data={"matricule": mat}, timeout=timeout)
        res_cand.raise_for_status()
        soup = BeautifulSoup(res_cand.content, "html.parser")
        id_inp = soup.find("input", attrs={"name": "id"})
        if not id_inp or not id_inp.get("value"):
            return {"status": "not_found", "message": "Candidat non trouvé pour le retrait de convocation."}

        student_id = id_inp["value"]
        pdf_res = http.post(f"{root_url}/convocation.pdf", data={"id": student_id}, timeout=timeout)
        pdf_res.raise_for_status()

        if not pdf_res.content.startswith(b"%PDF"):
            return {"status": "error", "message": "Le document renvoyé n'est pas un fichier PDF valide."}

        import os
        os.makedirs(output_dir, exist_ok=True)
        out_name = filename or f"convocation_bts_{mat}.pdf"
        if not out_name.lower().endswith(".pdf"):
            out_name += ".pdf"
        file_path = os.path.join(output_dir, out_name)

        with open(file_path, "wb") as f:
            f.write(pdf_res.content)

        return {
            "status": "success",
            "matricule": mat,
            "file_path": os.path.abspath(file_path),
            "file_size": len(pdf_res.content),
            "filename": out_name,
        }
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors du téléchargement de la convocation BTS : {e}"}
