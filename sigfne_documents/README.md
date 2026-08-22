# 🇨🇮 Téléchargeur de Documents Scolaires SIGFNE / DESPS (`agfne.sigfne.net`)

Ce sous-module permet d'interagir avec la plateforme officielle **SIGFNE / DESPS** (Direction de l'Encadrement des Établissements Privés / Système Intégré de Gestion des Flux et des Notes des Élèves) du Ministère de l'Éducation Nationale et de l'Alphabétisation de Côte d'Ivoire ([https://agfne.sigfne.net/vas/interface-edition-documents-sigfne/](https://agfne.sigfne.net/vas/interface-edition-documents-sigfne/)) afin de :

- 🧾 Télécharger les **reçus officiels de préinscription** en ligne au format PDF.
- 📑 Télécharger les **fiches de cursus scolaire** (format standard et new) au format PDF.
- 📅 Sélectionner l'**année scolaire** souhaitée (de 2019-2020 à 2026-2027).
- ⚡ Supporter les interrogations unitaires et par lot (batch) avec export JSON.

---

## 📁 Structure du module

```text
sigfne_documents/
├── scraper.py         # Logique d'interrogation et de téléchargement PDF
├── main.py            # CLI unitaire & batch avec export JSON
├── data.json          # Données de test / exemples
├── test_scraper.py    # Suite de tests unitaires mockés
└── README.md          # Documentation détaillée
```

---

## 📋 Types de documents disponibles

| Clé | Libellé |
|---|---|
| `recu` | Reçu de préinscription |
| `cursus` | Fiche Cursus Scolaire |
| `cursusnew` | Fiche Cursus Scolaire (New) |

---

## 📅 Années scolaires supportées

| Code | Année scolaire |
|---|---|
| `2627` | 2026 - 2027 *(par défaut)* |
| `2526` | 2025 - 2026 |
| `2425` | 2024 - 2025 |
| `2324` | 2023 - 2024 |
| `2223` | 2022 - 2023 |
| `2122` | 2021 - 2022 |
| `2021` | 2020 - 2021 |
| `1920` | 2019 - 2020 |

---

## 🚀 Utilisation en ligne de commande (CLI)

### 1. Télécharger un reçu de préinscription
```bash
python sigfne_documents/main.py --id 12345678A --type recu --annee 2627
```

### 2. Télécharger une fiche de cursus scolaire
```bash
python sigfne_documents/main.py --id 12345678A --type cursus --annee 2526 --output-dir downloads/sigfne
```

### 3. Exécuter un traitement par lot à partir d'un fichier JSON
```bash
python sigfne_documents/main.py --file sigfne_documents/data.json --save-json results.json
```

---

## 🐍 Utilisation en Python

### Exemple 1 : Téléchargement d'un reçu de préinscription
```python
from sigfne_documents.scraper import download_sigfne_document

res = download_sigfne_document("12345678A", doc_type="recu", annee="2627")

if res["status"] == "success":
    print("Document téléchargé :", res["file_path"])
    print("Taille :", res["file_size"], "octets")
else:
    print("Statut :", res["message"])
```

### Exemple 2 : Téléchargement d'une fiche de cursus
```python
from sigfne_documents.scraper import download_sigfne_document

res = download_sigfne_document("12345678A", doc_type="cursus", annee="2526")
print(res)
```

---

## 📊 Format des données retournées (Exemple fictif)

```json
{
  "status": "success",
  "matricule": "12345678A",
  "doc_type": "recu",
  "doc_label": "Reçu de préinscription",
  "annee": "2627",
  "annee_label": "2026 - 2027",
  "file_path": "downloads/sigfne/sigfne_recu_12345678A_2627.pdf",
  "file_size": 85420,
  "filename": "sigfne_recu_12345678A_2627.pdf"
}
```

---

## 🧪 Tests

Pour exécuter les tests unitaires du module :
```bash
python -m unittest sigfne_documents/test_scraper.py -v
```
