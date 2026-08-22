# 🇨🇮 Civ Public Service Helper — Wiki Officiel

Bienvenue sur le Wiki officiel du projet **Civ Public Service Helper** !

**Civ Public Service Helper** est une boîte à outils Python modulaire, robuste et extensible conçue pour interagir avec les plateformes gouvernementales ivoiriennes (Ministère de l'Éducation Nationale et de l'Alphabétisation - MENA, Ministère de l'Enseignement Supérieur et de la Recherche Scientifique - MESRS, Direction des Examens et Concours - DECO / DEXCO, Direction de l'Orientation et des Bourses - DOB, et concours nationaux tels que l'INFAS).

---

## 🧭 Sommaire du Wiki

1. [🏠 Accueil & Vue d'ensemble](Home.md)
2. [🎓 Examens & Résultats](Examens-et-Resultats.md)
3. [🏫 Affectations & Orientations Scolaires](Affectations-et-Orientations.md)
4. [🏥 Concours & Convocations](Concours-et-Convocations.md)
5. [📑 Documents Scolaires & Services MESRS](Documents-et-Services-MESRS.md)
6. [🛡️ Confidentialité, Tests & Contribution](Contribution-et-Confidentialite.md)

---

## 🌐 Plateformes et Services supportés

| Domaine / Plateforme | Organisme | URL officielle | Sous-module |
|---|---|---|---|
| **Résultats & Services BTS** | MESRS / DEXCO | [bts.mesrs-ci.net](https://bts.mesrs-ci.net) | [`bts_result/`](../bts_result/README.md) |
| **Affectation en Sixième** | MENA / DOB | [affectation.mendob.ci](https://affectation.mendob.ci) | [`sixieme_affectation/`](../sixieme_affectation/README.md) |
| **Orientation en Seconde** | MENA / DOB | [orientation.mendob.ci](https://orientation.mendob.ci) | [`seconde_orientation/`](../seconde_orientation/README.md) |
| **Concours d'Entrée INFAS** | Ministère de la Santé / INFAS | [infas.ciconcours.com](https://infas.ciconcours.com) | [`infas_convocation/`](../infas_convocation/README.md) |
| **Documents Scolaires SIGFNE** | MENA / DESPS | [agfne.sigfne.net](https://agfne.sigfne.net) | [`sigfne_documents/`](../sigfne_documents/README.md) |
| **Portail & Inscriptions MESRS** | MESRS | [inscription.mesrs-ci.net](https://inscription.mesrs-ci.net) | [`mesrs_services/`](../mesrs_services/README.md) |
| **Orientation Post-BAC** | MESRS | [bac.mesrs-ci.net](https://bac.mesrs-ci.net) | [`after_bac_orientation/`](../after_bac_orientation/README.md) |
| **Résultats BAC & BEPC** | MENA / DECO | [itdeco.ci](https://itdeco.ci) | [`getters.py`](../getters.py) |

---

## 🚀 Démarrage Rapide

### 1. Installation
```bash
git clone https://github.com/thamnis/civ-public-service-helper.git
cd civ-public-service-helper

# Création et activation de l'environnement virtuel
python -m venv .venv
# Sur Windows :
.venv\Scripts\activate
# Sur Linux/macOS :
source .venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt
```

### 2. Exemple d'utilisation de l'API unifiée Python
```python
from getters import (
    get_result,
    get_sixieme_affectation,
    get_seconde_orientation,
    get_infas_convocation,
    download_sigfne_document,
    verify_mesrs_payment,
)

# 1. Consulter le résultat d'un candidat au BTS
bts = get_result("DOJO010100001", exam="bts", birthdate="01/01/2000")
print("BTS :", bts)

# 2. Récupérer et télécharger une fiche d'affectation en 6ème
sixieme = get_sixieme_affectation("12345678A", download_pdf=True)
print("6ème :", sixieme["student"]["full_name"], "->", sixieme["school"]["school_name"])

# 3. Télécharger une convocation INFAS
infas = get_infas_convocation("CD00000000", download_pdf=True)
print("INFAS :", infas["full_name"], "Table :", infas["table_number"])
```
