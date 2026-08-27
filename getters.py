"""
getters.py

Ce module contient des fonctions pour récupérer des informations sur les sites
web officiels Ivoiriens (BAC, BEPC, BTS). Il permet de :

    - Télécharger des convocations (BAC, BEPC, BTS).
    - Récupérer les résultats d'examens.
    - Extraire des informations à partir de fichiers PDF de convocations.
    - Générer les chemins vers les fichiers PDF locaux.

Fonctions à ajouter :

    - Verification de l'existance et de l'intégrité d'un fichier avant de 
      télécharger et de remplacer un fichier.
    - La fonction de localisation des centre d'examen est toujours à écrire.
    - Ajouter dans get_infos() des informations sur le candiadat.

Auteur : Oskhane Boya Gueï (thamnis)
Projet : civ-public-service-helper (MIT License)
Date : Juillet 2025
"""

from requests import Session
from bs4 import BeautifulSoup
from typing import Literal, Optional
import pypdf, os


DOWNLOAD_DIR = 'downloads' # À modifier si nécessaire.


def get_school_document(id: str, type: Literal['fco', 'fp', 'fi'] = "fp") -> int:
    """
    Télécharge un document de convocation pour un candidat aux examens scolaires (BAC ou BEPC).

    Args:
        id (str): Identifiant unique du candidat.
        type (Literal['fco', 'fp', 'fi']): Type de document (par défaut "fp").
            - 'fco' : Fiche de convocation
            - 'fp' : Fiche de préinscription
            - 'fi' : Fiche d'inscriprtion

    Returns:
        int: 0 si succès, sinon code HTTP d'erreur.
    """
    if type not in ['fco', 'fp', 'fi', 'fc']:
        return "Please enter a valid type. ('fco' OR 'fp' OR 'fi')"
        
    conv_session = Session()
    url = f"http://agce.exam-deco.org/edit/fiche-candidature-bac-bepc/?codefiche={type}&codetype=of&codedm="

    try:
        buffer = conv_session.get(url+id, verify=False)
        if buffer.status_code == 200:
            filetype = buffer.headers["Content-Type"].split('/')[1]

            docs_dir = os.path.join(DOWNLOAD_DIR, type)
            os.makedirs(docs_dir, exist_ok=True)

            with open(os.path.join(docs_dir, f'{type}_{id}.{filetype}'), "wb") as f:
                f.write(buffer.content)
        else:
            print(f"Connection error : {buffer.status_code}")
            return buffer.status_code
    except requests.exceptions.SSLError as SSLe:
        raise SSLe

    return 0


def get_result(
    matricule: str,
    exam: Literal["bac", "bepc", "bts", "sixieme", "affectation_sixieme", "seconde", "orientation_seconde"],
    birthdate: Optional[str] = None,
    download_pdf: bool = False,
):
    """
    Récupère les résultats d'examen ou d'affectation pour un candidat (BAC, BEPC, BTS, 6ème ou 2nde).

    Args:
        matricule (str): Matricule du candidat (ou identifiant BTS pour le BTS).
        exam (Literal["bac", "bepc", "bts", "sixieme", "affectation_sixieme", "seconde", "orientation_seconde"]): Type d'examen ou service.
        birthdate (str, optional): Date de naissance requise pour l'examen BTS (ex: "2007-01-16" ou "16/01/2007").
        download_pdf (bool): Télécharger le PDF si applicable.

    Returns:
        dict or int: Un dictionnaire contenant les résultats, ou 404/code d'erreur si non trouvé.
    """
    if exam in ["sixieme", "affectation_sixieme"]:
        return get_sixieme_affectation(matricule, download_pdf=download_pdf)

    if exam in ["seconde", "orientation_seconde"]:
        return get_seconde_orientation(matricule, download_pdf=download_pdf)

    if exam == "bts":
        if not birthdate:
            raise ValueError("Le paramètre 'birthdate' est obligatoire pour consulter les résultats du BTS.")
        return get_bts_result(matricule, birthdate)

    RESULT_URL_INDEX = f"https://itdeco.ci/examens/resultat/{exam}/redis/index.php"
    RESULT_URL_DEST = f"https://itdeco.ci/examens/resultat/{exam}/redis/resultat.php"

    s = Session()
    g = s.get(RESULT_URL_INDEX)
    if g.status_code == 404:
        return 404

    csrf_token = BeautifulSoup(g.content, "html.parser").find("input", attrs={"name": "csrf_token"}).get("value")

    p = s.post(RESULT_URL_DEST, {"matricule": matricule, "csrf_token": csrf_token})

    soup = BeautifulSoup(p.content, "html.parser")

    status = soup.find("div").find("strong").get_text()

    info = soup.find_all("span", attrs={"class": "info-value"})
    
    lname = info[1].get_text()
    fname = info[2].get_text()
    mention = info[3].get_text()
    serie = info[4].get_text()
    pts = info[5].get_text()
    is_admit = None

    if status == "réfusé":
        is_admit = False
    elif status == "admis":
        is_admit = True

    return {
        "matricule": matricule,
        "lname": lname,
        "fname": fname,
        "mention": mention,
        "serie": serie,
        "pts": pts,
        "is_admit": is_admit
    }


