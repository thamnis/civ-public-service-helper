# 🇨🇮 Civ Public Service Helper — Documentation Wiki

Bienvenue sur le Wiki complet du projet **Civ Public Service Helper**.

---

## 📑 Table des Matières

1. [Vue d'ensemble & Architecture](#-vue-densemble--architecture)
2. [Plateformes et Services Supportés](#-plateformes-et-services-supportés)
3. [Installation & Démarrage Rapide](#-installation--démarrage-rapide)
4. [Module 1 : Résultats & Services BTS (`bts_result`)](#-module-1--résultats--services-bts-bts_result)
5. [Module 2 : Affectation en Sixième (`sixieme_affectation`)](#-module-2--affectation-en-sixième-sixieme_affectation)
6. [Module 3 : Orientation en Seconde (`seconde_orientation`)](#-module-3--orientation-en-seconde-seconde_orientation)
7. [Module 4 : Concours d'Entrée INFAS (`infas_convocation`)](#-module-4--concours-dentrée-infas-infas_convocation)
8. [Module 5 : Documents Scolaires SIGFNE (`sigfne_documents`)](#-module-5--documents-scolaires-sigfne-sigfne_documents)
9. [Module 6 : Portail & Services MESRS (`mesrs_services`)](#-module-6--portail--services-mesrs-mesrs_services)
10. [Module 7 : Orientation Post-BAC (`after_bac_orientation`)](#-module-7--orientation-post-bac-after_bac_orientation)
11. [Récapitulatif de l'API Python (`getters.py`)](#-récapitulatif-de-lapi-python-getterspy)
12. [Règles de Confidentialité & Contribution](#-règles-de-confidentialité--contribution)

---

## 🌟 Vue d'ensemble & Architecture

**Civ Public Service Helper** est une suite modulaire en Python conçue pour interagir avec les plateformes gouvernementales ivoiriennes.

```text
civ-public-service-helper/
├── api/                        # API REST FastAPI et routeurs
├── civ_helper/                 # SDK principal et CLI unifiée
├── docs/                       # Documentation additionnelle (Annuaire, etc.)
├── getters.py                  # Façade API Python unifiée de haut niveau
├── legacy/                     # Modules hérités pour la compatibilité (bts, infas, etc.)
├── wiki/                       # Pages Wiki modulaires
└── WIKI.md                     # Document Wiki consolidé
```

---

## 🌐 Plateformes et Services Supportés

| Service | Organisme | URL officielle | Sous-module |
|---|---|---|---|
| **Résultats & Services BTS** | MESRS / DEXCO | [bts.mesrs-ci.net](https://bts.mesrs-ci.net) | `legacy/bts_result/` |
| **Affectation en Sixième** | MENA / DOB | [affectation.mendob.ci](https://affectation.mendob.ci) | `legacy/sixieme_affectation/` |
| **Orientation en Seconde** | MENA / DOB | [orientation.mendob.ci](https://orientation.mendob.ci) | `legacy/seconde_orientation/` |
| **Concours d'Entrée INFAS** | Ministère de la Santé / INFAS | [infas.ciconcours.com](https://infas.ciconcours.com) | `legacy/infas_convocation/` |
| **Documents Scolaires SIGFNE** | MENA / DESPS | [agfne.sigfne.net](https://agfne.sigfne.net) | `legacy/sigfne_documents/` |
| **Portail & Inscriptions MESRS** | MESRS | [inscription.mesrs-ci.net](https://inscription.mesrs-ci.net) | `legacy/mesrs_services/` |
| **Orientation Post-BAC** | MESRS | [bac.mesrs-ci.net](https://bac.mesrs-ci.net) | `legacy/after_bac_orientation/` |
| **Résultats BAC & BEPC** | MENA / DECO | [itdeco.ci](https://itdeco.ci) | `getters.py` |
| **Examens Techniques SYGADEXC** | METFPA / DEXC | [dexc.ci](http://dexc.ci) | `wiki/Examens-et-Resultats.md` |
| **Bourses & Orientation METFPA** | METFPA / DOBMFP | [dobmfp.com](https://dobmfp.com) / [orientationfp.com](https://orientationfp.com) | `wiki/Affectations-et-Orientations.md` |
| **Concours Enseignants IPNETP** | IPNETP / METFPA | [ipnetp.ci](https://ipnetp.ci) / [sigec.ipnetp.cloud](https://sigec.ipnetp.cloud) | `wiki/Concours-et-Convocations.md` |

---

## 🚀 Installation & Démarrage Rapide

```bash
# 1. Cloner le dépôt
git clone https://github.com/thamnis/civ-public-service-helper.git
cd civ-public-service-helper

# 2. Créer l'environnement virtuel
python -m venv .venv
# Windows :
.venv\Scripts\activate
# Linux/macOS :
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## 🎓 Module 1 : Résultats & Services BTS (`bts_result`)

- **Plateforme** : [https://bts.mesrs-ci.net](https://bts.mesrs-ci.net)
- **Fonctionnalités** :
  - Consultation d'admissibilité par matricule et date de naissance.
  - Calendrier officiel de la session (épreuves, soutenances, délibérations).
  - Statistiques nationales (inscrits, centres, filières, taux de réussite).
  - Liste des 33 filières (23 industrielles et 10 tertiaires).
  - Téléchargement de convocation officielle.

### Exemple Python :
```python
from getters import get_bts_result, get_bts_calendar, get_bts_statistics, get_bts_filieres

# Candidat
candidat = get_bts_result("DOJO010100001", birthdate="01/01/2000")
print("Statut :", "ADMISSIBLE" if candidat["is_admitted"] else "REFUSÉ")

# Calendrier
cal = get_bts_calendar()
for ev in cal.get("events", []):
    print(f"• {ev['etape']} : {ev['periode']}")
```

### Exemple CLI :
```bash
python legacy/bts_result/main.py --id DOJO010100001 --birthdate 01/01/2000
python legacy/bts_result/main.py --calendar
python legacy/bts_result/main.py --stats
python legacy/bts_result/main.py --filieres
```

---

## 🏫 Module 2 : Affectation en Sixième (`sixieme_affectation`)

- **Plateforme** : [https://affectation.mendob.ci](https://affectation.mendob.ci)
- **Fonctionnalités** : Extraction identité élève, collège d'affectation (public/privé, DREN, IEFP), téléchargement automatique de la fiche PDF.

### Exemple Python :
```python
from getters import get_sixieme_affectation
res = get_sixieme_affectation("12345678A", download_pdf=True)
print("Élève :", res["student"]["full_name"], "Collège :", res["school"]["school_name"])
```

### Exemple CLI :
```bash
python legacy/sixieme_affectation/main.py --id 12345678A --download --output-dir downloads/affectation
```

---

## 🎒 Module 3 : Orientation en Seconde (`seconde_orientation`)

- **Plateforme** : [https://orientation.mendob.ci](https://orientation.mendob.ci)
- **Fonctionnalités** : TGP, Moyenne MSNO, Lycée d'affectation, série d'orientation (2nde C, 2nde A, etc.), quartier, téléchargement de la fiche PDF.

### Exemple Python :
```python
from getters import get_seconde_orientation
res = get_seconde_orientation("12345678A", download_pdf=True)
print("Lycée :", res["school"]["school_name"], "Série :", res["school"]["serie"])
```

### Exemple CLI :
```bash
python legacy/seconde_orientation/main.py --id 12345678A --download --output-dir downloads/orientation
```

---

## 🏥 Module 4 : Concours d'Entrée INFAS (`infas_convocation`)

- **Plateforme** : [https://infas.ciconcours.com](https://infas.ciconcours.com)
- **Fonctionnalités** : Gestion du token CSRF, identité candidat, numéro de table, salle, centre et sessions d'examen, téléchargement direct de la convocation PDF.

### Exemple Python :
```python
from getters import get_infas_convocation
res = get_infas_convocation("CD00000000", download_pdf=True)
print("Candidat :", res["full_name"], "Table :", res["table_number"])
```

### Exemple CLI :
```bash
python legacy/infas_convocation/main.py --id CD00000000 --download --output-dir downloads/infas
```

---

## 📑 Module 5 : Documents Scolaires SIGFNE (`sigfne_documents`)

- **Plateforme** : [https://agfne.sigfne.net](https://agfne.sigfne.net)
- **Fonctionnalités** : Téléchargement des reçus de préinscription (`recu`) et des fiches de cursus scolaire (`cursus`, `cursusnew`) pour les années 2019-2027.

### Exemple Python :
```python
from getters import download_sigfne_document
res = download_sigfne_document("12345678A", doc_type="recu", annee="2627")
print("PDF :", res["file_path"])
```

### Exemple CLI :
```bash
python legacy/sigfne_documents/main.py --id 12345678A --type recu --annee 2627
```

---

## 🏛️ Module 6 : Portail & Services MESRS (`mesrs_services`)

- **Plateforme** : [https://inscription.mesrs-ci.net](https://inscription.mesrs-ci.net)
- **Fonctionnalités** : Vérification de paiement d'inscription / réinscription universitaire, catalogue des actes d'examen DEXCO, annonces et tickers flash officiels.

### Exemple Python :
```python
from getters import verify_mesrs_payment, get_mesrs_dexco_services, get_mesrs_announcements

# Vérification paiement
pay = verify_mesrs_payment("AAAB19920001", "1502168548958751", "0102030405")
print("Paiement valide :", pay["is_valid"])

# Catalogue DEXCO
dexco = get_mesrs_dexco_services()
print("Actes disponibles :", dexco["count"])
```

### Exemple CLI :
```bash
python legacy/mesrs_services/main.py --matricule AAAB19920001 --code-paiement 1502168548958751 --numero-paiement 0102030405
python legacy/mesrs_services/main.py --dexco
python legacy/mesrs_services/main.py --announcements
```

---

## 🎯 Module 7 : Orientation Post-BAC (`after_bac_orientation`)

- **Plateforme** : [https://bac.mesrs-ci.net](https://bac.mesrs-ci.net)
- **Fonctionnalités** : Concours d'excellence (Architecture, Urbanisme, ENSAU, Bondoukou), listes des admissibles classés par rang, vérification de paiement post-BAC, simulateur d'affectation.

### Exemple Python :
```python
from getters import get_bac_orientation_concours, get_bac_orientation_concours_admissibles

concours = get_bac_orientation_concours()
admis = get_bac_orientation_concours_admissibles("20693")
for c in admis["admissibles"][:5]:
    print(f"Rang {c['rang']} : {c['nom_prenoms']}")
```

### Exemple CLI :
```bash
python legacy/after_bac_orientation/main.py --concours
python legacy/after_bac_orientation/main.py --admissibles 20693
python legacy/after_bac_orientation/main.py --payment 12345678A
```

---

## 📋 Récapitulatif de l'API Python (`getters.py`)

| Fonction | Description |
|---|---|
| `get_school_document(id, type)` | Télécharge la convocation BAC/BEPC (`fco`, `fp`, `fi`). |
| `get_result(matricule, exam, birthdate)` | Récupère le résultat d'examen (BAC, BEPC, BTS, sixième, seconde). |
| `get_bts_result(matricule, birthdate)` | Récupère et structure le résultat d'un candidat au BTS. |
| `get_bts_calendar()` | Récupère le calendrier officiel et les dates clés de la session BTS. |
| `get_bts_statistics()` | Récupère les statistiques nationales de la session BTS (taux de réussite, inscrits, centres). |
| `get_bts_filieres(category)` | Récupère la liste des 33 filières industrielles et tertiaires du BTS. |
| `get_bts_convoc(matricule)` | Télécharge la convocation BTS en format PDF. |
| `get_sixieme_affectation(matricule, download_pdf)` | Récupère l'affectation en 6ème et télécharge le PDF optionnel. |
| `download_sixieme_affectation(matricule)` | Télécharge la fiche PDF d'affectation en 6ème. |
| `get_seconde_orientation(matricule, download_pdf)` | Récupère l'orientation en 2nde et télécharge le PDF optionnel. |
| `download_seconde_orientation(matricule)` | Télécharge la fiche PDF d'orientation en seconde. |
| `get_infas_convocation(candidate_id, download_pdf)` | Récupère la convocation INFAS et télécharge le PDF optionnel. |
| `download_infas_convocation(candidate_id)` | Télécharge la convocation PDF au concours INFAS. |
| `get_sigfne_document(matricule, doc_type, annee)` | Télécharge un reçu de préinscription ou fiche de cursus SIGFNE. |
| `download_sigfne_document(matricule, doc_type, annee)` | Télécharge un document officiel SIGFNE au format PDF. |
| `verify_mesrs_payment(matricule, code, num)` | Vérifie la validité d'un paiement d'inscription universitaire MESRS. |
| `get_mesrs_dexco_services()` | Récupère le catalogue des actes d'examen et diplômes DEXCO. |
| `get_mesrs_announcements()` | Récupère les actualités et annonces flash officielles du MESRS. |
| `get_bac_orientation_concours()` | Récupère la liste des concours d'orientation spéciaux post-BAC. |
| `get_bac_orientation_concours_admissibles(concours_id)` | Récupère la liste classée des admissibles pour un concours post-BAC. |
| `check_bac_orientation_payment(matricule)` | Vérifie le statut de paiement des frais d'orientation post-BAC. |
| `simulate_bac_orientation(matricule)` | Simule l'affectation et les filières accessibles pour un bachelier. |
| `get_infos(pdf_path)` | Extrait les données essentielles depuis une convocation PDF. |
| `get_pdf_path(sid, type)` | Génère le chemin local vers un PDF téléchargé. |

---

## 🛡️ Règles de Confidentialité & Contribution

### Règle d'or : Zéro donnée personnelle
- Ne commitez **jamais** de données personnelles réelles (noms réels, matricules réels, numéros de téléphone réels ou références de paiement privées).
- Utilisez toujours des données factices : `12345678A`, `CD00000000`, `DOJO010100001`, `AAAB19920001`.

### Tests unitaires
Exécutez la suite complète de 72 tests unitaires avant tout commit :
```bash
python -m unittest legacy/after_bac_orientation/test_scraper.py legacy/mesrs_services/test_scraper.py legacy/bts_result/test_scraper.py legacy/sigfne_documents/test_scraper.py legacy/seconde_orientation/test_scraper.py legacy/infas_convocation/test_scraper.py legacy/sixieme_affectation/test_scraper.py -v
```
