# 🇨🇮 Scraper & Outils d'Orientation Post-BAC (`bac.mesrs-ci.net`)

Ce sous-module permet d'interagir avec la plateforme officielle d'**Orientation des Bacheliers** du Ministère de l'Enseignement Supérieur et de la Recherche Scientifique de Côte d'Ivoire ([https://bac.mesrs-ci.net](https://bac.mesrs-ci.net)).

---

## 📚 Fonctionnalités

- 🏛️ **Concours d'orientation d'excellence** : Récupérer la liste des concours d'entrée aux grandes filières sélectives (Architecture, Urbanisme, Architecture d'Intérieur, ENSAU).
- 📋 **Listes des admissibles** : Télécharger et extraire la liste complète des candidats admis/admissibles par concours avec leur rang officiel.
- 💳 **Statut de paiement de l'orientation** : Vérifier si les frais d'orientation post-BAC d'un bachelier ont été réglés (`/info/paiement`).
- 🎯 **Simulateur d'orientation** : Estimer les chances d'affectation et filières universitaires accessibles selon les notes du BAC (`/resultat/simulateur`).
- 🏫 **Annuaire des filières par établissement** : Extraire les filières, coordonnées et frais d'inscription des universités et grandes écoles.
- ⚡ **Support CLI moderne**.

---

## 📁 Structure du module

```text
after_bac_orientation/
├── scraper.py         # Logique d'interrogation et scraping (concours, admissibles, paiements)
├── main.py            # CLI moderne (concours, admissibles, paiement, simulateur)
├── func.py            # Fonctions utilitaires d'extraction CSV pour établissements
├── data.json          # Fichier de données d'exemple avec valeurs factices
├── test_scraper.py    # Suite de tests unitaires mockés
└── README.md          # Documentation détaillée du module
```

---

## 🚀 Utilisation en ligne de commande (CLI)

### 1. Lister les concours d'orientation spéciaux
```bash
python after_bac_orientation/main.py --concours
```

### 2. Afficher la liste des admissibles à un concours
```bash
python after_bac_orientation/main.py --admissibles 20693
```

### 3. Vérifier le paiement d'un bachelier
```bash
python after_bac_orientation/main.py --payment 12345678A
```

### 4. Simuler l'orientation pour un bachelier
```bash
python after_bac_orientation/main.py --simulate 12345678A
```

---

## 🐍 Utilisation en Python

### Exemple 1 : Récupérer les concours et leurs admissibles
```python
from getters import get_bac_orientation_concours, get_bac_orientation_concours_admissibles

# 1. Lister les concours
concours = get_bac_orientation_concours()
for c in concours["concours"]:
    print(f"• [ID: {c['id']}] {c['title']}")

# 2. Récupérer les admis pour le concours 20693 (Architecture)
res = get_bac_orientation_concours_admissibles("20693")
print(f"Total admissibles : {res['count']}")
for cand in res["admissibles"][:5]:
    print(f"Rang {cand['rang']} : {cand['nom_prenoms']}")
```

### Exemple 2 : Vérification du paiement d'orientation BAC
```python
from getters import check_bac_orientation_payment

res = check_bac_orientation_payment("12345678A")
if res["status"] == "success" and res["is_paid"]:
    print("✅ Paiement de l'orientation confirmé !")
else:
    print("Statut :", res["message"])
```

---

## 📊 Format des données retournées (Exemple fictif)

```json
{
  "status": "success",
  "concours_id": "20693",
  "title": "LICENCE ARCHITECTURE",
  "count": 70,
  "admissibles": [
    {
      "rang": 1,
      "nom_prenoms": "DOE JANE"
    },
    {
      "rang": 2,
      "nom_prenoms": "DOE JOHN"
    }
  ]
}
```

---

## 🧪 Tests

Pour exécuter les tests unitaires du module :
```bash
python -m unittest after_bac_orientation/test_scraper.py -v
```
