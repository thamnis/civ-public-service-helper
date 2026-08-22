# 🏫 Affectations & Orientations Scolaires

Ce chapitre décrit les outils d'extraction et de téléchargement pour les affectations en 6ème, orientations en 2nde et orientations post-BAC.

---

## 1. Affectation en Sixième (`affectation.mendob.ci`)

Le sous-module [`sixieme_affectation/`](../sixieme_affectation/README.md) permet d'interroger la Direction de l'Orientation et des Bourses (DOB).

### Fonctionnalités
- 🔍 Identité complète de l'élève (nom, prénoms, date de naissance, genre).
- 🏫 Établissement d'accueil (nom du collège, statut public/privé, DREN, IEFP, frais).
- 📥 Téléchargement automatique de la fiche officielle en format PDF.

### Exemple Python
```python
from getters import get_sixieme_affectation, download_sixieme_affectation

# Récupération des données et du PDF
res = get_sixieme_affectation("12345678A", download_pdf=True)
if res["status"] == "success":
    print("Élève :", res["student"]["full_name"])
    print("Collège :", res["school"]["school_name"])
    print("Fichier PDF :", res["pdf"]["file_path"])
```

### Utilisation CLI
```bash
python sixieme_affectation/main.py --id 12345678A --download --output-dir downloads/affectation
```

---

## 2. Orientation en Seconde (`orientation.mendob.ci`)

Le sous-module [`seconde_orientation/`](../seconde_orientation/README.md) permet de consulter les décisions d'orientation en 2nde de l'enseignement général et technique.

### Fonctionnalités
- 🔍 Scores de l'élève (Total Général Pondéré TGP, Moyenne MSNO).
- 🏫 Lycée d'accueil, série d'orientation (2nde C, 2nde A, etc.), quartier, type public/privé.
- 📥 Téléchargement de la fiche d'orientation en format PDF.

### Exemple Python
```python
from getters import get_seconde_orientation, download_seconde_orientation

res = get_seconde_orientation("12345678A", download_pdf=True)
if res["status"] == "success":
    print("Élève :", res["student"]["full_name"])
    print("Lycée :", res["school"]["school_name"])
    print("Série :", res["school"]["serie"])
    print("Fichier PDF :", res["pdf"]["file_path"])
```

### Utilisation CLI
```bash
python seconde_orientation/main.py --id 12345678A --download --output-dir downloads/orientation
```

---

## 3. Orientation Post-BAC (`bac.mesrs-ci.net`)

Le sous-module [`after_bac_orientation/`](../after_bac_orientation/README.md) interagit avec la plateforme d'orientation des bacheliers du MESRS.

### Fonctionnalités
- 🏛️ **Concours d'orientation d'excellence** : Architecture, Urbanisme, ENSAU, Université de Bondoukou.
- 📋 **Listes classées des candidats admissibles** avec rangs officiels.
- 💳 **Vérification de paiement d'orientation**.
- 🎯 **Simulateur d'orientation** par notes du BAC.

### Exemple Python
```python
from getters import get_bac_orientation_concours, get_bac_orientation_concours_admissibles, check_bac_orientation_payment

# Concours et admissibles
concours = get_bac_orientation_concours()
for c in concours["concours"]:
    print(f"Concours : {c['title']} (ID: {c['id']})")

admis = get_bac_orientation_concours_admissibles("20693")
for cand in admis["admissibles"][:5]:
    print(f"Rang {cand['rang']} : {cand['nom_prenoms']}")

# Vérification du paiement
pay = check_bac_orientation_payment("12345678A")
print("Paiement :", pay["is_paid"])
```

### Utilisation CLI
```bash
python after_bac_orientation/main.py --concours
python after_bac_orientation/main.py --admissibles 20693
python after_bac_orientation/main.py --payment 12345678A
```
