from requests import session
from bs4 import BeautifulSoup
from typing import Literal
import pypdf, os


DOWNLOAD_DIR = 'downloaded'


def get_school_document(id: str, type: Literal['fco', 'fp', 'fi'] = "fp") -> int:

    if type not in ['fco', 'fp', 'fi', 'fc']:
        return "Please enter a valid type. ('fco' OR 'fp' OR 'fi')"
        
    conv_session = session()
    url = f"http://agce.exam-deco.org/edit/fiche-candidature-bac-bepc/?codefiche={type}&codetype=of&codedm="

    try:
        buffer = conv_session.get(url+id, verify=False)
        if buffer.status_code == 200:
            filetype = buffer.headers["Content-Type"].split('/')[1]
            with open(f'{type}_{id}.{filetype}', "wb") as f:
                f.write(buffer.content)
        else:
            print(f"Connection error : {buffer.status_code}")
            return buffer.status_code
    except requests.exceptions.SSLError as SSLe:
        raise SSLe

    return 0


def get_result(matricule: str, exam: Literal["bac", "bepc"]):
    RESULT_URL_INDEX = f"https://itdeco.ci/examens/resultat/{exam}/redis/index.php"
    RESULT_URL_DEST = f"https://itdeco.ci/examens/resultat/{exam}/redis/resultat.php"

    s = session()
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
    root_url = "https://bts.mesrs-ci.net/"
    deep_page = f"{root_url}/candidat"
    s = session()
    g = s.post(url, {"matricule": matricule})
    soup = BeautifulSoup(g.content, "html.parser")

    student_id = soup.find("input", attrs={"name": "id"}).get("value")

    pdf_request = s.post(f"{root_url}/convocation.pdf", {"id": student_id})

    with open(f"convoc-{matricule}.pdf", "wb") as f:
        f.write(pdf_request.content)


def get_pdf_path(sid: str, type: Literal['fco', 'fp', 'fi']):
    if type not in ['fco', 'fp', 'fi', 'fc']:
        raise "Please enter a valid type. ('fco' OR 'fp' OR 'fi')"
    return os.path.join(DOWNLOAD_DIR, type, f'{type}_{sid}.pdf')


def get_infos(pdf_path):

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
    pass
