# 🇨🇮 Module d'Orientation Post-BAC (`bac.mesrs-ci.net`)

Ce sous-module permet d'extraire, structurer et enrichir les informations d'orientation post-baccalauréat et de classement des établissements d'enseignement supérieur depuis le portail officiel du MESRS ([https://bac.mesrs-ci.net](https://bac.mesrs-ci.net)).

---

## 📚 Fonctionnalités

- 🏫 Extraction des classements officiels des universités privées, grandes écoles et filières BTS.
- 📋 Récupération des détails par établissement (sigle, commune, localisation, téléphones, email, site web, frais d'inscription, montants de bourse).
- 📑 Extraction automatique des tableaux de filières disponibles par établissement.
- 📊 Normalisation et export consolidé sous format CSV.

---

## 📁 Structure du module

```text
after_bac_orientation/
├── func.py     # Fonctions de scraping, parsing HTML et manipulation CSV
├── main.py     # Script d'exécution et génération des classements
└── README.md   # Documentation du sous-module
```

---

## 🌐 Pages et ressources ciblées

- [Portail d'orientation MESRS](https://bac.mesrs-ci.net/)
- [Classement BTS](https://bac.mesrs-ci.net/classement/bts2022)
- [Classement Grandes Écoles](https://bac.mesrs-ci.net/classement/grdes-ecoles)
- [Classement Universités Privées](https://bac.mesrs-ci.net/classement/univ-prive)
- [Guide d'orientation](https://bac.mesrs-ci.net/guide/orientation)
- [Offres des établissements privés](https://bac.mesrs-ci.net/offres/ets-prives)

---

## 🚀 Utilisation en ligne de commande (CLI)

Pour lancer le pipeline d'extraction et de fusion des classements :
```bash
python after_bac_orientation/main.py
```

---

## 🐍 Utilisation en Python

```python
from after_bac_orientation.func import get_sectors_and_infos

# Récupérer les filières et coordonnées d'un établissement via son code
infos, sectors_csv = get_sectors_and_infos("CODE_ETABLISSEMENT")
print("Coordonnées :", infos)
print("Filières CSV :", sectors_csv)
```