def get_bts_result(matricule: str, birthdate: str, timeout: int = 15) -> dict:
    """
    Récupère les résultats du BTS à partir du site officiel du MESRS.

    Args:
        matricule (str): Matricule du candidat ou identifiant BTS (ex: "12345678A" ou "BTS2026000000").
        birthdate (str): Date de naissance du candidat (ex: "2000-01-01", "01/01/2000").
        timeout (int): Délai d'attente maximum en secondes.

    Returns:
        dict: Dictionnaire contenant le statut d'admission et les détails du candidat.
    """
    from bts_result.scraper import get_bts_result as _get_bts_result
    return _get_bts_result(matricule, birthdate, timeout=timeout)


def get_sixieme_affectation(
    matricule: str,
    download_pdf: bool = False,
    output_dir: str = os.path.join(DOWNLOAD_DIR, "affectation"),
    timeout: int = 15,
) -> dict:
    """
    Récupère les détails d'affectation en 6ème depuis la DOB (affectation.mendob.ci).

    Args:
        matricule (str): Matricule de l'élève (ex: "12345678A").
        download_pdf (bool): Télécharger automatiquement la fiche en PDF.
        output_dir (str): Dossier de sauvegarde pour le PDF.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Dictionnaire complet avec identité élève, établissement d'affectation et détails PDF.
    """
    from sixieme_affectation.scraper import get_sixieme_affectation as _get_sixieme_affectation
    return _get_sixieme_affectation(
        matricule,
        download_pdf=download_pdf,
        output_dir=output_dir,
        timeout=timeout,
    )


def download_sixieme_affectation(
    matricule: str,
    output_dir: str = os.path.join(DOWNLOAD_DIR, "affectation"),
    timeout: int = 15,
) -> dict:
    """
    Télécharge la fiche officielle d'affectation en 6ème (PDF) depuis affectation.mendob.ci.

    Args:
        matricule (str): Matricule de l'élève (ex: "12345678A").
        output_dir (str): Dossier de sauvegarde pour le PDF.
        timeout: Timeout en secondes.

    Returns:
        dict: Dictionnaire avec statut de téléchargement et chemin du fichier.
    """
    from sixieme_affectation.scraper import download_assignment_document as _download_doc
    return _download_doc(matricule, output_dir=output_dir, timeout=timeout)


def get_infas_convocation(
    candidate_id: str,
    download_pdf: bool = False,
    output_dir: str = os.path.join(DOWNLOAD_DIR, "infas"),
    timeout: int = 15,
) -> dict:
    """
    Récupère les informations de convocation pour le concours INFAS (https://infas.ciconcours.com).

    Args:
        candidate_id (str): Numéro de candidature (ex: "CD00000000" ou "CA00000000").
        download_pdf (bool): Télécharger automatiquement la convocation PDF.
        output_dir (str): Dossier de sauvegarde pour le PDF.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Informations de convocation et chemin du fichier PDF si téléchargé.
    """
    from infas_convocation.scraper import get_infas_convocation as _get_infas
    return _get_infas(candidate_id, download_pdf=download_pdf, output_dir=output_dir, timeout=timeout)


