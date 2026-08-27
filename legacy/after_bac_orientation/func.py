import re
from io import StringIO
import pandas as pd
import csv
from bs4 import BeautifulSoup
from requests import get, post

def get_page(url):
    g = get(url)
    return BeautifulSoup(g.content, "html.parser").find("table")

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

def table_to_csv_string(table_tag) -> str:
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

def get_sectors_and_infos(code_eta: str) -> tuple[dict, str]:
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
    return data, sectors

def merge_infos_to_csv(csv_input, csv_output) -> None:
    # Opening previous csv file in reading mode
    with open(csv_input, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f)
        
        # Extracting the header
        header = next(csv_reader)

        # Extracting values
        input_rows = [row for row in csv_reader]
        
        # extendind header
        header.extend(['sigle', 'commune', 'location', 'phone', 'email', 'website', 'subs_fee', 'scho_amount', "sectors"])

        # Opening output file in write mode
        with open(csv_output, "w", encoding="utf-8") as f:
            csv_writer = csv.writer(f)
            # Writing header in the output file
            csv_writer.writerow(header)
            
            # Writing values in the output file
            for row in input_rows:
                supplement = get_sectors_and_infos(row[-1])
                row.extend(list(supplement[0].values()))
                row.append(list(supplement[1].split("\n")))
                csv_writer.writerow(row)

def normalize_csv(csv_input) -> None:
    # Opening previous csv file in reading mode
    with open(csv_input, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f)
        
        # Extracting the header
        header = next(csv_reader)

        # Extracting values
        input_rows = [row for row in csv_reader]
        
        # Applying some normalization on the headers
        care_header = []
        for title in header.copy():
            title = title.lower().replace(' ', '_').replace('\'', '_')
            if title == "liste_des_filieres".lower():
                header[header.index("LISTE DES FILIERES")] = "code_eta"
            care_header.append(title)

    with open(csv_input, "w", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(care_header)
        csv_writer.writerows(input_rows)
