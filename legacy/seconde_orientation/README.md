# 🇨🇮 Scraper & Téléchargeur d'Orientation en Seconde (`orientation.mendob.ci`)

Ce sous-module permet d'interroger la plateforme officielle d'orientation en classe de seconde de la **Direction de l'Orientation et des Bourses (DOB)** du Ministère de l'Éducation Nationale et de l'Alphabétisation de Côte d'Ivoire ([https://orientation.mendob.ci](https://orientation.mendob.ci)) afin de :

- 🔍 Consulter l'**identité de l'élève** (nom, prénoms, date de naissance, TGP, Moyenne MSNO) à partir de son **matricule**.
- 🏫 Récupérer les détails de son **établissement d'accueil en seconde** (nom du lycée, série d'orientation, quartier, type public/privé, frais additionnels, places).
- 📥 Télécharger automatiquement la **fiche officielle d'orientation en format PDF**.
- ⚡ Supporter les requêtes unitaires et par lot (batch) avec export des résultats au format JSON.

---

## 📁 Structure du module

```text
seconde_orientation/
├── scraper.py         # Logique d'interrogation API AJAX & téléchargement PDF
├── main.py            # CLI unitaire & batch avec export JSON
├── data.json          # Fichier de données d'exemple pour batch
├── test_scraper.py    # Suite de tests unitaires et mocks
└── README.md          # Documentation détaillée
```

---

## 🚀 Utilisation en ligne de commande (CLI)

### 1. Consulter l'orientation d'un élève par son matricule
```bash
python seconde_orientation/main.py --id 12345678A
```

### 2. Consulter et télécharger la fiche PDF d'orientation
```bash
python seconde_orientation/main.py --id 12345678A --download --output-dir downloads/orientation
```

### 3. Exécuter un traitement par lot à partir d'un fichier JSON
```bash
python seconde_orientation/main.py --file seconde_orientation/data.json --download --save-json results.json
```

---

## 🐍 Utilisation en Python

### Exemple 1 : Consultation rapide & téléchargement PDF
```python
from seconde_orientation.scraper import get_seconde_orientation

# Récupérer l'orientation et télécharger le PDF
result = get_seconde_orientation("12345678A", download_pdf=True)

if result["status"] == "success":
    print("Statut orientation :", result["is_oriented"])
    print("Élève :", result["student"]["full_name"])
    if result["school"]:
        print("Lycée :", result["school"]["school_name"])
        print("Série :", result["school"]["serie"])
    if result.get("pdf"):
        print("Chemin PDF :", result["pdf"]["file_path"])
else:
    print("Résultat :", result["message"])
```

### Exemple 2 : Télécharger directement le document PDF
```python
from seconde_orientation.scraper import download_orientation_document

doc = download_orientation_document("12345678A", output_dir="downloads/orientation")
if doc["status"] == "success":
    print(f"PDF téléchargé : {doc['file_path']} ({doc['file_size']} octets)")
```

---

## 📊 Format des données retournées (Exemple fictif)

```json
{
  "status": "success",
  "is_oriented": true,
  "student_code": "12345678A",
  "student": {
    "status": "success",
    "id": "200001",
    "student_code": "12345678A",
    "first_name": "JANE",
    "last_name": "DOE",
    "full_name": "DOE JANE",
    "birthday": "01/01/2011",
    "age": "15",
    "gender": "F",
    "nationality": "Ivoirienne",
    "tgp": "140.50",
    "msno": "14.25"
  },
  "school": {
    "status": "success",
    "school_id": "501",
    "school_name": "LYCEE CLASSIQUE D'ABIDJAN",
    "serie": "2nde C",
    "quartier": "COCODY",
    "school_type": "Public",
    "school_cost": "0.00",
    "capacity": "300",
    "assigned_count": "280",
    "free_place": "20",
    "school_gender": "Mixte",
    "comment": ""
  },
  "pdf": {
    "status": "success",
    "file_path": "downloads/orientation/orientation_seconde_12345678A.pdf",
    "file_size": 112994,
    "filename": "orientation_seconde_12345678A.pdf"
  },
  "message": "Élève orienté(e) en seconde"
}
```

---

## 🧪 Tests

Pour exécuter les tests unitaires du module :
```bash
python -m unittest seconde_orientation/test_scraper.py -v
```
