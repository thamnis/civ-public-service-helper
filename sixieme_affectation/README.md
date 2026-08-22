# 🇨🇮 Scraper & Téléchargeur d'Affectation en Sixième (`affectation.mendob.ci`)

Ce sous-module permet d'interroger la plateforme officielle de la **Direction de l'Orientation et des Bourses (DOB)** du Ministère de l'Éducation Nationale et de l'Alphabétisation de Côte d'Ivoire ([https://affectation.mendob.ci](https://affectation.mendob.ci)) afin de :

- 🔍 Consulter l'**identité complète de l'élève** (nom, prénoms, date de naissance, TGP, etc.) à partir de son **matricule**.
- 🏫 Récupérer les détails de son **établissement d'affectation** (nom de l'école, commune/quartier, type public/privé, frais additionnels, places).
- 📥 Télécharger automatiquement la **fiche officielle d'affectation en format PDF**.
- 📄 Parser et extraire le contenu textuel de la fiche PDF.
- ⚡ Traiter des listes d'élèves en mode unitaire ou par lot (batch).

---

## 📁 Structure du module

```text
sixieme_affectation/
├── scraper.py         # Logique d'interrogation API AJAX & téléchargement PDF
├── main.py            # CLI unitaire & batch avec export JSON
├── data.json          # Fichier de données d'exemple pour batch
├── test_scraper.py    # Suite de tests unitaires et mocks
└── README.md          # Documentation détaillée
```

---

## 🚀 Utilisation en ligne de commande (CLI)

### 1. Consulter un élève par son matricule
```bash
python sixieme_affectation/main.py --id 12345678A
```

### 2. Consulter et télécharger la fiche PDF d'affectation
```bash
python sixieme_affectation/main.py --id 12345678A --download --output-dir downloads/affectation
```

### 3. Exécuter un traitement par lot à partir d'un fichier JSON
```bash
python sixieme_affectation/main.py --file sixieme_affectation/data.json --download --save-json results.json
```

---

## 🐍 Utilisation en Python

### Exemple 1 : Consultation rapide & téléchargement PDF
```python
from sixieme_affectation.scraper import get_sixieme_affectation

# Récupérer l'affectation et télécharger le PDF
result = get_sixieme_affectation("12345678A", download_pdf=True)

print("Statut affectation :", result["is_assigned"])
print("Élève :", result["student"]["full_name"])
print("Établissement :", result["school"]["school_name"])
print("Frais :", result["school"]["school_cost"])
print("Chemin PDF :", result["pdf"]["file_path"])
```

### Exemple 2 : Télécharger directement le document PDF
```python
from sixieme_affectation.scraper import download_assignment_document

doc = download_assignment_document("12345678A", output_dir="downloads/affectation")
if doc["status"] == "success":
    print(f"PDF téléchargé : {doc['file_path']} ({doc['file_size']} octets)")
```

### Exemple 3 : Extraire les métadonnées d'un PDF déjà téléchargé
```python
from sixieme_affectation.scraper import extract_pdf_info

info = extract_pdf_info("downloads/affectation/affectation_12345678A.pdf")
print("Nom :", info.get("full_name"))
print("Établissement :", info.get("school_name"))
print("Date d'opération :", info.get("operation_date"))
```

---

## 📊 Format des données retournées (Exemple fictif)

```json
{
  "status": "success",
  "is_assigned": true,
  "student_code": "12345678A",
  "student": {
    "status": "success",
    "id": "100001",
    "student_code": "12345678A",
    "first_name": "JANE",
    "last_name": "DOE",
    "full_name": "DOE JANE",
    "birthday": "01/01/2014",
    "age": "12",
    "gender": "F",
    "nationality": "Ivoirienne",
    "tgp": "110.00"
  },
  "school": {
    "status": "success",
    "school_id": "101",
    "school_name": "LYCEE MODERNE D'EXEMPLE ABIDJAN",
    "quartier": "COCODY CENTRE",
    "school_type": "Public",
    "school_cost": "0.00",
    "capacity": "200",
    "assigned_count": "150",
    "free_place": "50",
    "school_gender": "Mixte",
    "comment": ""
  },
  "pdf": {
    "status": "success",
    "file_path": "downloads/affectation/affectation_12345678A.pdf",
    "file_size": 112994,
    "filename": "affectation_12345678A.pdf"
  },
  "message": "Élève affecté(e)"
}
```

---

## 🧪 Tests

Pour exécuter les tests unitaires du module :
```bash
python -m unittest sixieme_affectation/test_scraper.py -v
```