def download_infas_convocation(
    candidate_id: str,
    output_dir: str = os.path.join(DOWNLOAD_DIR, "infas"),
    timeout: int = 15,
) -> dict:
    """
    Télécharge la convocation PDF officielle pour le concours INFAS.

    Args:
        candidate_id (str): Numéro de candidature (ex: "CD00000000" ou "CA00000000").
        output_dir (str): Dossier de destination pour le PDF.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Statut du téléchargement et chemin local du PDF.
    """
    from infas_convocation.scraper import download_infas_convocation as _dl_infas
    return _dl_infas(candidate_id, output_dir=output_dir, timeout=timeout)


def get_seconde_orientation(
    matricule: str,
    download_pdf: bool = False,
    output_dir: str = os.path.join(DOWNLOAD_DIR, "orientation"),
    timeout: int = 15,
) -> dict:
    """
    Récupère les détails d'orientation en seconde depuis la DOB (orientation.mendob.ci).

    Args:
        matricule (str): Matricule de l'élève (ex: "12345678A").
        download_pdf (bool): Télécharger automatiquement la fiche en PDF.
        output_dir (str): Dossier de sauvegarde pour le PDF.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Dictionnaire complet avec identité élève, établissement d'accueil, série et détails PDF.
    """
    from seconde_orientation.scraper import get_seconde_orientation as _get_seconde
    return _get_seconde(
        matricule,
        download_pdf=download_pdf,
        output_dir=output_dir,
        timeout=timeout,
    )


def download_seconde_orientation(
    matricule: str,
    output_dir: str = os.path.join(DOWNLOAD_DIR, "orientation"),
    timeout: int = 15,
) -> dict:
    """
    Télécharge la fiche officielle d'orientation en seconde (PDF) depuis orientation.mendob.ci.

    Args:
        matricule (str): Matricule de l'élève (ex: "12345678A").
        output_dir (str): Dossier de sauvegarde pour le PDF.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Dictionnaire avec statut de téléchargement et chemin du fichier.
    """
    from seconde_orientation.scraper import download_orientation_document as _download_doc
    return _download_doc(matricule, output_dir=output_dir, timeout=timeout)


def _get_iframe_fallback_url(men_delc_path: str, timeout: int = 15) -> Optional[str]:
    """
    Extrait l'URL de secours (iframe) depuis le portail MEN-DELC.
    """
    import requests
    from bs4 import BeautifulSoup
    try:
        res = requests.get(f"https://www.men-delc.org{men_delc_path}", verify=False, timeout=timeout)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, "html.parser")
            iframe = soup.find("iframe")
            if iframe and "src" in iframe.attrs:
                return iframe["src"]
    except Exception:
        pass
    return None


def get_sigfne_document(
    matricule: str,
    doc_type: Literal["recu", "cursus", "cursusnew"] = "recu",
    annee: str = "2627",
    output_dir: str = os.path.join(DOWNLOAD_DIR, "sigfne"),
    timeout: int = 15,
) -> dict:
    """
    Télécharge un document officiel SIGFNE/DESPS (Reçu de préinscription ou Fiche cursus).

    Args:
        matricule (str): Matricule de l'élève (ex: "12345678A").
        doc_type (Literal["recu", "cursus", "cursusnew"]): Type de document ('recu', 'cursus', 'cursusnew').
        annee (str): Année scolaire (ex: "2627" pour 2026-2027, "2526", ...).
        output_dir (str): Dossier de destination du PDF.
        timeout (int): Timeout en secondes.

    Returns:
        dict: Statut et chemin vers le document PDF téléchargé.
    """
    from sigfne_documents.scraper import download_sigfne_document as _dl_sigfne
    
    res = _dl_sigfne(matricule, doc_type=doc_type, annee=annee, output_dir=output_dir, timeout=timeout)
    if res.get("status") == "error":
        # Tentative de fallback via iframe MEN-DELC
        men_delc_path = "/views/impression-document-secondaire/"
        if doc_type in ["recu"]: # Assuming primary is different but recu/cursus are generally secondary here
             pass # adjust logic if we know it's primary vs secondary based on annee/doc_type
        
        fallback_url = _get_iframe_fallback_url(men_delc_path, timeout=timeout)
        if fallback_url:
            res_fallback = _dl_sigfne(
                matricule, doc_type=doc_type, annee=annee, 
                output_dir=output_dir, timeout=timeout, url_override=fallback_url
            )
            if res_fallback.get("status") != "error":
                return res_fallback

    return res


