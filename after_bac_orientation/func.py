import re
from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup
from requests import get, post

def get_page(url):
    g = get(url)
    return BeautifulSoup(g.content, "html.parser").find("table")

import re
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

def clean_text(text):
    """Nettoie le texte : supprime \n, \r, et réduit les espaces multiples."""
    return re.sub(r'\s+', ' ', text.strip())

def extract_link_or_text_or_code(cell: BeautifulSoup):
    """Retourne l'URL si présente, sinon le texte propre."""
    link = cell.find('a')
    code_eta = cell.find("input", attrs={"name": "etablissement_id"})
    if link and link.has_attr('href'):
        return link['href'].strip()
    if code_eta:
        return code_eta.get("value")

    return clean_text(cell.get_text())

def table_to_csv_string(table_tag):
    """Convertit une balise <table> en CSV compact sous forme de string avec URLs quand disponibles."""
    if not table_tag:
        raise ValueError("❌ Aucun élément <table> fourni.")

    header_row = table_tag.find("tr")
    raw_headers = [clean_text(cell.get_text()) for cell in header_row.find_all(['th', 'td'])]
    headers = [h for h in raw_headers if h]

    rows = []
    for tr in table_tag.find_all("tr")[1:]:
        cells_raw = [extract_link_or_text_or_code(td) for td in tr.find_all(['td', 'th'])]
        row = [cells_raw[i] for i in range(len(cells_raw)) if i < len(raw_headers) and raw_headers[i]]
        rows.append(row)

    df = pd.DataFrame(rows, columns=headers)
    output = StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def get_sectors_and_infos(code_eta: str):
    p = post("https://bac.mesrs-ci.net/liste-filiere-etablissement", data={"etablissement_id": code_eta})
    soup = BeautifulSoup(p.content, "html.parser")
    box = soup.find("div", attrs={"class": "card shadow-lg p-4 animate__animated animate__fadeIn"})
    infos = box.find_all("p")
    data = {
        "sigle": infos[0].get_text(strip=True).split(':')[-1].strip(),
        "commune": infos[1].get_text(strip=True).split(':')[-1].strip(),
        "location": infos[2].get_text(strip=True).split(':')[-1].strip(),
        "phone": infos[3].get_text(strip=True).split(':')[-1].strip().split('/'),
        "email": infos[4].get_text(strip=True).split(':')[-1].strip(),
        "website": infos[5].get_text(strip=True).split(':')[-1].strip(),
        "subs-fee": infos[6].get_text(strip=True).split(':')[-1].strip(),
        "scho-amount": infos[7].get_text(strip=True).split(':')[-1].strip(),
    }
    sectors = table_to_csv_string(box.find("table"))
    infos_and_sectors = data, sectors
    return infos_and_sectors
