
# 🇨🇮 Civ Public Service Helper

Un outil Python pour interagir avec les services en ligne d'examens en Côte d'Ivoire (prochainement un spectre plus large) : récupération de convocations, consultation de résultats, et extraction d'informations à partir de fichiers PDF.

---

## 📚 Fonctionnalités principales

- 📥 Télécharger la **convocation** (BAC, BEPC, BTS, ...) depuis les plateformes officielles ivoiriennes.
- 📑 Télécharger les **documents scolaires SIGFNE / DESPS** (Reçus de préinscription, Fiches de cursus) (`agfne.sigfne.net`).
- 🏥 Récupérer et télécharger les **convocations aux concours INFAS** (`infas.ciconcours.com`).
- 🏫 Consulter et télécharger la **fiche d'affectation en sixième** (`affectation.mendob.ci`).
- 🎓 Consulter et télécharger la **fiche d'orientation en seconde** (`orientation.mendob.ci`).
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

### Exemple : Télécharger un document scolaire SIGFNE (Reçu préinscription, Cursus)
```python
from getters import download_sigfne_document

# Télécharger le reçu de préinscription (année 2026-2027)
res = download_sigfne_document("12345678A", doc_type="recu", annee="2627")
print(res)

# Télécharger la fiche de cursus scolaire
res_cursus = download_sigfne_document("12345678A", doc_type="cursus", annee="2526")
print(res_cursus)
```

### Exemple : Télécharger une convocation au concours INFAS
```python
from getters import get_infas_convocation, download_infas_convocation

# Consultation et téléchargement du PDF
res = get_infas_convocation("CD00000000", download_pdf=True)
print(res["full_name"])
print(res["sessions"])
print(res["pdf"]["file_path"])

# Ou téléchargement direct :
download_infas_convocation("CD00000000", output_dir="downloads/infas")
```

### Exemple : Consulter une affectation en sixième (DOB / mendob.ci)
```python
from getters import get_sixieme_affectation, download_sixieme_affectation

# Consultation et téléchargement direct du PDF
res = get_sixieme_affectation("12345678A", download_pdf=True)
print(res["student"]["full_name"])
print(res["school"]["school_name"])
print(res["pdf"]["file_path"])

# Ou téléchargement direct :
download_sixieme_affectation("12345678A", output_dir="downloads/affectation")
```

### Exemple : Consulter une orientation en seconde (DOB / mendob.ci)
```python
from getters import get_seconde_orientation, download_seconde_orientation

# Consultation et téléchargement direct du PDF
res = get_seconde_orientation("12345678A", download_pdf=True)
print(res["student"]["full_name"])
print(res["school"]["school_name"])
print(res["school"]["serie"])
print(res["pdf"]["file_path"])

# Ou téléchargement direct :
download_seconde_orientation("12345678A", output_dir="downloads/orientation")
```

### Exemple : Consulter un résultat (BAC, BEPC ou BTS)
```python
from getters import get_result, get_bts_result

# BAC ou BEPC
result_bac = get_result("12345678A", exam="bac")
print(result_bac)

# BTS (nécessite matricule ou numéro BTS + date de naissance)
result_bts = get_bts_result("DOJO010100001", birthdate="01/01/2000")
# Ou via get_result :
# result_bts = get_result("DOJO010100001", exam="bts", birthdate="2000-01-01")
print(result_bts)
```

### Exemple : Lire des infos dans un PDF
```python
from getters import get_infos
infos = get_infos("downloaded/fco/fco_12345678A.pdf")
print(infos)
```

---

## 📦 Modules & Sous-projets

Le projet est organisé en sous-modules spécialisés, chacun disposant de sa propre documentation et d'outils CLI dédiés :

| Sous-module | Plateforme / Service | Description & Documentation |
|---|---|---|
| [`mesrs_services/`](mesrs_services/) | `inscription.mesrs-ci.net` | Vérification de paiement étudiant, catalogue DEXCO et annonces officielles MESRS. Voir le [README du module](mesrs_services/README.md). |
| [`sigfne_documents/`](sigfne_documents/) | `agfne.sigfne.net` | Téléchargement des reçus de préinscription et fiches de cursus scolaire. Voir le [README du module](sigfne_documents/README.md). |
| [`seconde_orientation/`](seconde_orientation/) | `orientation.mendob.ci` | Scraping d'identité, établissement d'accueil, série et téléchargement de fiches PDF 2nde. Voir le [README du module](seconde_orientation/README.md). |
| [`sixieme_affectation/`](sixieme_affectation/) | `affectation.mendob.ci` | Scraping d'identité, d'établissement et téléchargement de fiches PDF 6ème. Voir le [README du module](sixieme_affectation/README.md). |
| [`infas_convocation/`](infas_convocation/) | `infas.ciconcours.com` | Scraping des épreuves, centres et téléchargement des convocations INFAS. Voir le [README du module](infas_convocation/README.md). |
| [`bts_result/`](bts_result/) | `bts.mesrs-ci.net` | Résultats BTS, calendrier officiel, statistiques nationales, filières et convocation. Voir le [README du module](bts_result/README.md). |
| [`after_bac_orientation/`](after_bac_orientation/) | `bac.mesrs-ci.net` | Extraction et classement des filières et universités post-BAC. Voir le [README du module](after_bac_orientation/README.md). |

---

## 🧪 Fonctions disponibles

| Fonction | Description |
|---------|-------------|
| `get_school_document(id, type)` | Télécharge la convocation BAC/BEPC. |
| `verify_mesrs_payment(matricule, code, num)` | Vérifie la validité d'un paiement d'inscription MESRS (`inscription.mesrs-ci.net`). |
| `get_mesrs_dexco_services()` | Récupère le catalogue des actes d'examen et diplômes DEXCO. |
| `get_mesrs_announcements()` | Récupère les actualités et annonces flash officielles du MESRS. |
| `get_sigfne_document(matricule, doc_type, annee)` | Télécharge un reçu de préinscription ou fiche de cursus (`agfne.sigfne.net`). |
| `download_sigfne_document(matricule, doc_type, annee)` | Télécharge un document officiel SIGFNE / DESPS au format PDF. |
| `get_infas_convocation(candidate_id, download_pdf)` | Récupère la convocation INFAS et télécharge le PDF optionnel. |
| `download_infas_convocation(candidate_id)` | Télécharge la convocation PDF au concours INFAS (`infas.ciconcours.com`). |
| `get_sixieme_affectation(matricule, download_pdf)` | Récupère l'affectation en sixième et télécharge le PDF optionnel. |
| `download_sixieme_affectation(matricule)` | Télécharge la fiche PDF d'affectation en 6ème (`affectation.mendob.ci`). |
| `get_seconde_orientation(matricule, download_pdf)` | Récupère l'orientation en seconde et télécharge le PDF optionnel. |
| `download_seconde_orientation(matricule)` | Télécharge la fiche PDF d'orientation en seconde (`orientation.mendob.ci`). |
| `get_result(matricule, exam, birthdate)` | Récupère le résultat d'examen (BAC, BEPC, BTS, sixième, ou seconde). |
| `get_bts_result(matricule, birthdate)` | Récupère et structure le résultat d'un candidat au BTS. |
| `get_bts_calendar()` | Récupère le calendrier officiel et les dates clés de la session BTS. |
| `get_bts_statistics()` | Récupère les statistiques nationales de la session BTS (taux de réussite, inscrits, centres). |
| `get_bts_filieres(category)` | Récupère la liste des 33 filières industrielles et tertiaires du BTS. |
| `get_bts_convoc(matricule)` | Télécharge la convocation BTS. |
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
