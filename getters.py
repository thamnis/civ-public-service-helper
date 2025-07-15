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
from typing import Literal
import pypdf, os


DOWNLOAD_DIR = 'downloaded' # À modifier si nécessaire.


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


def get_result(matricule: str, exam: Literal["bac", "bepc"]):
    """
    Récupère les résultats d'examen pour un candidat à partir du site de la DECO.

    Args:
        matricule (str): Matricule du candidat.
        exam (Literal["bac", "bepc"]): Type d'examen.

    Returns:
        dict or int: Un dictionnaire contenant les résultats, ou 404 si non trouvé.
    """
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
