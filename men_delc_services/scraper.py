import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.men-delc.org"

def _fetch_soup(url, timeout=15):
    try:
        response = requests.get(url, verify=False, timeout=timeout)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        return None

def get_textes_officiels(timeout=15):
    """
    Récupère tous les textes officiels (Arrêtés, Circulaires, Décrets, etc.) depuis le site de la DELC.
    """
    url = f"{BASE_URL}/views/tous-les-textes-officiels/"
    soup = _fetch_soup(url, timeout=timeout)
    if not soup:
        return {"status": "error", "message": "Impossible de joindre le portail DELC."}

    textes = []
    # Most pdf links in MEN-DELC end with .pdf
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if ".pdf" in href.lower():
            title = link.get_text(strip=True)
            if not title:
                continue
            
            # handle relative URLs
            if href.startswith("/"):
                full_url = f"{BASE_URL}{href}"
            elif href.startswith("http"):
                full_url = href
            else:
                full_url = f"{BASE_URL}/{href}"
                
            textes.append({"titre": title, "url": full_url})
            
    return {"status": "success", "count": len(textes), "textes": textes}

def get_directory(url_path, timeout=15):
    url = f"{BASE_URL}{url_path}"
    soup = _fetch_soup(url, timeout=timeout)
    if not soup:
        return {"status": "error", "message": "Impossible de joindre le portail DELC."}

    results = []
    # Assuming directory entries are typically in tables or lists.
    # We will extract table rows.
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if cells:
                entry = {}
                for i, cell in enumerate(cells):
                    header = headers[i] if i < len(headers) else f"col_{i}"
                    entry[header] = cell.get_text(strip=True)
                results.append(entry)
                
    return {"status": "success", "count": len(results), "data": results}

def get_drena_directory(timeout=15):
    return get_directory("/views/repertoire-des-dren/", timeout)

def get_iepp_directory(timeout=15):
    return get_directory("/views/repertoire-des-inspections/", timeout)

def get_primaire_nominations(type_nomination="directeur", timeout=15):
    """
    Récupère les décisions de nomination au primaire.
    type_nomination: "directeur" ou "maitre_application"
    """
    if type_nomination == "directeur":
        url = f"{BASE_URL}/views/decision-portant-nomination-directeur/"
    elif type_nomination == "maitre_application":
        url = f"{BASE_URL}/views/decision-portant-nomination-maitre-application/"
    else:
        return {"status": "error", "message": "Type de nomination invalide."}
        
    soup = _fetch_soup(url, timeout=timeout)
    if not soup:
        return {"status": "error", "message": "Impossible de joindre le portail DELC."}

    decisions = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if ".pdf" in href.lower():
            title = link.get_text(strip=True)
            if title:
                full_url = href if href.startswith("http") else f"{BASE_URL}{href}" if href.startswith("/") else f"{BASE_URL}/{href}"
                decisions.append({"titre": title, "url": full_url})
                
    return {"status": "success", "count": len(decisions), "decisions": decisions}
