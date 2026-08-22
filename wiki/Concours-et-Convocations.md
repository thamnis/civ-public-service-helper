# 🏥 Concours & Convocations

Ce chapitre décrit les outils dédiés aux concours nationaux (notamment l'INFAS) et aux convocations d'examens scolaires et supérieurs.

---

## 1. Concours d'Entrée à l'INFAS (`infas.ciconcours.com`)

Le sous-module [`infas_convocation/`](../infas_convocation/README.md) automatise l'interrogation du portail officiel du concours de l'Institut National de Formation des Agents de Santé.

### Fonctionnalités
- 🔐 Gestion automatique du jeton de sécurité CSRF.
- 👤 Extraction de l'identité du candidat et du numéro de table.
- 🏛️ Récupération des salles, centres d'examen et sessions de composition.
- 📥 Téléchargement automatique de la convocation officielle en format PDF.

### Exemple Python
```python
from getters import get_infas_convocation, download_infas_convocation

# Récupération des infos et téléchargement PDF
res = get_infas_convocation("CD00000000", download_pdf=True)
if res["status"] == "success":
    print("Candidat :", res["full_name"])
    print("Table    :", res["table_number"])
    print("Sessions :", res["sessions"])
    print("PDF      :", res["pdf"]["file_path"])

# Téléchargement direct
download_infas_convocation("CD00000000", output_dir="downloads/infas")
```

### Utilisation CLI
```bash
# Consultation unitaire
python infas_convocation/main.py --id CD00000000 --download --output-dir downloads/infas

# Traitement par lot (batch)
python infas_convocation/main.py --file infas_convocation/data.json --save-json results.json
```

---

## 2. Convocations Scolaires BAC / BEPC (`men-deco.org`)

Le module racine permet de télécharger les fiches de convocation scolaires :
- `fco` : Formation Continue / Candidat Officiel
- `fp` : Formation Professionnelle / Libre
- `fi` : Formation Initiale

### Exemple Python
```python
from getters import get_school_document, get_infos

# Téléchargement
get_school_document("12345678A", type="fco")

# Extraction des informations depuis le PDF téléchargé
infos = get_infos("downloads/fco/fco_12345678A.pdf")
print("Centre :", infos["school"])
print("Dates  :", infos["dates"])
```

---

## 3. Convocations BTS (`bts.mesrs-ci.net`)

### Exemple Python
```python
from getters import get_bts_convoc

# Télécharge dans downloads/bts-convoc/convoc-{matricule}.pdf
get_bts_convoc("DOJO010100001")
```