def download_sigfne_document(
    matricule: str,
    doc_type: Literal["recu", "cursus", "cursusnew"] = "recu",
    annee: str = "2627",
    output_dir: str = os.path.join(DOWNLOAD_DIR, "sigfne"),
    timeout: int = 15,
) -> dict:
    """
    Alias pour télécharger un document officiel SIGFNE/DESPS (Reçu de préinscription ou Fiche cursus).
    """
    return get_sigfne_document(matricule, doc_type=doc_type, annee=annee, output_dir=output_dir, timeout=timeout)


def get_bts_convoc(matricule):
    """
    Télécharge la convocation BTS à partir du site officiel du MESRS.

    Args:
        matricule (str): Matricule du candidat.

    Returns:
        None
    """
    root_url = "https://bts.mesrs-ci.net/"
    deep_page = f"{root_url}/convocation/candidat"
    s = Session()
    g = s.post(deep_page, {"matricule": matricule})
    soup = BeautifulSoup(g.content, "html.parser")

    student_id = soup.find("input", attrs={"name": "id"}).get("value")

    pdf_request = s.post(f"{root_url}/convocation.pdf", {"id": student_id})

    bts_convoc_dir = os.path.join(DOWNLOAD_DIR, 'bts-convoc')
    os.makedirs(bts_convoc_dir, exist_ok=True)
    with open(os.path.join(bts_convoc_dir, f"convoc-{matricule}.pdf"), "wb") as f:
        f.write(pdf_request.content)


def get_bts_calendar() -> dict:
    """
    Récupère le calendrier officiel de la session BTS (étapes et dates clés).
    """
    from bts_result.scraper import get_bts_calendar as _get_cal
    return _get_cal()


def get_bts_statistics() -> dict:
    """
    Récupère les statistiques nationales de la session du BTS (taux de réussite, inscrits, centres).
    """
    from bts_result.scraper import get_bts_statistics as _get_stats
    return _get_stats()


def get_bts_filieres(category: str = "all") -> dict:
    """
    Récupère la liste des filières industrielles et tertiaires du BTS (https://bts.mesrs-ci.net).
    """
    from bts_result.scraper import get_bts_filieres as _get_fils
    return _get_fils(category=category)


def verify_mesrs_payment(
    matricule_mesrs: str,
    code_paiement: str,
    numero_paiement: str,
    timeout: int = 15,
) -> dict:
    """
    Vérifie la validité d'un paiement d'inscription / réinscription universitaire auprès du MESRS.

    Args:
        matricule_mesrs (str): Matricule MESRS (ex: "AAAB19920001").
        code_paiement (str): Référence ou code de paiement (ex: "1502168548958751").
        numero_paiement (str): Numéro de téléphone / paiement (ex: "0102030405").
        timeout (int): Timeout en secondes.

    Returns:
        dict: Résultat de la vérification (statut, validité, détails).
    """
    from mesrs_services.scraper import verify_mesrs_payment as _verify
    return _verify(matricule_mesrs, code_paiement, numero_paiement, timeout=timeout)


def get_mesrs_dexco_services() -> dict:
    """
    Récupère le catalogue des actes d'examen et diplômes disponibles via DEXCO (https://inscription.mesrs-ci.net/dexco).
    """
    from mesrs_services.scraper import get_mesrs_dexco_services as _dexco
    return _dexco()


def get_mesrs_announcements() -> dict:
    """
    Récupère les actualités et annonces flash officielles diffusées sur le portail MESRS.
    """
    from mesrs_services.scraper import get_mesrs_announcements as _news
    return _news()


def get_bac_orientation_concours() -> dict:
    """
    Récupère la liste des concours d'orientation spéciaux post-BAC (https://bac.mesrs-ci.net/orientation/concours).
    """
    from after_bac_orientation.scraper import get_bac_orientation_concours as _concours
    return _concours()


def get_bac_orientation_concours_admissibles(concours_id: str) -> dict:
    """
    Récupère la liste officielle des candidats admissibles classés par rang pour un concours post-BAC.
    """
    from after_bac_orientation.scraper import get_bac_orientation_concours_admissibles as _admissibles
    return _admissibles(concours_id)


