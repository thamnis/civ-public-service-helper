import re
from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup
from requests import get


def get_page(url):
    g = get(url)
    return BeautifulSoup(g.content, "html.parser").find("table")

def clean_text(text):
    """Nettoie le texte : supprime \n, \r, et réduit les espaces multiples."""
    return re.sub(r'\s+', ' ', text.strip())

def table_to_csv_string(table_tag):
    """Convertit une balise <table> en CSV compact sous forme de string."""
    if not table_tag:
        raise ValueError("❌ Aucun élément <table> fourni.")

    header_row = table_tag.find("tr")
    raw_headers = [clean_text(cell.get_text()) for cell in header_row.find_all(['th', 'td'])]
    headers = [h for h in raw_headers if h]

    rows = []
    for tr in table_tag.find_all("tr")[1:]:
        cells_raw = [clean_text(td.get_text()) for td in tr.find_all(['td', 'th'])]
        row = [cells_raw[i] for i in range(len(cells_raw)) if i < len(raw_headers) and raw_headers[i]]
        rows.append(row)

    df = pd.DataFrame(rows, columns=headers)
    output = StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()