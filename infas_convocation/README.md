# 🇨🇮 Scraper & Téléchargeur de Convocations INFAS (`infas.ciconcours.com`)

Ce sous-module permet d'interroger le portail officiel des concours de l'**Institut National de Formation des Agents de Santé (INFAS)** de Côte d'Ivoire ([https://infas.ciconcours.com](https://infas.ciconcours.com)) afin de :

- 🔍 Récupérer les **informations du candidat** (Nom, Prénoms, Date et lieu de naissance, Pièce d'identité, Numéro de table, Photo).
- 🏥 Extraire les **détails des épreuves et sessions** (Intitulé du concours, Centre d'examen, Salle, Date, Horaires).
- 📥 Télécharger automatiquement la **convocation officielle en format PDF**.
- ⚡ Supporter les interrogations unitaires et par lot (batch) avec export JSON.

---

## 📁 Structure du module

```text
infas_convocation/
├── scraper.py         # Logique d'extraction HTML & téléchargement PDF
├── main.py            # CLI unitaire & batch avec export JSON
├── data.json          # Données de test / exemples
├── test_scraper.py    # Suite de tests unitaires mockés
└── README.md          # Documentation détaillée
```

---

## 🚀 Utilisation en ligne de commande (CLI)

### 1. Consulter les détails d'un candidat
```bash
python infas_convocation/main.py --id CD00000000
```

### 2. Consulter et télécharger la convocation PDF
```bash
python infas_convocation/main.py --id CD00000000 --download --output-dir downloads/infas
```

### 3. Traitement par lot à partir d'un fichier JSON
```bash
python infas_convocation/main.py --file infas_convocation/data.json --download --save-json results.json
```

---

## 🐍 Utilisation en Python

### Exemple 1 : Consultation et téléchargement
```python
from infas_convocation.scraper import get_infas_convocation

# Récupérer les détails et télécharger le PDF
res = get_infas_convocation("CD00000000", download_pdf=True)

if res["status"] == "success":
    print("Candidat :", res["full_name"])
    print("Numéro de table :", res["table_number"])
    print("Sessions :", res["sessions"])
    if res.get("pdf"):
        print("Chemin PDF :", res["pdf"]["file_path"])
```

### Exemple 2 : Télécharger directement la convocation PDF
```python
from infas_convocation.scraper import download_infas_convocation

doc = download_infas_convocation("CD00000000", output_dir="downloads/infas")
if doc["status"] == "success":
    print(f"PDF téléchargé : {doc['file_path']} ({doc['file_size']} octets)")
```

---

## 📊 Format des données retournées (Exemple fictif)

```json
{
  "status": "success",
  "candidate_id": "CD00000000",
  "table_number": "10000001",
  "full_name": "DOE JOHN",
  "birthdate": "01-01-2000",
  "birthplace": "ABIDJAN",
  "id_card": "CNI / C0000000000",
  "photo_url": "https://infas.ciconcours.com/storage/photos/CD00000000.jpg",
  "sessions": [
    {
      "concours": "INFIRMIERS ET INFIRMIERES",
      "centre": "LYCEE D'EXEMPLE ABIDJAN",
      "salle": "SALLE 01",
      "date": "20 Août 2026",
      "heure": "08:00:00 - 12:00:00"
    }
  ],
  "convocation_url": "https://infas.ciconcours.com/imprimerConvocation/10000001/CONVOCATION",
  "pdf": {
    "status": "success",
    "file_path": "downloads/infas/convocation_infas_CD00000000_10000001.pdf",
    "file_size": 77494,
    "filename": "convocation_infas_CD00000000_10000001.pdf"
  }
}
```

---

## 🧪 Tests

Pour exécuter les tests unitaires du module :
```bash
python -m unittest infas_convocation/test_scraper.py -v
```