def check_bac_orientation_payment(matricule: str) -> dict:
    """
    Vérifie le statut de paiement des frais d'orientation post-BAC d'un bachelier (https://bac.mesrs-ci.net).
    """
    from after_bac_orientation.scraper import check_bac_orientation_payment as _payment
    return _payment(matricule)


def simulate_bac_orientation(matricule: str) -> dict:
    """
    Simule les filières et affectations possibles pour un bachelier selon ses notes.
    """
    from after_bac_orientation.scraper import simulate_bac_orientation as _sim
    return _sim(matricule)


# ==============================================================================
# ONECI SERVICES (Office National de l'État Civil et de l'Identification)
# ==============================================================================

def check_cni_status(numero_demande: str, nom: str, date_naissance: str, titre: str = "CNI", recaptcha_token: str = "") -> dict:
    """
    Vérifie le statut de production d'une CNI ou CRC depuis statut.oneci.ci.
    """
    from oneci_services.scraper import check_cni_status as _status
    return _status(numero_demande, nom, date_naissance, titre, recaptcha_token)


def find_numero_demande(nom: str, prenoms: str, date_naissance: str, lieu_naissance: str, titre: str = "CNI", recaptcha_token: str = "") -> dict:
    """
    Recherche un numéro de demande ONECI perdu.
    """
    from oneci_services.scraper import find_numero_demande as _find
    return _find(nom, prenoms, date_naissance, lieu_naissance, titre, recaptcha_token)


# ==============================================================================
# DECO SERVICES (Examens Scolaires : BEPC / CEPE)
# ==============================================================================

def get_bepc_result(matricule: str) -> dict:
    """
    Consulte le résultat du BEPC.
    """
    from deco_services.scraper import get_bepc_result as _bepc
    return _bepc(matricule)

def get_cepe_result(matricule: str) -> dict:
    """
    Consulte le résultat du CEPE.
    """
    from deco_services.scraper import get_cepe_result as _cepe
    return _cepe(matricule)


# ==============================================================================
# CEI SERVICES (Commission Electorale Indépendante)
# ==============================================================================

def check_voter_status(numero_cni: str) -> dict:
    """
    Vérifie le statut d'un électeur sur la liste électorale.
    """
    from cei_services.scraper import check_voter_status as _voter
    return _voter(numero_cni)


# ==============================================================================
# MFP SERVICES (Ministère de la Fonction Publique)
# ==============================================================================

def get_concours_result(num_inscription: str) -> dict:
    """
    Vérifie le résultat d'un concours administratif.
    """
    from mfp_services.scraper import get_concours_result as _mfp
    return _mfp(num_inscription)


# ==============================================================================
# JUSTICE SERVICES (e-Justice / Casier Judiciaire)
# ==============================================================================

def check_demande_status_justice(numero_demande: str, session_cookie: str = "") -> dict:
    """
    Vérifie le statut d'une demande de casier judiciaire.
    """
    from justice_services.scraper import check_demande_status as _justice
    return _justice(numero_demande, session_cookie)


def get_bac_orientation_result(matricule: str) -> dict:
    """
    Consulte le résultat de l'orientation d'un bachelier depuis bac.mesrs-ci.net.
    """
    from after_bac_orientation.scraper import get_bac_orientation_result as _res
    return _res(matricule)


def download_bac_orientation_fiche(matricule: str, output_dir: str = os.path.join(DOWNLOAD_DIR, "orientation_bac")) -> dict:
    """
    Télécharge la fiche officielle d'orientation au format PDF.
    """
    from after_bac_orientation.scraper import download_bac_orientation_fiche as _dl
    return _dl(matricule, output_dir=output_dir)


def get_pdf_path(sid: str, type: Literal['fco', 'fp', 'fi']):
    """
    Renvoie le chemin d'accès à un fichier PDF déjà téléchargé.

    Args:
        sid (str): Identifiant du candidat.
        type (Literal['fco', 'fp', 'fi']): Type de formation.

    Returns:
        str: Chemin absolu vers le fichier PDF.
    """
    if type not in ['fco', 'fp', 'fi', 'fc']:
        raise "Please enter a valid type. ('fco' OR 'fp' OR 'fi')"
    down_dir_content = os.listdir(DOWNLOAD_DIR)
    if type in down_dir_content:
        docs = os.listdir(os.path.join(DOWNLOAD_DIR, type))
        if f'{type}_{sid}.pdf' in docs:
            return os.path.join(DOWNLOAD_DIR, type, f'{type}_{sid}.pdf')
        else:
            raise BaseException(f'{type}_{sid}.pdf not found.')
    else:
        raise BaseException(f'{DOWNLOAD_DIR}/{type}/ not found.')


