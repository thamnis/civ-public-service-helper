
# 🇨🇮 Civ Public Service Helper

Un outil Python pour interagir avec les services en ligne d'examens en Côte d'Ivoire (prochainement un spectre plus large) : récupération de convocations, consultation de résultats, et extraction d'informations à partir de fichiers PDF.

---

## 📚 Fonctionnalités principales

- 📥 Télécharger la **convocation** (BAC, BEPC, BTS, ...) depuis les plateformes officielles ivoiriennes.
- 📊 Extraire les **informations** importantes depuis le fichier PDF (dates d’épreuves, origine du candidat, établissement, etc.).
- 🧾 Consulter les **résultats** en ligne à partir du **matricule**.
- 📁 Gérer automatiquement les fichiers PDF localement.

---

## 🧑‍💻 Technologies utilisées

- `requests` — pour les requêtes HTTP.
- `BeautifulSoup` — pour parser le HTML.
- `pypdf` — pour lire les fichiers PDF.
- `typing` — pour sécuriser les types (`Literal`).
- `os` — pour manipuler les chemins de fichiers.

---

## ⚙️ Installation

1. Clone le repo :
```bash
git clone https://github.com/thamnis/civ-public-service-helper.git
cd civ-public-service-helper
```

2. Crée un environnement virtuel :
```bash
python -m venv .env
source .env/bin/activate  # ou .env\Scripts\activate sur Windows
```

3. Installe les dépendances :
```bash
pip install -r requirements.txt
```

> 📝 Si `requirements.txt` est manquant, installe manuellement :
```bash
pip install requests beautifulsoup4 pypdf
```

---

## 🚀 Utilisation

### Exemple : Télécharger une convocation d'examen scolaire
```python
from getters import get_school_document
get_school_document("12345678A", type="fco")  # type: 'fp', 'fi', 'fco'
```

### Exemple : Consulter un résultat
```python
from getters import get_result
result = get_result("12345678A", exam="bac")
print(result)
```

### Exemple : Lire des infos dans un PDF
```python
from getters import get_infos
infos = get_infos("downloaded/fco/fco_12345678A.pdf")
print(infos)
```

---

## 🧪 Fonctions disponibles

| Fonction | Description |
|---------|-------------|
| `get_school_document(id, type)` | Télécharge la convocation BAC/BEPC. |
| `get_result(matricule, exam)` | Récupère le résultat d'examen (BAC ou BEPC). |
| `get_bts_convoc(matricule)` | Télécharge la convocation BTS (fonction expérimentale). |
| `get_infos(pdf_path)` | Extrait les données essentielles depuis une convocation PDF. |
| `get_pdf_path(sid, type)` | Génère le chemin local vers un PDF téléchargé. |
| `get_location(id)` | *(à implémenter)* |

---

## 🛡️ Avertissement

Ce projet interagit avec des sites web gouvernementaux ivoiriens. Il est conseillé de l'utiliser **de manière responsable** et uniquement à des fins **personnelles ou éducatives**.

---

## 📄 Licence

Ce projet est open-source sous licence **MIT**.
Voir le fichier [`LICENSE`](LICENSE) pour plus de détails.

---

## 👨‍💻 Auteur

[thamnis](https://github.com/thamnis)

---
