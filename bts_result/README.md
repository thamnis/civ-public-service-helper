# 🇨🇮 Scraper & Utilitaires BTS (`bts.mesrs-ci.net`)

Ce sous-module permet d'interagir avec l'ensemble des services officiels du **Brevet de Technicien Supérieur (BTS)** du Ministère de l'Enseignement Supérieur et de la Recherche Scientifique de Côte d'Ivoire ([https://bts.mesrs-ci.net](https://bts.mesrs-ci.net)).

---

## 📚 Fonctionnalités

- 🔍 **Résultats d'admissibilité** : Consulter le statut d'un candidat (Admissible / Non admissible), identité, filière et session.
- 📅 **Calendrier de la session** : Extraire les étapes officielles de la session (inscriptions, épreuves orales, écrites, soutenances, réclamations).
- 📊 **Statistiques nationales** : Récupérer le nombre de candidats inscrits, centres d'examen, filières et taux de réussite global.
- 📚 **Filières & Spécialités** : Lister l'ensemble des filières **Industrielles** (23 filières) et **Tertiaires** (10 filières).
- 📥 **Convocations** : Télécharger le fichier PDF officiel de convocation au BTS.
- 🔄 **Normalisation des dates** : Support de multiples formats de dates de naissance (`YYYY-MM-DD`, `DD/MM/YYYY`, `DD-MM-YYYY`, `DD.MM.YYYY`).
- ⚡ **CLI polyvalent** & requêtes par lot (batch).

---

## 📁 Structure du module

```text
bts_result/
├── scraper.py         # Logique de scraping (résultats, calendrier, stats, filières, convocation)
├── main.py            # CLI unitaire, informations et batch
├── data.json          # Fichier de configuration / liste de candidats factices
├── test_scraper.py    # Suite de tests unitaires mockés
└── README.md          # Documentation détaillée du module
```

---

## 🚀 Utilisation en ligne de commande (CLI)

### 1. Consulter le résultat d'un candidat
```bash
python bts_result/main.py --id DOJO010100001 --birthdate 01/01/2000
```

### 2. Afficher le calendrier officiel de la session
```bash
python bts_result/main.py --calendar
```

### 3. Afficher les statistiques nationales de la session
```bash
python bts_result/main.py --stats
```

### 4. Afficher la liste des filières industrielles et tertiaires
```bash
python bts_result/main.py --filieres
```

### 5. Télécharger la convocation d'un candidat
```bash
python bts_result/main.py --id DOJO010100001 --convocation --output-dir downloads/bts-convoc
```

### 6. Traitement par lot à partir d'un fichier JSON
```bash
python bts_result/main.py --file bts_result/data.json --save-json results.json
```

---

## 🐍 Utilisation en Python

### Exemple 1 : Consultation d'un résultat d'admissibilité
```python
from bts_result.scraper import get_bts_result

result = get_bts_result("DOJO010100001", birthdate="01/01/2000")

if result["status"] == "success":
    print("Statut :", "🎉 ADMISSIBLE" if result["is_admitted"] else "❌ NON ADMISSIBLE")
    print("Candidat :", result["full_name"])
    print("Filière :", result["sector"])
```

### Exemple 2 : Obtenir le calendrier et les statistiques
```python
from bts_result.scraper import get_bts_calendar, get_bts_statistics

# Calendrier
cal = get_bts_calendar()
for event in cal.get("events", []):
    print(f"• {event['etape']} : {event['periode']}")

# Statistiques nationales
stats = get_bts_statistics()
print(stats["statistics"])
```

### Exemple 3 : Lister les filières officielles
```python
from bts_result.scraper import get_bts_filieres

fils = get_bts_filieres(category="all")
print("Industrielles :", len(fils["industrielles"]))
print("Tertiaires :", len(fils["tertiaires"]))
```

---

## 📊 Format des données retournées (Exemple fictif)

```json
{
  "status": "success",
  "is_admitted": true,
  "decision": "admissible",
  "bts_id": "BTS2026000001",
  "student_id": "DOJO010100001",
  "full_name": "DOE JOHN",
  "last_name": "DOE",
  "first_name": "JOHN",
  "birthdate": "01/01/2000",
  "birthplace": "ABIDJAN",
  "sector": "IDA/INFORMATIQUE DEVELOPPEUR D'APPLICATIONS",
  "session": "2026",
  "message": "Vous avez été déclaré admissible au BTS session 2026"
}
```

---

## 🧪 Tests

Pour exécuter les tests unitaires du module :
```bash
python -m unittest bts_result/test_scraper.py -v
```