def get_infos(pdf_path):
    """
    Extrait les informations utiles à partir d’un fichier PDF de convocation.

    Args:
        pdf_path (str): Chemin vers le fichier PDF.

    Returns:
        dict: Un dictionnaire contenant les informations extraites :
            - dates (dict)
            - origin (str)
            - table_number (str)
            - school (str)
            - city (str)
    """
    pdf = pypdf.PdfReader(pdf_path)

    content = pdf.pages[0].extract_text()
    splitt = content.split('\n')

    capital = splitt[splitt.index('CONVOCATION CANDIDAT')+1]

    dates = None
    origin = None

    if "BEPC" in capital:
        dates = {
            'anglais':  splitt[splitt.index('EPREUVE ORALE D’ANGLAIS')+1],
            'ecrits': splitt[splitt.index('EPREUVES ECRITES')+1]
        }
        origin = splitt[splitt.index('Origine candidat: ')+1]
    elif "BACCALAUREAT" in capital:
        dates = {
            'technique': splitt[splitt.index('Technique')+1],
            'artistique': splitt[splitt.index('Artistique')+1],
            'général': splitt[splitt.index('Général')+1],
            'ecrits': splitt[splitt.index('Baccalauréats')+1]
        }
        origin = splitt[splitt.index('Origine Candidat: ')+1]
    else:
        Raise("ERROR OCCURED WHILE READING PDF: Determining exam")

    centre_pre = splitt.index('est prié(e) de se présenter au centre ')

    # print(splitt)
    table_number = splitt[splitt.index('Numéro de Table: ')+1]
    school = splitt[centre_pre+1]
    city = splitt[centre_pre+2]

    if splitt[centre_pre+2] == "pour subir les épreuves qui s'y dérouleront.":
        city = school.split(' ')[-1]
        school = ' '.join(school.split(' ')[:-1])

    return {
        'dates': dates,
        'origin': origin,
        'table_number': table_number,
        'school': school,
        'city': city
    }


def get_location(id: str):
    """
    [À implémenter] Récupère la localisation d’un centre à partir de ID l'élève.

    Args:
        id (str): Identifiant de l'élève.

    Returns:
        None
    """
    pass


# -------------------------------------------------------------------------
# Nouveaux services: CAFOP et MEN-DELC
# -------------------------------------------------------------------------

def get_cafop_affectation(matricule: str, timeout: int = 15) -> dict:
    """
    Consulte l'affectation CAFOP d'un candidat à partir de son matricule.
    """
    from cafop_services.scraper import get_cafop_affectation as _cafop
    return _cafop(matricule, timeout=timeout)


def get_cafop_directors_directory(timeout: int = 15) -> dict:
    """
    Récupère l'annuaire des directeurs de CAFOP.
    """
    from cafop_services.scraper import get_cafop_directors_directory as _cafop_dir
    return _cafop_dir(timeout=timeout)


def get_textes_officiels(timeout: int = 15) -> dict:
    """
    Récupère tous les textes officiels (Arrêtés, Circulaires, etc.) depuis la DELC.
    """
    from men_delc_services.scraper import get_textes_officiels as _textes
    return _textes(timeout=timeout)


def get_drena_directory(timeout: int = 15) -> dict:
    """
    Récupère l'annuaire des DRENA depuis la DELC.
    """
    from men_delc_services.scraper import get_drena_directory as _drena
    return _drena(timeout=timeout)


def get_iepp_directory(timeout: int = 15) -> dict:
    """
    Récupère l'annuaire des IEPP depuis la DELC.
    """
    from men_delc_services.scraper import get_iepp_directory as _iepp
    return _iepp(timeout=timeout)


def get_primaire_nominations(type_nomination: Literal["directeur", "maitre_application"] = "directeur", timeout: int = 15) -> dict:
    """
    Récupère les décisions de nomination au primaire.
    """
    from men_delc_services.scraper import get_primaire_nominations as _primaire
    return _primaire(type_nomination, timeout=timeout)
